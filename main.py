"""
main.py - Điểm khởi chạy chính của Space Invaders.
Chứa Game Loop, xử lý va chạm, quản lý state (Menu/Playing/GameOver).
"""

import pygame
import sys
import os
import math
import array
import random as rnd

# Đảm bảo import từ thư mục gốc project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, DARK_BG,
    NEON_CYAN, NEON_RED, NEON_YELLOW, NEON_PINK, WHITE
)
from src.player import Player
from src.invader import Fleet
from src.laser import LaserGroup
from src.UI import (
    HUD, MenuScreen, GameOverScreen, WaveAnnouncer,
    Starfield, ExplosionManager
)


# ═══════════════════════════════════════════════════════════
#  GAME STATES
# ═══════════════════════════════════════════════════════════
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WAVE_TRANSITION = "wave_transition"


class Game:
    """Class chính quản lý toàn bộ trò chơi."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # State
        self.state = STATE_MENU
        self.running = True

        # Game objects
        self.player = Player()
        self.fleet = Fleet()
        self.player_lasers = LaserGroup()
        self.enemy_lasers = LaserGroup()

        # UI
        self.hud = HUD()
        self.menu_screen = MenuScreen()
        self.game_over_screen = GameOverScreen()
        self.wave_announcer = WaveAnnouncer()
        self.starfield = Starfield()
        self.explosions = ExplosionManager()

        # Game data
        self.score = 0
        self.wave = 1
        self.new_record = False

        # Wave transition
        self.wave_transition_timer = 0

        # Âm thanh (tạo programmatically vì không có file audio)
        self._init_sounds()

    def _init_sounds(self):
        """Tạo âm thanh bằng code (không cần file audio bên ngoài)."""
        self.sounds = {}
        try:
            # Tiếng laser - tần số cao ngắn
            sample_rate = 22050
            duration_laser = 0.08
            n_samples_laser = int(sample_rate * duration_laser)
            buf_laser = array.array('h', [0] * n_samples_laser)
            for i in range(n_samples_laser):
                t = i / sample_rate
                freq = 1200 - t * 8000  # Sweep xuống
                val = int(4000 * math.sin(2 * math.pi * freq * t))
                fade = 1.0 - (i / n_samples_laser)
                buf_laser[i] = int(val * fade)
            sound_laser = pygame.mixer.Sound(buffer=buf_laser)
            sound_laser.set_volume(0.15)
            self.sounds['laser'] = sound_laser

            # Tiếng nổ - noise burst
            duration_exp = 0.25
            n_samples_exp = int(sample_rate * duration_exp)
            buf_exp = array.array('h', [0] * n_samples_exp)
            for i in range(n_samples_exp):
                t = i / sample_rate
                fade = 1.0 - (i / n_samples_exp)
                noise = rnd.randint(-6000, 6000)
                low_freq = int(3000 * math.sin(2 * math.pi * 80 * t))
                buf_exp[i] = int((noise * 0.5 + low_freq * 0.5) * fade)
            sound_exp = pygame.mixer.Sound(buffer=buf_exp)
            sound_exp.set_volume(0.12)
            self.sounds['explode'] = sound_exp

            # Tiếng bị trúng đạn
            duration_hit = 0.15
            n_samples_hit = int(sample_rate * duration_hit)
            buf_hit = array.array('h', [0] * n_samples_hit)
            for i in range(n_samples_hit):
                t = i / sample_rate
                freq = 300 + math.sin(t * 40) * 200
                val = int(5000 * math.sin(2 * math.pi * freq * t))
                fade = 1.0 - (i / n_samples_hit)
                buf_hit[i] = int(val * fade)
            sound_hit = pygame.mixer.Sound(buffer=buf_hit)
            sound_hit.set_volume(0.15)
            self.sounds['hit'] = sound_hit

        except Exception:
            # Nếu không tạo được âm thanh, game vẫn chạy bình thường
            pass

    def play_sound(self, name):
        """Phát âm thanh an toàn."""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    # ───────────────────────────────────────────────────────
    #  RESET & NEW GAME
    # ───────────────────────────────────────────────────────

    def new_game(self):
        """Bắt đầu game mới."""
        self.score = 0
        self.wave = 1
        self.new_record = False
        self.player.reset()
        self.player_lasers.empty()
        self.enemy_lasers.empty()
        self.explosions = ExplosionManager()
        self.fleet.spawn_wave(self.wave)
        self.wave_announcer.announce(self.wave)
        self.state = STATE_PLAYING

    def next_wave(self):
        """Chuyển sang wave tiếp theo."""
        self.wave += 1
        self.player_lasers.empty()
        self.enemy_lasers.empty()
        self.fleet.spawn_wave(self.wave)
        self.wave_announcer.announce(self.wave)
        self.wave_transition_timer = 60  # Delay nhỏ trước khi quái bắn
        self.state = STATE_WAVE_TRANSITION

    # ───────────────────────────────────────────────────────
    #  EVENT HANDLING
    # ───────────────────────────────────────────────────────

    def handle_events(self):
        """Xử lý sự kiện bàn phím và chuột."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_MENU
                    else:
                        self.running = False

                if event.key == pygame.K_RETURN:
                    if self.state == STATE_MENU:
                        self.new_game()
                    elif self.state == STATE_GAME_OVER:
                        self.state = STATE_MENU

                if self.state == STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        if self.player.shoot(self.player_lasers):
                            self.play_sound('laser')

    # ───────────────────────────────────────────────────────
    #  UPDATE LOGIC
    # ───────────────────────────────────────────────────────

    def update_playing(self):
        """Cập nhật logic game khi đang chơi."""
        keys = pygame.key.get_pressed()

        # Cho phép bắn liên tục khi giữ SPACE
        if keys[pygame.K_SPACE]:
            if self.player.shoot(self.player_lasers):
                self.play_sound('laser')

        # Cập nhật các đối tượng
        self.player.update(keys)
        self.fleet.update(self.enemy_lasers)
        self.player_lasers.update()
        self.enemy_lasers.update()
        self.starfield.update()
        self.explosions.update()
        self.wave_announcer.update()

        # Dọn dẹp đạn ngoài màn hình (Garbage Collection)
        self.player_lasers.cleanup()
        self.enemy_lasers.cleanup()

        # ── VA CHẠM ────────────────────────────────────────

        # 1. Đạn người chơi vs Quái vật (groupcollide)
        hits = pygame.sprite.groupcollide(
            self.player_lasers, self.fleet.invaders,
            True, True  # Xóa cả đạn và quái
        )
        for laser, invaders_hit in hits.items():
            for inv in invaders_hit:
                self.score += inv.points
                self.explosions.create(
                    inv.rect.centerx, inv.rect.centery,
                    inv.color, 25
                )
                self.play_sound('explode')

        # 2. Đạn địch vs Người chơi
        if not self.player.invincible and self.player.alive:
            enemy_hits = pygame.sprite.spritecollide(
                self.player, self.enemy_lasers, True
            )
            if enemy_hits:
                died = self.player.take_damage()
                self.play_sound('hit')
                if died:
                    self.explosions.create(
                        self.player.rect.centerx, self.player.rect.centery,
                        NEON_CYAN, 40
                    )
                    self._game_over()

        # 3. Quái chạm đáy = thua
        if self.fleet.reached_bottom():
            self.player.alive = False
            self._game_over()

        # 4. Hết quái = sang wave mới
        if self.fleet.is_defeated():
            self.next_wave()

    def update_wave_transition(self):
        """Xử lý transition giữa các wave."""
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        if keys[pygame.K_SPACE]:
            if self.player.shoot(self.player_lasers):
                self.play_sound('laser')

        self.player_lasers.update()
        self.starfield.update()
        self.explosions.update()
        self.wave_announcer.update()
        self.player_lasers.cleanup()

        self.wave_transition_timer -= 1
        if self.wave_transition_timer <= 0:
            self.state = STATE_PLAYING

    def _game_over(self):
        """Chuyển sang trạng thái Game Over."""
        self.hud.save_highscore(self.score)
        self.new_record = (self.score >= self.hud.highscore and self.score > 0)
        self.game_over_screen.frame = 0
        self.state = STATE_GAME_OVER

    # ───────────────────────────────────────────────────────
    #  RENDER
    # ───────────────────────────────────────────────────────

    def render_playing(self):
        """Vẽ toàn bộ game lên màn hình."""
        self.screen.fill(DARK_BG)
        self.starfield.draw(self.screen)

        # Vẽ grid nền nhẹ
        self._draw_subtle_grid()

        # Vẽ các đối tượng game
        self.fleet.invaders.draw(self.screen)
        self.player_lasers.draw(self.screen)
        self.enemy_lasers.draw(self.screen)
        self.player.draw(self.screen)
        self.player.draw_health_bar(self.screen)
        self.explosions.draw(self.screen)

        # HUD
        self.hud.draw(self.screen, self.score, self.wave, self.player.hp)
        self.wave_announcer.draw(self.screen)

    def _draw_subtle_grid(self):
        """Vẽ grid nền mờ nhẹ kiểu cyberpunk."""
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, 80):
            pygame.draw.line(grid_surf, (15, 15, 40, 25), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 80):
            pygame.draw.line(grid_surf, (15, 15, 40, 25), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(grid_surf, (0, 0))

    # ───────────────────────────────────────────────────────
    #  MAIN LOOP
    # ───────────────────────────────────────────────────────

    def run(self):
        """Vòng lặp game chính."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()

            if self.state == STATE_MENU:
                self.menu_screen.draw(self.screen)

            elif self.state == STATE_PLAYING:
                self.update_playing()
                self.render_playing()

            elif self.state == STATE_WAVE_TRANSITION:
                self.update_wave_transition()
                self.render_playing()

            elif self.state == STATE_GAME_OVER:
                # Vẫn vẽ nền game phía sau
                self.starfield.update()
                self.explosions.update()
                self.screen.fill(DARK_BG)
                self.starfield.draw(self.screen)
                self._draw_subtle_grid()
                self.fleet.invaders.draw(self.screen)
                self.explosions.draw(self.screen)
                self.hud.draw(self.screen, self.score, self.wave, 0)
                # Overlay Game Over
                self.game_over_screen.draw(
                    self.screen, self.score,
                    self.hud.highscore, self.wave, self.new_record
                )

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    game = Game()
    game.run()

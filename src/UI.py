"""
UI.py - Xử lý vẽ điểm số, màn hình Menu, Game Over, nút bấm,
         Particle System cho vụ nổ, và Parallax Starfield background.
"""

import pygame
import random
import math
import os
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, WHITE, CYAN, NEON_CYAN, NEON_PINK, NEON_PURPLE,
    NEON_RED, NEON_YELLOW, NEON_GREEN, NEON_ORANGE,
    DARK_BG, DARK_BLUE, GRID_COLOR,
    PARTICLE_COUNT_EXPLOSION, PARTICLE_LIFETIME,
    STAR_LAYERS, STAR_COUNT_PER_LAYER,
    PLAYER_MAX_HP, HIGHSCORE_FILE
)


# ═══════════════════════════════════════════════════════════
#  PARTICLE SYSTEM - Hiệu ứng vụ nổ
# ═══════════════════════════════════════════════════════════

class Particle:
    """Một hạt pixel nhỏ trong vụ nổ."""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.lifetime = random.randint(15, PARTICLE_LIFETIME)
        self.max_life = self.lifetime
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        alpha = int(255 * self.lifetime / self.max_life)
        alpha = max(0, min(255, alpha))
        size = max(1, int(self.size * self.lifetime / self.max_life))
        ps = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(ps, c, (size, size), size)
        surface.blit(ps, (int(self.x) - size, int(self.y) - size))

    @property
    def alive(self):
        return self.lifetime > 0


class Explosion:
    """Một vụ nổ gồm nhiều hạt + flash sáng ban đầu."""

    def __init__(self, x, y, color, count=PARTICLE_COUNT_EXPLOSION):
        self.particles = []
        self.flash_timer = 6
        self.x = x
        self.y = y
        self.color = color

        for _ in range(count):
            self.particles.append(Particle(x, y, color))
        # Thêm vài hạt trắng sáng
        for _ in range(count // 3):
            self.particles.append(Particle(x, y, WHITE))

    def update(self):
        self.flash_timer -= 1
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        # Flash sáng ban đầu
        if self.flash_timer > 0:
            flash_size = self.flash_timer * 6
            fs = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            alpha = int(180 * self.flash_timer / 6)
            pygame.draw.circle(fs, (*self.color[:3], alpha),
                               (flash_size, flash_size), flash_size)
            pygame.draw.circle(fs, (*WHITE[:3], alpha // 2),
                               (flash_size, flash_size), flash_size // 2)
            surface.blit(fs, (int(self.x) - flash_size, int(self.y) - flash_size))

        for p in self.particles:
            p.draw(surface)

    @property
    def alive(self):
        return len(self.particles) > 0 or self.flash_timer > 0


class ExplosionManager:
    """Quản lý tất cả vụ nổ đang active."""

    def __init__(self):
        self.explosions = []

    def create(self, x, y, color, count=PARTICLE_COUNT_EXPLOSION):
        self.explosions.append(Explosion(x, y, color, count))

    def update(self):
        for exp in self.explosions:
            exp.update()
        self.explosions = [e for e in self.explosions if e.alive]

    def draw(self, surface):
        for exp in self.explosions:
            exp.draw(surface)


# ═══════════════════════════════════════════════════════════
#  PARALLAX STARFIELD - Nền trời sao
# ═══════════════════════════════════════════════════════════

class Star:
    """Một ngôi sao trong nền."""

    def __init__(self, layer):
        self.layer = layer
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        # Layer xa = chậm + nhỏ + mờ; Layer gần = nhanh + to + sáng
        self.speed = 0.2 + layer * 0.4
        self.size = 1 + layer
        self.base_alpha = 80 + layer * 60
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        self.color_choice = random.choice([
            (200, 200, 255),  # Xanh nhạt
            (255, 255, 255),  # Trắng
            (255, 220, 180),  # Vàng nhạt
            (180, 200, 255),  # Xanh dương
        ])

    def update(self, frame):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT + 5:
            self.y = -5
            self.x = random.randint(0, SCREEN_WIDTH)
        self.frame = frame

    def draw(self, surface):
        twinkle = math.sin(self.frame * self.twinkle_speed + self.twinkle_offset)
        alpha = int(self.base_alpha + twinkle * 40)
        alpha = max(30, min(255, alpha))
        size = max(1, self.size)

        if size <= 1:
            # Pixel đơn cho sao xa
            color = (*self.color_choice[:3],)
            surface.set_at((int(self.x), int(self.y)),
                           (color[0] * alpha // 255,
                            color[1] * alpha // 255,
                            color[2] * alpha // 255))
        else:
            ss = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ss, (*self.color_choice[:3], alpha),
                               (size, size), size)
            # Glow nhẹ
            if size >= 2:
                pygame.draw.circle(ss, (*self.color_choice[:3], alpha // 4),
                                   (size, size), size + 1)
            surface.blit(ss, (int(self.x) - size, int(self.y) - size))


class Starfield:
    """Hệ thống nền sao parallax nhiều tầng."""

    def __init__(self):
        self.stars = []
        for layer in range(STAR_LAYERS):
            for _ in range(STAR_COUNT_PER_LAYER):
                self.stars.append(Star(layer))
        self.frame = 0

    def update(self):
        self.frame += 1
        for star in self.stars:
            star.update(self.frame)

    def draw(self, surface):
        for star in self.stars:
            star.draw(surface)


# ═══════════════════════════════════════════════════════════
#  HUD - Hiển thị thông tin game
# ═══════════════════════════════════════════════════════════

class HUD:
    """Vẽ điểm số, wave, HP, highscore lên màn hình."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.highscore = self._load_highscore()
        self._init_fonts()

    def _init_fonts(self):
        """Khởi tạo font chữ."""
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Consolas", 42, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 18)

    def _load_highscore(self):
        """Đọc highscore từ file."""
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return 0

    def save_highscore(self, score):
        """Lưu highscore nếu đạt kỷ lục mới."""
        if score > self.highscore:
            self.highscore = score
            try:
                with open(HIGHSCORE_FILE, 'w') as f:
                    f.write(str(score))
            except IOError:
                pass

    def draw(self, surface, score, wave, hp):
        """Vẽ HUD lên trên cùng màn hình."""
        # Score
        score_text = self.font_medium.render(f"SCORE: {score:06d}", True, NEON_CYAN)
        surface.blit(score_text, (15, 8))

        # Highscore
        hi_text = self.font_small.render(f"HI: {self.highscore:06d}", True, NEON_PINK)
        surface.blit(hi_text, (15, 38))

        # Wave
        wave_text = self.font_medium.render(f"WAVE {wave}", True, NEON_YELLOW)
        wave_rect = wave_text.get_rect(centerx=SCREEN_WIDTH // 2, y=8)
        surface.blit(wave_text, wave_rect)

        # HP (hiển thị dạng icon)
        hp_label = self.font_small.render("HP:", True, NEON_GREEN)
        surface.blit(hp_label, (SCREEN_WIDTH - 180, 12))
        for i in range(PLAYER_MAX_HP):
            x = SCREEN_WIDTH - 140 + i * 24
            y = 12
            if i < hp:
                # Filled heart/shield
                pygame.draw.rect(surface, NEON_GREEN, (x, y, 18, 18), border_radius=3)
                pygame.draw.rect(surface, WHITE, (x, y, 18, 18), 1, border_radius=3)
            else:
                pygame.draw.rect(surface, (40, 40, 40), (x, y, 18, 18), border_radius=3)
                pygame.draw.rect(surface, (80, 80, 80), (x, y, 18, 18), 1, border_radius=3)

        # Đường phân cách
        pygame.draw.line(surface, (*NEON_CYAN[:3],), (0, 55), (SCREEN_WIDTH, 55), 1)


# ═══════════════════════════════════════════════════════════
#  MENU & GAME OVER SCREENS
# ═══════════════════════════════════════════════════════════

class MenuScreen:
    """Màn hình Menu chính."""

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas", 52, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 22)
        self.font_small = pygame.font.SysFont("Consolas", 16)
        self.frame = 0
        self.stars = Starfield()

    def draw(self, surface):
        self.frame += 1
        self.stars.update()

        # Nền
        surface.fill(DARK_BG)
        self.stars.draw(surface)

        # Grid nền cyberpunk
        self._draw_grid(surface)

        cy = SCREEN_HEIGHT // 2

        # Title glow
        title_text = "SPACE INVADERS"
        glow_intensity = int(abs(math.sin(self.frame * 0.03)) * 55) + 40
        glow_color = (0, min(255, glow_intensity + 150), min(255, glow_intensity + 160))
        title_surf = self.font_title.render(title_text, True, glow_color)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=cy - 140)
        surface.blit(title_surf, title_rect)

        # Subtitle
        sub_text = "N E O N   C Y B E R P U N K   E D I T I O N"
        sub_color_val = min(255, int(abs(math.sin(self.frame * 0.05)) * 100) + 155)
        sub_surf = self.font_sub.render(sub_text, True, (sub_color_val, 0, sub_color_val))
        sub_rect = sub_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=cy - 80)
        surface.blit(sub_surf, sub_rect)

        # Decorative line
        line_w = 300
        lx = SCREEN_WIDTH // 2 - line_w // 2
        pygame.draw.line(surface, NEON_CYAN, (lx, cy - 55), (lx + line_w, cy - 55), 2)

        # Instructions
        instructions = [
            ("[ARROW / A-D]  Di chuyen", NEON_CYAN),
            ("[SPACE]  Ban dan", NEON_YELLOW),
            ("[ESC]  Thoat game", NEON_RED),
        ]
        for i, (text, color) in enumerate(instructions):
            txt = self.font_sub.render(text, True, color)
            rect = txt.get_rect(centerx=SCREEN_WIDTH // 2, y=cy - 20 + i * 35)
            surface.blit(txt, rect)

        # Start prompt (nhấp nháy)
        if (self.frame // 30) % 2 == 0:
            start_text = ">>> PRESS [ENTER] TO START <<<"
            start_surf = self.font_sub.render(start_text, True, NEON_GREEN)
            start_rect = start_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=cy + 110)
            surface.blit(start_surf, start_rect)

        # Credits
        credit = self.font_small.render("Made with Python & Pygame", True, (80, 80, 120))
        cr = credit.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 15)
        surface.blit(credit, cr)

    def _draw_grid(self, surface):
        """Vẽ grid nền kiểu cyberpunk."""
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, 60):
            pygame.draw.line(grid_surf, (*GRID_COLOR, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 60):
            pygame.draw.line(grid_surf, (*GRID_COLOR, 40), (0, y), (SCREEN_WIDTH, y))
        surface.blit(grid_surf, (0, 0))


class GameOverScreen:
    """Màn hình Game Over."""

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas", 56, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 20)
        self.frame = 0

    def draw(self, surface, score, highscore, wave, new_record=False):
        self.frame += 1

        # Overlay tối
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cy = SCREEN_HEIGHT // 2

        # GAME OVER text (nhấp nháy đỏ)
        flash = abs(math.sin(self.frame * 0.08))
        r = int(200 + flash * 55)
        go_text = self.font_title.render("GAME OVER", True, (r, 30, 30))
        go_rect = go_text.get_rect(centerx=SCREEN_WIDTH // 2, y=cy - 120)
        surface.blit(go_text, go_rect)

        # Score
        score_text = self.font_medium.render(f"FINAL SCORE: {score:06d}", True, NEON_CYAN)
        sr = score_text.get_rect(centerx=SCREEN_WIDTH // 2, y=cy - 40)
        surface.blit(score_text, sr)

        # Wave reached
        wave_text = self.font_small.render(f"Wave Reached: {wave}", True, NEON_YELLOW)
        wr = wave_text.get_rect(centerx=SCREEN_WIDTH // 2, y=cy + 0)
        surface.blit(wave_text, wr)

        # Highscore
        hi_color = NEON_PINK if new_record else WHITE
        hi_prefix = "NEW RECORD! " if new_record else ""
        hi_text = self.font_medium.render(
            f"{hi_prefix}HIGHSCORE: {highscore:06d}", True, hi_color
        )
        hr = hi_text.get_rect(centerx=SCREEN_WIDTH // 2, y=cy + 40)
        surface.blit(hi_text, hr)

        # Restart prompt
        if (self.frame // 25) % 2 == 0:
            r_text = self.font_small.render(
                "[ENTER] Choi lai   |   [ESC] Thoat", True, NEON_GREEN
            )
            rr = r_text.get_rect(centerx=SCREEN_WIDTH // 2, y=cy + 100)
            surface.blit(r_text, rr)


class WaveAnnouncer:
    """Hiệu ứng thông báo wave mới."""

    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 48, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 22)
        self.timer = 0
        self.wave = 0
        self.active = False
        self.duration = 120  # frames

    def announce(self, wave):
        self.wave = wave
        self.timer = self.duration
        self.active = True

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def draw(self, surface):
        if not self.active:
            return

        # Fade in/out
        if self.timer > self.duration - 20:
            alpha = int(255 * (self.duration - self.timer) / 20)
        elif self.timer < 20:
            alpha = int(255 * self.timer / 20)
        else:
            alpha = 255

        alpha = max(0, min(255, alpha))

        wave_text = f"WAVE {self.wave}"
        txt = self.font.render(wave_text, True, NEON_CYAN)
        txt.set_alpha(alpha)
        rect = txt.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 - 20)
        surface.blit(txt, rect)

        sub_txt = "Get Ready!"
        stxt = self.font_sub.render(sub_txt, True, NEON_YELLOW)
        stxt.set_alpha(alpha)
        sr = stxt.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 + 25)
        surface.blit(stxt, sr)

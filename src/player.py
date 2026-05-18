"""
player.py - Class Player điều khiển phi thuyền và thanh máu.
Bao gồm hiệu ứng thruster animation và muzzle flash khi bắn.
"""

import pygame
import math
import random
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, PLAYER_MAX_HP,
    PLAYER_SHOOT_COOLDOWN, PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_INVINCIBLE_TIME, LASER_SPEED_PLAYER,
    NEON_CYAN, NEON_PINK, WHITE, BLACK, NEON_GREEN, NEON_RED, NEON_ORANGE
)
from src.laser import Laser


class Player(pygame.sprite.Sprite):
    """Phi thuyền chiến đấu của người chơi."""

    def __init__(self):
        super().__init__()
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        # Surface chính
        self.base_image = self._create_ship_surface()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=SCREEN_HEIGHT - 20
        )

        # Trạng thái
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.speed = PLAYER_SPEED

        # Cooldown bắn
        self.last_shot_time = 0
        self.shoot_flash_timer = 0

        # Bất tử sau khi trúng đạn
        self.invincible = False
        self.invincible_timer = 0
        self.blink_timer = 0

        # Thruster animation
        self.thruster_frame = 0
        self.thruster_particles = []

    def _create_ship_surface(self):
        """Vẽ phi thuyền Neon Cyberpunk bằng code (không cần file ảnh)."""
        w, h = self.width + 20, self.height + 20
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        cx = w // 2
        # Thân chính - hình tam giác góc cạnh
        body_points = [
            (cx, 4),              # Mũi tàu
            (cx + 22, h - 10),    # Cánh phải
            (cx + 14, h - 16),
            (cx + 6, h - 8),
            (cx - 6, h - 8),
            (cx - 14, h - 16),
            (cx - 22, h - 10),    # Cánh trái
        ]
        # Lớp glow ngoài
        glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, (*NEON_CYAN[:3], 30), body_points)
        surf.blit(glow_surf, (0, 0))

        # Thân tàu
        pygame.draw.polygon(surf, (15, 25, 60), body_points)
        pygame.draw.polygon(surf, NEON_CYAN, body_points, 2)

        # Kính buồng lái
        cockpit = [
            (cx, 10),
            (cx + 6, 24),
            (cx - 6, 24),
        ]
        pygame.draw.polygon(surf, (0, 150, 200, 150), cockpit)
        pygame.draw.polygon(surf, NEON_CYAN, cockpit, 1)

        # Cánh phụ
        wing_l = [(cx - 16, h - 14), (cx - 26, h - 6), (cx - 18, h - 8)]
        wing_r = [(cx + 16, h - 14), (cx + 26, h - 6), (cx + 18, h - 8)]
        pygame.draw.polygon(surf, (20, 30, 70), wing_l)
        pygame.draw.polygon(surf, NEON_CYAN, wing_l, 1)
        pygame.draw.polygon(surf, (20, 30, 70), wing_r)
        pygame.draw.polygon(surf, NEON_CYAN, wing_r, 1)

        return surf

    def _draw_thruster(self, surface, camera_offset_y=0):
        """Vẽ hiệu ứng lửa phản lực nhấp nháy ở đuôi tàu."""
        self.thruster_frame += 1
        cx = self.rect.centerx
        bot = self.rect.bottom

        # Ngọn lửa chính (nhấp nháy)
        flame_h = 8 + math.sin(self.thruster_frame * 0.5) * 4 + random.randint(-2, 2)
        flame_w = 5 + math.sin(self.thruster_frame * 0.3) * 2

        flame_points = [
            (cx - flame_w, bot - 4),
            (cx, bot + flame_h),
            (cx + flame_w, bot - 4),
        ]

        # Glow layer
        glow_surf = pygame.Surface((int(flame_w * 6), int(flame_h + 20)), pygame.SRCALPHA)
        glow_rect = glow_surf.get_rect(center=(cx, bot + flame_h // 2))
        pygame.draw.ellipse(glow_surf, (NEON_ORANGE[0], NEON_ORANGE[1], NEON_ORANGE[2], 25),
                            glow_surf.get_rect())
        surface.blit(glow_surf, glow_rect)

        # Lửa ngoài (cam)
        pygame.draw.polygon(surface, NEON_ORANGE, flame_points)
        # Lửa trong (vàng-trắng)
        inner_points = [
            (cx - flame_w * 0.4, bot - 2),
            (cx, bot + flame_h * 0.6),
            (cx + flame_w * 0.4, bot - 2),
        ]
        pygame.draw.polygon(surface, (255, 255, 200), inner_points)

        # Particles nhỏ từ thruster
        if self.thruster_frame % 2 == 0:
            self.thruster_particles.append({
                'x': cx + random.randint(-4, 4),
                'y': bot + random.randint(0, 4),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(1, 3),
                'life': random.randint(5, 12),
                'size': random.randint(1, 3),
            })

        # Cập nhật và vẽ particles
        for p in self.thruster_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.thruster_particles.remove(p)
            else:
                alpha = int(255 * p['life'] / 12)
                color = (255, 150 + random.randint(0, 50), 0, min(alpha, 255))
                ps = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, color, (p['size'], p['size']), p['size'])
                surface.blit(ps, (p['x'] - p['size'], p['y'] - p['size']))

    def _draw_muzzle_flash(self, surface):
        """Vẽ hiệu ứng lóe sáng đầu nòng khi bắn."""
        if self.shoot_flash_timer > 0:
            self.shoot_flash_timer -= 1
            cx = self.rect.centerx
            top = self.rect.top
            # Flash tròn neon cyan
            flash_size = 6 + self.shoot_flash_timer * 2
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            alpha = min(200, self.shoot_flash_timer * 50)
            pygame.draw.circle(flash_surf, (*NEON_CYAN[:3], alpha),
                               (flash_size, flash_size), flash_size)
            pygame.draw.circle(flash_surf, (*WHITE[:3], alpha // 2),
                               (flash_size, flash_size), flash_size // 2)
            surface.blit(flash_surf, (cx - flash_size, top - flash_size))

    def update(self, keys):
        """Cập nhật vị trí và trạng thái người chơi."""
        if not self.alive:
            return

        # Di chuyển trái/phải
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Giới hạn trong màn hình
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)

        # Xử lý thời gian bất tử
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincible_timer > PLAYER_INVINCIBLE_TIME:
                self.invincible = False
            self.blink_timer += 1

    def shoot(self, laser_group):
        """Bắn đạn laser (có cooldown)."""
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= PLAYER_SHOOT_COOLDOWN:
            self.last_shot_time = now
            self.shoot_flash_timer = 5

            laser = Laser(
                self.rect.centerx, self.rect.top,
                LASER_SPEED_PLAYER, NEON_CYAN, is_player=True
            )
            laser_group.add(laser)
            return True
        return False

    def take_damage(self):
        """Nhận sát thương, kích hoạt bất tử tạm thời."""
        if self.invincible:
            return False

        self.hp -= 1
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True  # Player chết

        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        return False

    def draw(self, surface):
        """Vẽ phi thuyền lên surface chính."""
        if not self.alive:
            return

        # Nhấp nháy khi bất tử
        if self.invincible and self.blink_timer % 6 < 3:
            return

        surface.blit(self.image, self.rect)
        self._draw_thruster(surface)
        self._draw_muzzle_flash(surface)

    def draw_health_bar(self, surface):
        """Vẽ thanh máu dưới phi thuyền."""
        if not self.alive:
            return

        bar_w = 50
        bar_h = 5
        x = self.rect.centerx - bar_w // 2
        y = self.rect.bottom + 6

        # Nền
        pygame.draw.rect(surface, (40, 40, 40), (x, y, bar_w, bar_h), border_radius=2)
        # Máu
        hp_ratio = self.hp / PLAYER_MAX_HP
        if hp_ratio > 0.5:
            color = NEON_GREEN
        elif hp_ratio > 0.25:
            color = NEON_ORANGE
        else:
            color = NEON_RED
        fill_w = int(bar_w * hp_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, color, (x, y, fill_w, bar_h), border_radius=2)
        # Viền
        pygame.draw.rect(surface, WHITE, (x, y, bar_w, bar_h), 1, border_radius=2)

    def reset(self):
        """Reset trạng thái người chơi."""
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.invincible = False
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.thruster_particles.clear()

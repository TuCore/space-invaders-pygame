"""
invader.py - Class Invader và logic di chuyển bầy đàn (Fleet).
3 loại quái: Elite (tím), Medium (đỏ), Grunt (vàng).
Mỗi loại có 2 frame animation để tạo hiệu ứng di chuyển.
"""

import pygame
import random
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INVADER_ROWS, INVADER_COLS,
    INVADER_PADDING_X, INVADER_PADDING_Y, INVADER_OFFSET_X, INVADER_OFFSET_Y,
    INVADER_BASE_SPEED, INVADER_DROP_DISTANCE, INVADER_SHOOT_CHANCE,
    INVADER_TYPES, LASER_SPEED_ENEMY, NEON_PURPLE, NEON_RED, NEON_YELLOW,
    BLACK, WHITE
)
from src.laser import Laser


class Invader(pygame.sprite.Sprite):
    """Một quái vật không gian đơn lẻ."""

    def __init__(self, inv_type, row, col, x, y):
        super().__init__()
        self.inv_type = inv_type
        self.row = row
        self.col = col
        self.points = INVADER_TYPES[inv_type]["points"]
        self.color = INVADER_TYPES[inv_type]["color"]

        self.size = 32
        # Tạo 2 frame animation
        self.frames = [
            self._create_frame(0),
            self._create_frame(1),
        ]
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 30  # Frames giữa mỗi lần đổi

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def _create_frame(self, frame_num):
        """Vẽ quái vật bằng pixel art code - 2 frame khác nhau."""
        s = self.size + 8
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        cx, cy = s // 2, s // 2

        if self.inv_type == "elite":
            self._draw_elite(surf, cx, cy, s, frame_num)
        elif self.inv_type == "medium":
            self._draw_medium(surf, cx, cy, s, frame_num)
        else:
            self._draw_grunt(surf, cx, cy, s, frame_num)

        return surf

    def _draw_elite(self, surf, cx, cy, s, frame):
        """Quái tinh anh - hình dạng phức tạp, màu tím."""
        color = self.color
        glow = (*color[:3], 40)

        # Glow
        pygame.draw.ellipse(surf, glow, (2, 2, s - 4, s - 4))

        # Thân chính
        body = [
            (cx, 4), (cx + 12, cy - 4), (cx + 16, cy + 4),
            (cx + 10, cy + 10), (cx + 14, s - 6) if frame == 0 else (cx + 16, s - 4),
            (cx, cy + 12),
            (cx - 14, s - 6) if frame == 0 else (cx - 16, s - 4),
            (cx - 10, cy + 10), (cx - 16, cy + 4), (cx - 12, cy - 4),
        ]
        pygame.draw.polygon(surf, (30, 0, 50), body)
        pygame.draw.polygon(surf, color, body, 2)

        # Mắt
        pygame.draw.circle(surf, WHITE, (cx - 5, cy - 2), 4)
        pygame.draw.circle(surf, WHITE, (cx + 5, cy - 2), 4)
        pygame.draw.circle(surf, color, (cx - 5, cy - 2), 2)
        pygame.draw.circle(surf, color, (cx + 5, cy - 2), 2)

    def _draw_medium(self, surf, cx, cy, s, frame):
        """Quái tầm trung - hình dáng cân đối, màu đỏ."""
        color = self.color
        glow = (*color[:3], 35)
        pygame.draw.ellipse(surf, glow, (4, 4, s - 8, s - 8))

        # Thân hình bầu dục
        pygame.draw.ellipse(surf, (50, 10, 10), (cx - 14, cy - 10, 28, 22))
        pygame.draw.ellipse(surf, color, (cx - 14, cy - 10, 28, 22), 2)

        # Râu/chân - frame khác nhau
        if frame == 0:
            tentacles = [
                ((cx - 10, cy + 8), (cx - 14, cy + 16)),
                ((cx - 4, cy + 10), (cx - 4, cy + 18)),
                ((cx + 4, cy + 10), (cx + 4, cy + 18)),
                ((cx + 10, cy + 8), (cx + 14, cy + 16)),
            ]
        else:
            tentacles = [
                ((cx - 10, cy + 8), (cx - 16, cy + 14)),
                ((cx - 4, cy + 10), (cx - 6, cy + 18)),
                ((cx + 4, cy + 10), (cx + 6, cy + 18)),
                ((cx + 10, cy + 8), (cx + 16, cy + 14)),
            ]
        for start, end in tentacles:
            pygame.draw.line(surf, color, start, end, 2)

        # Mắt
        pygame.draw.circle(surf, WHITE, (cx - 5, cy - 2), 3)
        pygame.draw.circle(surf, WHITE, (cx + 5, cy - 2), 3)
        pygame.draw.circle(surf, (200, 0, 0), (cx - 5, cy - 2), 1)
        pygame.draw.circle(surf, (200, 0, 0), (cx + 5, cy - 2), 1)

    def _draw_grunt(self, surf, cx, cy, s, frame):
        """Quái lính cát - hình dáng đơn giản, màu vàng."""
        color = self.color
        glow = (*color[:3], 30)
        pygame.draw.ellipse(surf, glow, (6, 6, s - 12, s - 12))

        # Thân hình vuông bo tròn
        body_rect = pygame.Rect(cx - 12, cy - 8, 24, 18)
        pygame.draw.rect(surf, (50, 45, 0), body_rect, border_radius=4)
        pygame.draw.rect(surf, color, body_rect, 2, border_radius=4)

        # Antena
        if frame == 0:
            pygame.draw.line(surf, color, (cx - 6, cy - 8), (cx - 10, cy - 16), 2)
            pygame.draw.line(surf, color, (cx + 6, cy - 8), (cx + 10, cy - 16), 2)
        else:
            pygame.draw.line(surf, color, (cx - 6, cy - 8), (cx - 8, cy - 16), 2)
            pygame.draw.line(surf, color, (cx + 6, cy - 8), (cx + 8, cy - 16), 2)

        # Đầu antena
        pygame.draw.circle(surf, color,
                           (cx - 10 if frame == 0 else cx - 8, cy - 16), 2)
        pygame.draw.circle(surf, color,
                           (cx + 10 if frame == 0 else cx + 8, cy - 16), 2)

        # Chân
        if frame == 0:
            pygame.draw.line(surf, color, (cx - 8, cy + 10), (cx - 12, cy + 16), 2)
            pygame.draw.line(surf, color, (cx + 8, cy + 10), (cx + 12, cy + 16), 2)
        else:
            pygame.draw.line(surf, color, (cx - 8, cy + 10), (cx - 10, cy + 16), 2)
            pygame.draw.line(surf, color, (cx + 8, cy + 10), (cx + 10, cy + 16), 2)

        # Mắt
        pygame.draw.circle(surf, WHITE, (cx - 4, cy), 3)
        pygame.draw.circle(surf, WHITE, (cx + 4, cy), 3)
        pygame.draw.circle(surf, (180, 150, 0), (cx - 4, cy), 1)
        pygame.draw.circle(surf, (180, 150, 0), (cx + 4, cy), 1)

    def animate(self):
        """Chuyển frame animation."""
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = 1 - self.frame_index
            self.image = self.frames[self.frame_index]

    def try_shoot(self, enemy_laser_group):
        """Cố gắng bắn đạn ngẫu nhiên."""
        if random.random() < INVADER_SHOOT_CHANCE:
            laser = Laser(
                self.rect.centerx, self.rect.bottom,
                LASER_SPEED_ENEMY, NEON_RED, is_player=False
            )
            enemy_laser_group.add(laser)


class Fleet:
    """Quản lý toàn bộ đội hình quái vật (Grid Movement Matrix)."""

    def __init__(self):
        self.invaders = pygame.sprite.Group()
        self.direction = 1  # 1 = phải, -1 = trái
        self.speed = INVADER_BASE_SPEED
        self.drop_needed = False
        self.wave = 1

    def spawn_wave(self, wave=1):
        """Tạo một làn sóng quái vật mới."""
        self.invaders.empty()
        self.direction = 1
        self.wave = wave
        # Tăng tốc theo wave
        self.speed = INVADER_BASE_SPEED + (wave - 1) * 0.3

        for row in range(INVADER_ROWS):
            # Xác định loại quái dựa trên hàng
            inv_type = "grunt"
            for t_name, t_data in INVADER_TYPES.items():
                if row in t_data["rows"]:
                    inv_type = t_name
                    break

            for col in range(INVADER_COLS):
                x = INVADER_OFFSET_X + col * INVADER_PADDING_X
                y = INVADER_OFFSET_Y + row * INVADER_PADDING_Y
                invader = Invader(inv_type, row, col, x, y)
                self.invaders.add(invader)

    def update(self, enemy_laser_group):
        """Cập nhật di chuyển bầy đàn: ngang → chạm biên → hạ → đổi hướng."""
        if len(self.invaders) == 0:
            return

        # Tăng tốc khi quái giảm
        total = INVADER_ROWS * INVADER_COLS
        remaining = len(self.invaders)
        speed_mult = 1.0 + (total - remaining) / total * 2.5
        current_speed = self.speed * speed_mult

        # Kiểm tra chạm biên
        hit_edge = False
        for inv in self.invaders:
            if self.direction == 1 and inv.rect.right >= SCREEN_WIDTH - 10:
                hit_edge = True
                break
            elif self.direction == -1 and inv.rect.left <= 10:
                hit_edge = True
                break

        if hit_edge:
            # Hạ thấp cao độ & đổi hướng
            self.direction *= -1
            for inv in self.invaders:
                inv.rect.y += INVADER_DROP_DISTANCE

        # Di chuyển ngang
        for inv in self.invaders:
            inv.rect.x += int(current_speed * self.direction)
            inv.animate()
            inv.try_shoot(enemy_laser_group)

    def is_defeated(self):
        """Kiểm tra toàn bộ quái đã bị tiêu diệt chưa."""
        return len(self.invaders) == 0

    def reached_bottom(self):
        """Kiểm tra quái đã chạm đáy (xâm chiếm) chưa."""
        for inv in self.invaders:
            if inv.rect.bottom >= SCREEN_HEIGHT - 60:
                return True
        return False

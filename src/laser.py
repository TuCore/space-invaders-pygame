"""
laser.py - Class Laser xử lý đạn bay và tự hủy khi ra khỏi màn hình.
Áp dụng quản lý vòng đời vật thể (Object Lifecycle) để tránh Memory Leak.
"""

import pygame
import math
from src.settings import (
    LASER_WIDTH, LASER_HEIGHT, SCREEN_HEIGHT,
    NEON_CYAN, NEON_RED, WHITE
)


class Laser(pygame.sprite.Sprite):
    """Viên đạn laser - tự hủy khi bay ra khỏi biên màn hình."""

    def __init__(self, x, y, speed, color=None, is_player=True):
        super().__init__()
        self.speed = speed
        self.is_player = is_player
        self.color = color or (NEON_CYAN if is_player else NEON_RED)

        # Tạo surface đạn với hiệu ứng phát sáng (glow)
        glow_w = LASER_WIDTH * 4
        glow_h = LASER_HEIGHT + 6
        self.image = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        self._draw_laser(glow_w, glow_h)

        self.rect = self.image.get_rect(centerx=x, centery=y)
        self.y_float = float(y)

    def _draw_laser(self, w, h):
        """Vẽ đạn laser với hiệu ứng neon glow."""
        cx = w // 2
        # Lớp glow ngoài (mờ)
        glow_color = (*self.color[:3], 40)
        pygame.draw.rect(self.image, glow_color,
                         (cx - LASER_WIDTH * 2, 0, LASER_WIDTH * 4, h),
                         border_radius=4)
        # Lớp glow giữa
        glow_color2 = (*self.color[:3], 90)
        pygame.draw.rect(self.image, glow_color2,
                         (cx - LASER_WIDTH, 1, LASER_WIDTH * 2, h - 2),
                         border_radius=3)
        # Lõi sáng
        core_color = (*WHITE[:3], 220)
        pygame.draw.rect(self.image, core_color,
                         (cx - LASER_WIDTH // 2, 2, LASER_WIDTH, h - 4),
                         border_radius=2)
        # Outer color layer
        pygame.draw.rect(self.image, (*self.color[:3], 180),
                         (cx - LASER_WIDTH + 1, 1, LASER_WIDTH * 2 - 2, h - 2),
                         border_radius=3)

    def update(self):
        """Di chuyển đạn và tự hủy (Garbage Collection) khi ra khỏi màn hình."""
        self.y_float += self.speed
        self.rect.centery = int(self.y_float)

        # Tự động kill khỏi tất cả Group khi vượt biên
        if self.rect.bottom < -10 or self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()


class LaserGroup(pygame.sprite.Group):
    """Nhóm quản lý tất cả đạn laser, tự dọn dẹp bộ nhớ."""

    def cleanup(self):
        """Xóa thủ công những viên đạn đã bay ra ngoài (dự phòng)."""
        for laser in self.sprites():
            if laser.rect.bottom < -20 or laser.rect.top > SCREEN_HEIGHT + 20:
                laser.kill()

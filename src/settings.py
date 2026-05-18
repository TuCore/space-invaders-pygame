"""
settings.py - Lưu toàn bộ hằng số cấu hình cho game Space Invaders.
"""

# ── Màn hình ──────────────────────────────────────────────
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60
TITLE = "Space Invaders - Neon Cyberpunk Edition"

# ── Màu sắc Neon Cyberpunk ────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
NEON_CYAN = (0, 240, 255)
NEON_PINK = (255, 0, 200)
NEON_PURPLE = (180, 0, 255)
NEON_RED = (255, 40, 40)
NEON_YELLOW = (255, 230, 0)
NEON_GREEN = (0, 255, 100)
NEON_ORANGE = (255, 140, 0)
DARK_BG = (5, 5, 20)
DARK_BLUE = (10, 10, 40)
GRID_COLOR = (20, 20, 60)
HUD_BG = (10, 10, 30, 180)

# ── Người chơi ────────────────────────────────────────────
PLAYER_SPEED = 6
PLAYER_MAX_HP = 5
PLAYER_SHOOT_COOLDOWN = 250          # ms giữa mỗi viên đạn
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_INVINCIBLE_TIME = 1500        # ms bất tử sau khi bị trúng đạn

# ── Đạn Laser ─────────────────────────────────────────────
LASER_SPEED_PLAYER = -8              # Âm = bay lên
LASER_SPEED_ENEMY = 4                # Dương = bay xuống
LASER_WIDTH = 4
LASER_HEIGHT = 18

# ── Quái vật ──────────────────────────────────────────────
INVADER_ROWS = 5
INVADER_COLS = 10
INVADER_PADDING_X = 55
INVADER_PADDING_Y = 50
INVADER_OFFSET_X = 75
INVADER_OFFSET_Y = 80
INVADER_BASE_SPEED = 1.0
INVADER_DROP_DISTANCE = 30
INVADER_SHOOT_CHANCE = 0.002         # Xác suất mỗi frame mỗi quái bắn

# Loại quái & điểm số
INVADER_TYPES = {
    "elite":  {"color": NEON_PURPLE, "points": 30, "rows": [0]},
    "medium": {"color": NEON_RED,    "points": 20, "rows": [1, 2]},
    "grunt":  {"color": NEON_YELLOW, "points": 10, "rows": [3, 4]},
}

# ── Hiệu ứng ─────────────────────────────────────────────
PARTICLE_COUNT_EXPLOSION = 20
PARTICLE_LIFETIME = 30               # frames
STAR_LAYERS = 3
STAR_COUNT_PER_LAYER = 60

# ── Điểm số ───────────────────────────────────────────────
HIGHSCORE_FILE = "highscore.dat"

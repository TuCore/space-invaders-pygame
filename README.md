# 🌌 Space Invaders - Pygame Edition

Một bản remake hiện đại của tựa game cổ điển huyền thoại **Space Invaders** (Bắn Gà / Bắn Quái Không Gian) được phát triển bằng ngôn ngữ **Python** và thư viện **Pygame**. Dự án áp dụng mô hình lập trình hướng đối tượng (OOP) để quản lý thực thể, tối ưu hóa bộ nhớ và xây dựng hiệu ứng đồ họa bắt mắt.

---

## 🎮 Tổng Quan Trò Chơi

Trong game, người chơi sẽ điều khiển một phi thuyền chiến đấu tối tân nằm ở đáy màn hình, di chuyển theo trục ngang để phòng thủ trước các toán quân lính ngoài hành tinh đang dịch chuyển lượn sóng và tiến dần xuống mặt đất. Mục tiêu là tiêu diệt toàn bộ làn sóng kẻ địch trước khi chúng xâm chiếm hành tinh hoặc phá hủy phi thuyền của bạn.

### Các Tính Năng Nổi Bật:
*   **Hệ thống kẻ địch phân tầng:** Quái vật di chuyển theo bầy đàn (Fleet), tự động tăng tốc độ khi số lượng giảm xuống và có khả năng bắn trả ngẫu nhiên.
*   **Hệ thống Điểm số & Highscore:** Tính điểm dựa trên loại quái vật bị tiêu diệt và lưu lại điểm số cao nhất.
*   **Đồ họa & Hiệu ứng Tân tiến:** Sử dụng hiệu ứng hạt (Particle system) cho các vụ nổ, hiệu ứng hoạt ảnh (Animation) khi quái vật di chuyển và thanh máu (Health bar) trực quan cho người chơi.
*   **Âm thanh sống động:** Nhạc nền dồn dập, hiệu ứng âm thanh (SFX) riêng biệt cho tiếng laser, tiếng nổ và khi game over.

---

## 🧠 Kiến Thức Lập Trình Đạt Được

Dự án này là một bài thực hành hoàn hảo để nắm vững các tư duy lập trình game cốt lõi:

1.  **Quản lý Bộ nhớ & Vòng đời Vật thể (Object Lifecycle):** Học cách quản lý danh sách đạn (Laser) thông qua mảng/nhóm. Đạn được khởi tạo khi nhấn nút và **tự động xóa khỏi bộ nhớ (Garbage Collection)** ngay khi bay ra khỏi biên màn hình để tránh hiện tượng rò rỉ bộ nhớ (Memory Leak).
2.  **Sử dụng `pygame.sprite.Sprite` và `Group`:** Tận dụng tối đa sức mạnh của Pygame để quản lý hàng loạt thực thể kẻ địch. Sử dụng các hàm toán học tích hợp sẵn để xử lý va chạm diện rộng (`pygame.sprite.groupcollide`) giữa danh sách đạn và danh sách quái vật chỉ với một dòng code.
3.  **Thuật toán Di chuyển Bầy đàn (Grid Movement Matrix):** Lập trình trạng thái dịch chuyển đồng bộ của cả đội hình quái vật: di chuyển ngang $\rightarrow$ chạm biên $\rightarrow$ hạ thấp cao độ $\rightarrow$ đổi hướng ngược lại.

---

## 🎨 Hướng Dẫn Thiết Kế Đồ Họa & Giao Diện (UI/UX)

Để trò chơi có trải nghiệm thị giác "đẹp và cuốn hút", dự án hướng tới phong cách **Neon Cyberpunk** với các thiết kế asset như sau:

*   **Phi Thuyền Người Chơi (Player):** Model phi thuyền không gian góc cạnh, có hiệu ứng lửa phản lực (Thruster animation) nhấp nháy ở đuôi. Khi bắn, đầu nòng súng lóe sáng màu xanh Cyan.
*   **Quái Vật Không Gian (Invaders):** Chia làm 3 loại với màu sắc và điểm số khác nhau (ví dụ: Hàng trên cùng màu Tím - Quái tinh anh; Hàng giữa màu Đỏ - Quái tầm trung; Hàng dưới màu Vàng - Quái lính cát). Mỗi loại có ít nhất 2 khung hình (Frames) để tạo hiệu ứng vỗ cánh/di chuyển liên tục.
*   **Hiệu ứng Vụ Nổ (Explosion Particles):** Thay vì biến mất đột ngột, khi quái vật chết, một Sprite Sheet gồm 5-6 khung hình vụ nổ sẽ được kích hoạt, kèm theo các hạt pixel nhỏ bay tán loạn rồi mờ dần (Fade out).
*   **Nền Trời (Background):** Sử dụng một bức ảnh vũ trụ sâu thẳm (Deep Space) với các tầng sao (Stars) di chuyển chậm về phía dưới (Parallax Scrolling) tạo cảm giác phi thuyền đang thực sự bay về phía trước.

---

## 📂 Cấu Trúc Thư Mục Dự Án

Dự án được tổ chức theo cấu trúc dạng mô-đun (Modular) rõ ràng giúp dễ dàng bảo trì và mở rộng:

```text
space-invaders/
│
├── assets/                  # Quản lý toàn bộ tài nguyên của game
│   ├── images/              # Hình ảnh đồ họa (.png)
│   │   ├── player.png       # Phi thuyền người chơi
│   │   ├── invaders/        # Thư mục chứa các loại quái vật (invader1, invader2...)
│   │   ├── laser.png        # Tia đạn laser
│   │   └── explosion.png    # Sprite sheet hiệu ứng nổ
│   └── audio/               # Âm thanh (.wav, .mp3)
│       ├── background.mp3   # Nhạc nền trận đấu
│       ├── laser.wav        # Tiếng bắn đạn
│       └── explode.wav      # Tiếng nổ khi quái chết
│
├── src/                     # Thư mục mã nguồn chính
│   ├── __init__.py
│   ├── settings.py          # Lưu các hằng số: kích thước màn hình, FPS (60), tốc độ, màu sắc
│   ├── player.py            # Class Player điều khiển phi thuyền và thanh máu
│   ├── invader.py           # Class Invader và điều khiển logic di chuyển bầy đàn
│   ├── laser.py             # Class Laser xử lý đạn bay và tự hủy khi ra khỏi màn hình
│   └── UI.py                # Xử lý vẽ điểm số, màn hình Menu, Game Over và nút bấm
│
├── main.py                  # Điểm khởi chạy chính (Vòng lặp Game Loop, xử lý va chạm chính)
├── requirements.txt         # Danh sách thư viện phụ thuộc
└── README.md                # Tệp tài liệu hướng dẫn này
"# space-invaders-pygame" 

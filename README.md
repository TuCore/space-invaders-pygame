# 🌌 Space Invaders - Pygame Edition

A modern, high-performance 2D arcade remake of the legendary classic **Space Invaders** (Bắn Gà / Bắn Quái Không Gian), engineered using **Python** and the **Pygame** framework. This project heavily leverages Object-Oriented Programming (OOP) principles, clean state machines, and optimized asset lifecycles to deliver fluid 60-FPS gameplay alongside eye-catching visual effects.

---

## 🎮 Game Overview

Players command an advanced starfighter anchored at the bottom of the viewport, maneuvering horizontally to defend their territory against a descending armada of hostile alien invaders. The invaders operate as a synchronized grid matrix, executing complex weaving formations that progressively accelerate as their numbers decline. Your ultimate objective: neutralize the extra-terrestrial threat before they breach your defensive line or compromise your structural integrity.

### Key Features:
* **Dynamic Swarm Grid AI:** Invaders shift smoothly as a fleet, dropping down a row and reversing direction upon colliding with screen boundaries. Movement speed dynamically scales inversely with the remaining fleet size.
* **Persistent High Score Management:** Automatically tracks scores based on different alien tiers and persists the all-time high score locally across independent game sessions.
* **Advanced Visual Effects (VFX):** Built-in custom particle systems handling stylized destruction bursts, frame-by-frame sprite sheet rendering for smooth entity animation, and real-time interactive health bars.
* **Immersive Soundscapes (SFX & Audio Mixer):** Features atmospheric deep-space background tracks playing concurrently with independent audio channels dedicated to synchronized laser fires, explosions, and game-state transitions.

---

## 🛠️ Tech Stack & Dependencies

### System Requirements
* **Operating System:** Windows 10/11, macOS, or Linux
* **Base Language:** Python `3.11.x` or `3.12.x` *(Highly recommended for optimal runtime speeds and native byte-code optimization)*

### Libraries & Frameworks
* **Core Game Engine:** `pygame-ce` (Pygame Community Edition) `2.5.2` or standard `pygame` `2.5.2+`
* **Asset Management:** `Pillow` `10.2.0+` *(Optional internal asset configuration)*

---

## 🚀 Installation & Setup Guide

### 🔹 For Casual Players (Just Want to Play)

**Prerequisite:** Ensure Python is installed on your computer. 
> ⚠️ **CRITICAL WINDOWS NOTE:** During the Python installation setup process, you **MUST** check the box that says **"Add python.exe to PATH"**. If missed, your system terminal will fail to recognize the executable commands.

1.  **Download the Code:** Download and extract the source zip file directly from GitHub, or clone the repository via terminal:
    ```bash
    git clone [https://github.com/your-username/space-invaders-pygame.git](https://github.com/your-username/space-invaders-pygame.git)
    cd space-invaders-pygame
    ```
2.  **Install the Engine:** Open your Terminal (macOS/Linux) or Command Prompt/PowerShell (Windows) inside the extracted project folder and run:
    ```bash
    pip install pygame
    ```
3.  **Boot Up the Game:** Execute the core controller script to launch the application:
    ```bash
    python main.py
    ```

---

### 🔸 For Developers (Local Environment Configuration)

To sandbox your dependencies and prevent cross-package corruption on your global machine, configure an isolated virtual environment:

1.  **Initialize Virtual Environment:**
    ```bash
    python -m venv venv
    ```
2.  **Activate Environment Context:**
    * **Windows (CMD / PowerShell):**
        ```powershell
        .\venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
3.  **Install Frozen Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🧠 Architectural Insights & Core Logic

This repository acts as a production-ready educational blueprint for mastering 2D video game math and patterns:

1.  **Automated Memory & Object Lifecycle Management:** Laser entities are bound inside active array groups. To prevent severe **Memory Leaks**, projectiles are audited every frame; objects are instantly purged from the heap memory using Pygame's native `.kill()` method the moment their bounding boxes (`Rect`) exit top/bottom viewport margins.
2.  **Sprite Batching & Broadphase Collisions:** Utilizes `pygame.sprite.Sprite` and `pygame.sprite.Group` architectures. Instead of nesting expensive $O(N^2)$ tracking loops, multi-entity collision registration is evaluated using optimized native sweeping sweeps (`pygame.sprite.groupcollide`), resolving broad hitboxes in a single internal C-call.
3.  **Thuật toán Di chuyển Bầy đàn (Grid Movement Matrix):** Tracks the boundaries of the entire invader matrix collectively. When the outermost alive sprite intersects an edge, a global flag trips—lowering the elevation coordinate of all fleet elements simultaneously before flipping the horizontal velocity vector.

---

## 🎨 Asset & UI/UX Design Guidelines

The game exhibits a polished **Neon Cyberpunk / Arcade Retro** aesthetic using targeted asset models:
* **Player Starfighter:** Hard-edged, sleek sci-fi ship vectors paired with animated thruster flame toggles and custom cyan muzzle flashes mapped to weapon fire events.
* **Invader Hierarchy:** Divided into 3 separate visual ranks yielding variable point allocations (Top Row: Purple Elite; Middle Rows: Red Vanguard; Bottom Rows: Yellow Grunts). Each entity switches between a minimum of 2 frames to animate movement.
* **Explosion Particles:** Upon receiving fatal damage, entities spawn localized burst handlers that cycle through a pre-baked 6-frame alpha sprite sheet, scattering pixel fragments that fade smoothly over time.
* **Deep Space Backdrop:** Features layered, slow-moving stars using an artificial **Parallax Scrolling** algorithm, generating an organic illusion of 3D cosmic velocity.

---

## 📂 Project Directory Structure

The project code is built using modular styling principles to allow easy structural adjustments:

```text
space-invaders/
│
├── assets/                  # Binary media storage (Immutable game data)
│   ├── images/              # Graphic texturing and sprites (.png)
│   │   ├── player.png       # Primary player spacecraft texture
│   │   ├── invaders/        # Dynamic sub-folder storing alien ranks
│   │   ├── laser.png        # Laser beam projectile assets
│   │   └── explosion.png    # Pre-rendered destruction sprite sheet
│   └── audio/               # Digital sound files (.wav for actions, .mp3 for loops)
│       ├── background.mp3   # Looping high-tempo game soundtrack
│       ├── laser.wav        # Primary fire sound effect
│       └── explode.wav      # Entity structural failure sound effect
│
├── src/                     # Isolated system source code
│   ├── __init__.py
│   ├── settings.py          # Global configurations: Screen resolution, targeted FPS, velocity constants
│   ├── player.py            # Player class tracking movement boundaries and health maps
│   ├── invader.py           # Swarm array generation, behavior patterns, and speed scaling
│   ├── laser.py             # Individual bullet update logic and bounding box disposal
│   └── UI.py                # Main menu overlay renders, scorecard updates, and game-over scenes
│
├── main.py                  # Primary runtime file (Initializes engine clock and game loop ticks)
├── requirements.txt         # Package specification file
└── README.md                # System documentation manual
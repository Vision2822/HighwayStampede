# 🤠 Highway Stampede: AI-Powered 3D Endless Runner

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Engine](https://img.shields.io/badge/Engine-Ursina-orange)
![AI](https://img.shields.io/badge/AI-MediaPipe-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

> **Highway Stampede** is a high-octane 3D endless runner where you play as a cowboy leaping between moving vehicles.
>
> 🚀 **New for 2025:** This project features a **Hands-Free AI Control System** that tracks your head movements in real-time to steer the character!

---

## 🎮 Game Features

- ** infinite Procedural World:** The highway generates infinitely using Python **Generators**, ensuring no two runs are the same.
- **🤖 AI Head Tracking:** Uses **Google MediaPipe** and **OpenCV** to track facial landmarks. Tilt your head Left or Right to steer the cowboy!
- **⚡ Multithreading:** The computer vision logic runs on a separate **daemon thread**, ensuring the game maintains a smooth 60 FPS while processing video input.
- **🏎️ Traffic System:** Diverse vehicles (Police, Taxi, Race cars) with unique speeds and behaviors.
- **💥 Physics & Particles:** Real-time collision detection, ragdoll physics, and explosion effects.
- **💾 Persistence:** High scores are saved and loaded via CSV file handling.

## 🛠️ Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Vision2822/HighwayStampede.git
    cd highway-stampede
    ```

2.  **Install Dependencies:**
    Make sure you have Python installed. Install the required libraries using the pre-configured file:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Game:**
    ```bash
    python main.py
    ```

---

## 🕹️ Controls

You can play using **Classic Keyboard** controls OR the experimental **AI Head Tracking**.

| Action          | Keyboard Input            | AI Input (Webcam) |
| :-------------- | :------------------------ | :---------------- |
| **Steer Left**  | `A` or `Left Arrow`       | Tilt Head Left    |
| **Steer Right** | `D` or `Right Arrow`      | Tilt Head Right   |
| **Jump**        | `SPACE`                   | N/A               |
| **Lasso Car**   | Release `SPACE` (Mid-air) | N/A               |
| **Restart**     | `R`                       | N/A               |
| **Quit**        | `ESC`                     | N/A               |

> **Note on AI:** Ensure your room is well-lit for the best head-tracking performance. The game automatically prioritizes keyboard input if keys are pressed.

---

## 📂 Project Structure

This project implements core academic Python concepts:

- **`main.py`**: The main entry point containing the Game Loop, Player Class, and AI Threading logic.
- **`highscores.csv`**: Automated file for persistent data storage (**File I/O**).
- **Concepts Used:**
  - **OOP:** Classes for Player, Vehicles, and Collectibles using Inheritance.
  - **Functional Programming:** `lambda` functions for sorting scores.
  - **Generators:** `yield` used for spawning terrain efficiently.
  - **Multithreading:** `threading` module for parallel AI processing.

---

## 🎨 Credits & Assets

### 3D Models

- **Kenney Assets (Kenney.nl):** A massive thanks to [Kenney.nl](https://kenney.nl) for the high-quality 3D vehicle and environment assets used in this project.
  - _License:_ CC0 1.0 Universal

### Libraries

- **Ursina Engine:** For the 3D rendering pipeline.
- **MediaPipe:** For the AI Face Mesh detection.
- **OpenCV:** For video capture processing.

---

## 📜 License

This project is for educational purposes.

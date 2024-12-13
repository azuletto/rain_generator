# Rain Simulator with Python

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square) ![pygame](https://img.shields.io/badge/pygame-2.1-green?style=flat-square)

🌧️ A simple yet immersive rain and thunderstorm simulator built with Python and `pygame`. The project features dynamic lightning effects, realistic thunder sounds, and procedurally generated rain noise for an atmospheric experience.

---

## ✨ Features

- **Lightning Effects:** Flashes of light simulating real lightning strikes.
- **Thunder Sounds:** Plays random thunder sounds with adjustable volume.
- **Rain Noise:** Procedurally generated background rain sounds with smooth transitions.
- **Interactive Controls:**
  - Adjust volume for thunder, rain, and raindrop effects.
  - Change storm intensity levels (Low, Medium, High).
  - Toggle fullscreen mode.

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rain_generator
   cd thunderstorm_main
   ```

2. Install the required dependencies:
   ```bash
   pip install pygame numpy sounddevice scipy
   ```

3. Run the application:
   ```bash
   python thunderstorm_simulator.py
   ```

---

## 🎮 Usage

- **Change Intensity:** Use the on-screen menu to switch between Low, Medium, and High intensity levels.
- **Toggle Fullscreen:** Press `F` to enter or exit fullscreen mode.
- **Adjust Volume:** Use the interactive modal to fine-tune sound levels.

---

## ⚙️ How It Works

- **Visuals:**
  - `pygame` is used to create dynamic flashes representing lightning.
- **Audio:**
  - Rain sounds are generated procedurally using `numpy` and `scipy`.
  - Thunder sounds are loaded and played randomly.
- **Interactive Menu:**
  - Adjustable sound sliders and storm intensity controls implemented with `pygame` events.

---

## 🤝 Contributing

Feel free to submit issues or fork the repository to improve this project. Contributions are always welcome!

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

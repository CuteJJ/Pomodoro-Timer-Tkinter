# Simple Pomodoro Timer with Tkinter

A clean, fully-featured **Pomodoro Timer** built with **Python’s Tkinter GUI library**.  
Includes multiple timer modes (Pomodoro & Revision), configurable durations, automatic session tracking, and local JSON save/backup.

---

## Features

- **Pomodoro Mode** — Focus sessions with short and long breaks  
- **Revision Mode** — Single continuous study session (no breaks)  
- **Customizable Durations** — Change work / break lengths in-app  
- **Auto Save & Backup** — Saves progress to `pomodoro_data.json` and keeps `.bak` backup  
- **Statistics Panel** — View sessions completed, total study minutes, averages, and recent activity  
- **Threaded Timer** — Runs in background to keep the UI responsive

---

## Project Structure

```
.
├── main.py              # Entry point of the application (MainApplication)
├── PomodoroTimer.py     # Timer logic, GUI classes, and data management
└── pomodoro_data.json   # Auto-generated file storing session progress (created at runtime)
```

---

## Requirements

- Python 3.8+ (3.10+ recommended)
- `tkinter` (usually bundled with Python on Windows/macOS; on some Linux distros install via package manager)
- Uses only Python standard library modules: `tkinter`, `json`, `threading`, `time`, `datetime`, `os`

---

## Quick Start

1. Clone or download this repository:
   ```bash
   git clone https://github.com/CuteJJ/Pomodoro-Timer-Tkinter.git
   ```

2. Run the app:
   ```bash
   python main.py
   ```

---

## How to use

- Launch app, click **📚 Study Pomodoro Timer**.
- Select **Pomodoro** or **Revision** from the dropdown.
- Click **▶ Start Timer** to begin; use **⏸ Pause**, **↻ Reset**, or **⚙️ Timer Settings** to customize durations.
- After sessions finish, you’re prompted to auto-start the next session; progress is saved automatically for Pomodoro mode.

---

## Data & Privacy

- Progress and settings are saved to `pomodoro_data.json` in the same folder.
- A backup file `pomodoro_data.json.bak` is kept when saving new data.
- Delete these files to fully reset stored progress.

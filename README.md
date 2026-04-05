# ASL Speed Test

ASL Speed Test is a desktop Python app for practicing American Sign Language letter recognition with a timed typing challenge.

## Project Structure

```text
asl-speed-test/
├── assets/         # sign images and sound effects
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup & Run

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 2. Run the app

```bash
python3 main.py
```

### 3. Run it later

```bash
source .venv/bin/activate
python3 main.py
```

## How to Play

1. Choose the number of rounds on the home screen.
2. Click `Start Test`.
3. A sign image appears.
4. Type the matching letter.
5. The app tracks correct answers, wrong answers, skips, and timing.
6. Review your score and missed signs on the results screen.

## Features

- Modernized dark UI with improved home, game, results, and reference screens
- Round selector pills for `10`, `20`, and `30`
- Timed ASL letter recognition gameplay
- Accuracy and speed summary after each run
- Reference gallery for all A-Z signs
- Optional sound effects loaded from `assets/`

## Reference

Click `View All Signs` on the home screen to browse the full A-Z ASL alphabet grid.

## Sound Effects

The app looks for these sound files in `assets/`:

- `button_click.wav`
- `game_start.wav`
- `correct.wav`
- `wrong.wav`
- `skip.wav`
- `game_end.wav`
- `good_grade.wav`
- `failing_grade.wav`

On macOS, the app can fall back to `afplay` if `pygame` audio is unavailable.

## Notes

- The app uses `tkinter` for the GUI and `Pillow` for image handling.
- `__pycache__/` and virtual environment folders are ignored by Git.
- If you are on macOS with Homebrew Python, using a virtual environment is recommended.

## Dependencies

- Python 3.8+
- `tkinter`
- `Pillow`

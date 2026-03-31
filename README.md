# ASL Speed Test

This is a speed test to see how fast you can recongnize ASL letters.

## Project Structure

```
asl-speed-test/
├── assets/ (A–Z)
├── main.py        
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python3 main.py
```

## How to Play

1. **Start** — Choose number of rounds (10 / 20 / 30) and click **Start Test**
2. **See** — A hand sign image appears on screen
3. **Type** — Press the letter key you think it represents
4. **Score** — Correct/wrong tracked in real time with per-round timing
5. **Results** — See accuracy %, average time per round, and which letters you missed

## Improvments

- Make the program more user freindly
- add window adjustment
- add the ability to change color pallete
- add a "TypeRacer" like version of the game
- add camera access and hand sign recognization

## Reference

Click **View All Signs** on the home screen to browse the full A–Z ASL alphabet grid.

## Dependencies

- Python 3.8+
- `tkinter` 
- `Pillow` 

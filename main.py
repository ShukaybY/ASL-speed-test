"""
This is a speed test to see how fast you can recongnize ASL letters.
Author: Shukayb Yezdani
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import random
import time
import os
from PIL import Image, ImageTk

# ─── Config ────────────────────────────────────────────────────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
IMG_SIZE = (260, 260)

ROUNDS_OPTIONS = [10, 20, 30]
DEFAULT_ROUNDS = 10

# ─── Color Palette ─────────────────────────────────────────────────────────────
BG       = "#0d1b2a"
SURFACE  = "#1b2838"
SURFACE2 = "#243447"
ACCENT   = "#2d6a4f"
ACCENT2  = "#52b788"
GREEN    = "#74c69d"
RED      = "#e63946"
YELLOW   = "#f4a261"
TEXT     = "#d8f3dc"
TEXT_DIM = "#74c69d"
WHITE    = "#ffffff"


class ASLSpeedTest(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASL Speed Test")
        self.geometry("620x780")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._load_images()
        self._setup_state()
        self._build_ui()
        self._show_screen("home")

    # ── Image loading ──────────────────────────────────────────────────────────
    def _load_images(self):
        self.sign_images = {}
        for letter in LETTERS:
            path = os.path.join(ASSETS_DIR, f"{letter}.png")
            if os.path.exists(path):
                img = Image.open(path).resize(IMG_SIZE, Image.LANCZOS)
                self.sign_images[letter] = ImageTk.PhotoImage(img)

    # ── State ──────────────────────────────────────────────────────────────────
    def _setup_state(self):
        self.total_rounds    = DEFAULT_ROUNDS
        self.current_round   = 0
        self.score           = 0
        self.wrong           = 0
        self.current_letter  = ""
        self.queue           = []
        self.start_time      = 0.0
        self.round_times     = []
        self.round_results   = []   # list of (letter, guess, correct)
        self._timer_id       = None
        self._feedback_id    = None
        self._elapsed        = 0.0

    # ── UI Build ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.frames = {}

        # ── Home ──────────────────────────────────────────────────────────────
        home = tk.Frame(self, bg=BG)
        self.frames["home"] = home

        tk.Label(home, text="ASL Speed Test", font=("Georgia", 30, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(60, 4))
        tk.Label(home, text="How fast can you read American Sign Language?",
                 font=("Segoe UI", 13), fg=TEXT_DIM, bg=BG).pack(pady=(0, 40))

        # Settings card
        card = tk.Frame(home, bg=SURFACE, padx=30, pady=24)
        card.pack(padx=50, fill="x")
        self._rounded_label(card, "Settings", 13, TEXT_DIM)

        rnd_row = tk.Frame(card, bg=SURFACE)
        rnd_row.pack(fill="x", pady=(12, 0))
        tk.Label(rnd_row, text="Number of rounds", font=("Segoe UI", 12),
                 fg=TEXT, bg=SURFACE).pack(side="left")
        self.rounds_var = tk.IntVar(value=DEFAULT_ROUNDS)
        for n in ROUNDS_OPTIONS:
            tk.Radiobutton(rnd_row, text=str(n), variable=self.rounds_var, value=n,
                           font=("Segoe UI", 12, "bold"), fg=ACCENT2, bg=SURFACE,
                           selectcolor=SURFACE2, activebackground=SURFACE,
                           activeforeground=ACCENT2, relief="flat",
                           command=lambda v=n: self.rounds_var.set(v)).pack(side="left", padx=10)

        self._btn(home, "Start Test", self._start_game, pady=(30, 10))
        self._btn(home, "View All Signs", self._show_reference,
                  color=SURFACE2, pady=(0, 10))

        tk.Label(home, text="Types A–Z  •  Time tracked  •  Accuracy scored",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=BG).pack(pady=(0, 30))

        # ── Game ──────────────────────────────────────────────────────────────
        game = tk.Frame(self, bg=BG)
        self.frames["game"] = game

        # Top bar
        top = tk.Frame(game, bg=BG)
        top.pack(fill="x", padx=30, pady=(20, 0))

        self.lbl_round = tk.Label(top, text="Round 1 / 10", font=("Segoe UI", 12),
                                   fg=TEXT_DIM, bg=BG)
        self.lbl_round.pack(side="left")

        self.lbl_timer = tk.Label(top, text="0.0s", font=("Segoe UI", 13, "bold"),
                                   fg=YELLOW, bg=BG)
        self.lbl_timer.pack(side="right")

        self.lbl_score = tk.Label(top, text="Correct: 0   Wrong: 0", font=("Segoe UI", 12),
                                   fg=TEXT_DIM, bg=BG)
        self.lbl_score.pack(side="right", padx=20)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Purple.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT2,
                        borderwidth=0, thickness=6)
        self.progress_bar = ttk.Progressbar(game, variable=self.progress_var,
                                             maximum=100,
                                             style="Purple.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", padx=30, pady=(8, 0))

        # Image card
        img_card = tk.Frame(game, bg=SURFACE, padx=0, pady=0)
        img_card.pack(padx=30, pady=18)

        self.lbl_image = tk.Label(img_card, bg=SURFACE, bd=0)
        self.lbl_image.pack(padx=20, pady=20)

        # Feedback strip
        self.lbl_feedback = tk.Label(game, text="", font=("Segoe UI", 15, "bold"),
                                      bg=BG, fg=GREEN)
        self.lbl_feedback.pack(pady=(0, 6))

        # Prompt
        tk.Label(game, text="Type the letter you see  →", font=("Segoe UI", 13),
                 fg=TEXT_DIM, bg=BG).pack()

        # Input
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(game, textvariable=self.entry_var,
                              font=("Georgia", 36, "bold"),
                              width=3, justify="center",
                              bg=SURFACE2, fg=ACCENT2, insertbackground=ACCENT2,
                              relief="flat", bd=0)
        self.entry.pack(pady=12, ipady=10)
        self.entry.bind("<KeyRelease>", self._on_key)

        # Skip button
        self._btn(game, "Skip →", self._skip_round,
                  color=SURFACE2, pady=(0, 20), font_size=11)

        # ── Results ───────────────────────────────────────────────────────────
        results = tk.Frame(self, bg=BG)
        self.frames["results"] = results

        tk.Label(results, text="Test Complete!", font=("Georgia", 26, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(4, 20))

        stats_card = tk.Frame(results, bg=SURFACE, padx=30, pady=24)
        stats_card.pack(padx=40, fill="x")

        self.stat_labels = {}
        stat_defs = [
            ("accuracy",    "Accuracy",        ""),
            ("correct",     "Correct",          ""),
            ("wrong",       "Wrong",            ""),
            ("avg_time",    "Avg Time / Round",  ""),
            ("total_time",  "Total Time",       ""),
        ]
        for key, label, _ in stat_defs:
            row = tk.Frame(stats_card, bg=SURFACE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 13), fg=TEXT_DIM,
                     bg=SURFACE, width=22, anchor="w").pack(side="left")
            val_lbl = tk.Label(row, text="", font=("Segoe UI", 13, "bold"),
                               fg=TEXT, bg=SURFACE)
            val_lbl.pack(side="right")
            self.stat_labels[key] = val_lbl

        # Mistakes list
        self.mistakes_frame = tk.Frame(results, bg=BG)
        self.mistakes_frame.pack(padx=40, pady=16, fill="x")

        self._btn(results, "Play Again", self._restart, pady=(0, 8))
        self._btn(results, "Main Menu", lambda: self._show_screen("home"),
                  color=SURFACE2, pady=(0, 30))

        # ── Reference ─────────────────────────────────────────────────────────
        ref = tk.Frame(self, bg=BG)
        self.frames["reference"] = ref

        ref_top = tk.Frame(ref, bg=BG)
        ref_top.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(ref_top, text="ASL Alphabet Reference", font=("Georgia", 20, "bold"),
                 fg=ACCENT2, bg=BG).pack(side="left")
        self._btn(ref_top, "Back", lambda: self._show_screen("home"),
                  color=SURFACE2, pady=0, pack_side="right")

        canvas = tk.Canvas(ref, bg=BG, highlightthickness=0)
        scroll = tk.Scrollbar(ref, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        cols = 4
        for i, letter in enumerate(LETTERS):
            r, c = divmod(i, cols)
            cell = tk.Frame(inner, bg=SURFACE, padx=8, pady=8)
            cell.grid(row=r, column=c, padx=6, pady=6)
            if letter in self.sign_images:
                # Thumbnail
                img = Image.open(os.path.join(ASSETS_DIR, f"{letter}.png"))
                img = img.resize((110, 110), Image.LANCZOS)
                thumb = ImageTk.PhotoImage(img)
                lbl = tk.Label(cell, image=thumb, bg=SURFACE)
                lbl.image = thumb
                lbl.pack()
            tk.Label(cell, text=letter, font=("Georgia", 16, "bold"),
                     fg=ACCENT2, bg=SURFACE).pack()

        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    # ── Helper widgets ─────────────────────────────────────────────────────────
    def _rounded_label(self, parent, text, size, color):
        tk.Label(parent, text=text, font=("Segoe UI", size), fg=color, bg=parent["bg"]).pack(anchor="w")

    def _btn(self, parent, text, cmd, color=ACCENT, pady=(0, 0),
             font_size=13, pack_side=None):
        b = tk.Button(parent, text=text, command=cmd,
                      font=("Helvetica", font_size, "bold"),
                      bg=color, fg=WHITE, activebackground=ACCENT2,
                      activeforeground=WHITE, relief="flat", bd=0,
                      padx=40, pady=14, cursor="hand2",
                      highlightthickness=0, highlightbackground=color)
        if pack_side:
            b.pack(side=pack_side, padx=4)
        else:
            b.pack(pady=pady)
        return b

    # ── Screen management ──────────────────────────────────────────────────────
    def _show_screen(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # ── Game flow ──────────────────────────────────────────────────────────────
    def _start_game(self):
        self._setup_state()
        self.total_rounds = self.rounds_var.get()
        self.queue = random.choices(LETTERS, k=self.total_rounds)
        self._show_screen("game")
        self._next_round()

    def _next_round(self):
        if self.current_round >= self.total_rounds:
            self._show_results()
            return

        self.current_letter = self.queue[self.current_round]
        self.current_round += 1

        # Update UI
        self.lbl_round.config(text=f"Round {self.current_round} / {self.total_rounds}")
        self.lbl_score.config(text=f"Correct: {self.score}   Wrong: {self.wrong}")
        pct = ((self.current_round - 1) / self.total_rounds) * 100
        self.progress_var.set(pct)
        self.lbl_feedback.config(text="")

        if self.current_letter in self.sign_images:
            self.lbl_image.config(image=self.sign_images[self.current_letter])

        self.entry_var.set("")
        self.entry.config(state="normal")
        self.entry.focus_set()

        self.start_time = time.perf_counter()
        self._tick()

    def _tick(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._elapsed = time.perf_counter() - self.start_time
        self.lbl_timer.config(text=f"{self._elapsed:.1f}s")
        self._timer_id = self.after(100, self._tick)

    def _stop_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def _on_key(self, event):
        val = self.entry_var.get().strip().upper()
        if not val:
            return
        if len(val) >= 1 and val[-1].isalpha():
            guess = val[-1]
            self._submit(guess)

    def _submit(self, guess):
        self._stop_timer()
        elapsed = time.perf_counter() - self.start_time
        self.round_times.append(elapsed)

        correct = guess == self.current_letter
        self.round_results.append((self.current_letter, guess, correct))

        if correct:
            self.score += 1
            self.lbl_feedback.config(text=f"Correct!  ({elapsed:.2f}s)", fg=GREEN)
        else:
            self.wrong += 1
            self.lbl_feedback.config(
                text=f"Wrong  —  it was {self.current_letter},  you typed {guess}", fg=RED)

        self.entry.config(state="disabled")
        if self._feedback_id:
            self.after_cancel(self._feedback_id)
        self._feedback_id = self.after(900, self._next_round)

    def _skip_round(self):
        self._stop_timer()
        elapsed = time.perf_counter() - self.start_time
        self.round_times.append(elapsed)
        self.wrong += 1
        self.round_results.append((self.current_letter, "—", False))
        self.lbl_feedback.config(text=f"Skipped  (answer: {self.current_letter})", fg=YELLOW)
        self.entry.config(state="disabled")
        if self._feedback_id:
            self.after_cancel(self._feedback_id)
        self._feedback_id = self.after(800, self._next_round)

    def _restart(self):
        self._show_screen("home")

    # ── Results ────────────────────────────────────────────────────────────────
    def _show_results(self):
        self._stop_timer()
        total_time = sum(self.round_times)
        avg_time   = total_time / len(self.round_times) if self.round_times else 0
        accuracy   = (self.score / self.total_rounds) * 100

        self.stat_labels["accuracy"].config(
            text=f"{accuracy:.1f}%",
            fg=GREEN if accuracy >= 70 else YELLOW if accuracy >= 40 else RED)
        self.stat_labels["correct"].config(text=str(self.score), fg=GREEN)
        self.stat_labels["wrong"].config(text=str(self.wrong), fg=RED)
        self.stat_labels["avg_time"].config(text=f"{avg_time:.2f}s")
        self.stat_labels["total_time"].config(text=f"{total_time:.1f}s")

        # Clear old mistakes
        for w in self.mistakes_frame.winfo_children():
            w.destroy()

        mistakes = [(l, g) for l, g, ok in self.round_results if not ok]
        if mistakes:
            tk.Label(self.mistakes_frame, text="Missed letters:",
                     font=("Segoe UI", 12, "bold"), fg=TEXT_DIM, bg=BG).pack(anchor="w")
            chips = tk.Frame(self.mistakes_frame, bg=BG)
            chips.pack(anchor="w", pady=4)
            for letter, guess in mistakes:
                chip = tk.Frame(chips, bg=SURFACE, padx=8, pady=4)
                chip.pack(side="left", padx=4)
                if guess == "—":
                    txt = f"{letter} (skipped)"
                else:
                    txt = f"{letter} → {guess}"
                tk.Label(chip, text=txt, font=("Segoe UI", 11),
                         fg=RED, bg=SURFACE).pack()

        self._show_screen("results")
        self.progress_var.set(100)

    # ── Reference ─────────────────────────────────────────────────────────────
    def _show_reference(self):
        self._show_screen("reference")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ASLSpeedTest()
    app.mainloop()

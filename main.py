"""
This is a speed test to see how fast you can recongnize ASL letters.
Author: Shukayb Yezdani
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import random
import time
import os
import shutil
import subprocess
from PIL import Image, ImageTk

try:
    import pygame
except ImportError:
    pygame = None

# ─── Config ────────────────────────────────────────────────────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
IMG_SIZE = (260, 260)
APP_SIZE = "900x780"
MIN_SIZE = (720, 680)
CONTENT_MAX = 760

ROUNDS_OPTIONS = [10, 20, 30]
DEFAULT_ROUNDS = 10

# ─── Color Palette ─────────────────────────────────────────────────────────────
BG       = "#212121"
SURFACE  = "#2a2a2a"
SURFACE2 = "#343541"
ACCENT   = "#1f6f43"
ACCENT2  = "#2e8b57"
GREEN    = "#19c37d"
RED      = "#ef4444"
YELLOW   = "#f59e0b"
TEXT     = "#ececec"
TEXT_DIM = "#b4b4b4"
WHITE    = "#ffffff"


class ASLSpeedTest(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASL Speed Test")
        self.geometry(APP_SIZE)
        self.minsize(*MIN_SIZE)
        self.resizable(True, True)
        self.configure(bg=BG)

        self._init_audio()
        self._load_images()
        self._setup_state()
        self._build_ui()
        self._show_screen("home")

    # ── Audio ──────────────────────────────────────────────────────────────────
    def _init_audio(self):
        self.audio_enabled = False
        self.sounds = {}
        self.sound_paths = {}
        self.audio_backend = None

        self._load_sound_paths()

        if pygame is not None:
            try:
                pygame.mixer.init()
                self.audio_enabled = True
                self.audio_backend = "pygame"
                self._load_sounds()
                return
            except Exception:
                pass

        if shutil.which("afplay"):
            self.audio_enabled = True
            self.audio_backend = "afplay"

    def _load_sound_paths(self):
        sound_map = {
            "button_click": "button_click.wav",
            "game_start": "game_start.wav",
            "correct": "correct.wav",
            "wrong": "wrong.wav",
            "skip": "skip.wav",
            "game_end": "game_end.wav",
            "good_grade": "good_grade.wav",
            "failing_grade": "failing_grade.wav",
        }

        for key, filename in sound_map.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                self.sound_paths[key] = path

    def _load_sounds(self):
        for key, path in self.sound_paths.items():
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except Exception:
                continue

    def _play_sound(self, name):
        if not self.audio_enabled:
            return

        if self.audio_backend == "pygame":
            sound = self.sounds.get(name)
            if sound is None:
                return
            try:
                sound.play()
            except Exception:
                pass
            return

        if self.audio_backend == "afplay":
            path = self.sound_paths.get(name)
            if path is None:
                return
            try:
                subprocess.Popen(
                    ["afplay", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    # ── Image loading ──────────────────────────────────────────────────────────
    def _load_images(self):
        self.sign_images = {}
        for letter in LETTERS:
            path = os.path.join(ASSETS_DIR, f"{letter}.png")
            if os.path.exists(path):
                self.sign_images[letter] = ImageTk.PhotoImage(
                    self._fit_image(path, IMG_SIZE, SURFACE)
                )

    def _fit_image(self, path, size, bg_color):
        img = Image.open(path).convert("RGBA")
        img.thumbnail(size, Image.LANCZOS)

        canvas = Image.new("RGBA", size, bg_color)
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        canvas.paste(img, (x, y), img)
        return canvas

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
        self._build_home_screen()
        self._build_game_screen()
        self._build_results_screen()
        self._build_reference_screen()

    def _build_home_screen(self):
        home = tk.Frame(self, bg=BG)
        self.frames["home"] = home
        content = self._content_frame(home)

        tk.Label(content, text="ASL Speed Test", font=("Georgia", 30, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(60, 4))
        tk.Label(content, text="How fast can you read American Sign Language?",
                 font=("Segoe UI", 13), fg=TEXT_DIM, bg=BG).pack(pady=(0, 40))

        # Settings card
        card = tk.Frame(content, bg=SURFACE, padx=30, pady=24)
        card.pack(fill="x")
        self._rounded_label(card, "Settings", 13, TEXT_DIM)

        rnd_row = tk.Frame(card, bg=SURFACE)
        rnd_row.pack(fill="x", pady=(12, 0))
        tk.Label(rnd_row, text="Number of rounds", font=("Segoe UI", 12),
                 fg=TEXT, bg=SURFACE).pack(side="left")
        self.rounds_var = tk.IntVar(value=DEFAULT_ROUNDS)
        self.round_buttons = {}
        for n in ROUNDS_OPTIONS:
            btn = tk.Button(
                rnd_row,
                text=str(n),
                command=lambda v=n: self._set_rounds(v),
                font=("Segoe UI", 11, "bold"),
                bg=SURFACE2,
                fg=TEXT_DIM,
                activebackground=ACCENT2,
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                padx=18,
                pady=8,
                cursor="hand2",
                highlightthickness=0,
            )
            btn.pack(side="left", padx=10)
            self._add_pill_interactions(btn)
            self.round_buttons[n] = btn
        self._refresh_round_buttons()

        self._btn(content, "Start Test", self._start_game, pady=(30, 10))
        self._btn(content, "View All Signs", self._show_reference,
                  color=SURFACE2, pady=(0, 10))

        tk.Label(content, text="Types A–Z  •  Time tracked  •  Accuracy scored",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=BG).pack(pady=(0, 30))

    def _build_game_screen(self):
        game = tk.Frame(self, bg=BG)
        self.frames["game"] = game
        content = self._content_frame(game, pady=20)

        # Status card
        status_card = tk.Frame(content, bg=SURFACE, padx=24, pady=18)
        status_card.pack(fill="x")

        status_top = tk.Frame(status_card, bg=SURFACE)
        status_top.pack(fill="x")

        self.lbl_round = tk.Label(status_top, text="Round 1 / 10", font=("Segoe UI", 12, "bold"),
                                   fg=TEXT, bg=SURFACE)
        self.lbl_round.pack(side="left")

        self.lbl_timer = tk.Label(status_top, text="0.0s", font=("Segoe UI", 13, "bold"),
                                   fg=YELLOW, bg=SURFACE)
        self.lbl_timer.pack(side="right")

        self.lbl_score = tk.Label(status_top, text="Correct: 0   Wrong: 0", font=("Segoe UI", 11),
                                   fg=TEXT_DIM, bg=SURFACE)
        self.lbl_score.pack(side="right", padx=18)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Game.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT2,
                        borderwidth=0, thickness=10)
        self.progress_bar = ttk.Progressbar(game, variable=self.progress_var,
                                             maximum=100,
                                             style="Game.Horizontal.TProgressbar")
        self.progress_bar.pack(in_=status_card, fill="x", pady=(14, 0))

        # Image card
        img_card = tk.Frame(content, bg=SURFACE, padx=28, pady=24)
        img_card.pack(fill="x", pady=18)

        tk.Label(img_card, text="Read this sign", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=SURFACE).pack()
        tk.Label(img_card, text="Type the matching letter as fast as you can",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=SURFACE).pack(pady=(4, 16))

        image_shell = tk.Frame(img_card, bg=SURFACE2, padx=18, pady=18)
        image_shell.pack()

        self.lbl_image = tk.Label(image_shell, bg=SURFACE2, bd=0)
        self.lbl_image.pack()

        # Feedback strip
        feedback_card = tk.Frame(content, bg=BG)
        feedback_card.pack(fill="x", pady=(0, 12))

        self.lbl_feedback = tk.Label(feedback_card, text="", font=("Segoe UI", 13, "bold"),
                                      bg=BG, fg=GREEN)
        self.lbl_feedback.pack()

        # Answer card
        answer_card = tk.Frame(content, bg=SURFACE, padx=24, pady=22)
        answer_card.pack(fill="x")

        tk.Label(answer_card, text="Your answer", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=SURFACE).pack()
        tk.Label(answer_card, text="Press the key for the letter shown above",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=SURFACE).pack(pady=(4, 14))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(answer_card, textvariable=self.entry_var,
                              font=("Georgia", 36, "bold"),
                              width=3, justify="center",
                              bg=SURFACE2, fg=ACCENT2, insertbackground=ACCENT2,
                              relief="flat", bd=0, highlightthickness=2,
                              highlightbackground=SURFACE2, highlightcolor=ACCENT2)
        self.entry.pack(pady=(0, 14), ipady=10)
        self.entry.bind("<KeyRelease>", self._on_key)

        # Skip button
        action_row = tk.Frame(answer_card, bg=SURFACE)
        action_row.pack()
        self._btn(action_row, "Skip Round", self._skip_round,
                  color=SURFACE2, pady=0, font_size=11)

    def _build_results_screen(self):
        results = tk.Frame(self, bg=BG)
        self.frames["results"] = results
        content = self._content_frame(results, pady=20)

        tk.Label(content, text="Test Complete!", font=("Georgia", 26, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(4, 20))

        stats_card = tk.Frame(content, bg=SURFACE, padx=30, pady=24)
        stats_card.pack(fill="x")

        tk.Label(stats_card, text="Performance Summary", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(stats_card, text="A quick look at your speed and accuracy",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=SURFACE).pack(anchor="w", pady=(4, 18))

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
        mistakes_card = tk.Frame(content, bg=SURFACE, padx=30, pady=24)
        mistakes_card.pack(fill="x", pady=16)

        tk.Label(mistakes_card, text="Review Missed Signs", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(mistakes_card, text="Incorrect answers and skips from this session",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=SURFACE).pack(anchor="w", pady=(4, 16))

        self.mistakes_frame = tk.Frame(mistakes_card, bg=SURFACE)
        self.mistakes_frame.pack(fill="x")

        actions = tk.Frame(content, bg=BG)
        actions.pack(pady=(0, 30))

        self._btn(actions, "Play Again", self._restart, pady=0)
        self._btn(actions, "Main Menu", lambda: self._show_screen("home"),
                  color=SURFACE2, pady=(8, 0))

    def _build_reference_screen(self):
        ref = tk.Frame(self, bg=BG)
        self.frames["reference"] = ref
        ref.grid_rowconfigure(0, weight=1)
        ref.grid_columnconfigure(0, weight=1)

        shell = tk.Frame(ref, bg=BG, padx=20, pady=20)
        shell.grid(row=0, column=0, sticky="nsew")
        shell.grid_rowconfigure(1, weight=1)
        shell.grid_columnconfigure(0, weight=1)

        ref_top = tk.Frame(shell, bg=BG)
        ref_top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(ref_top, text="ASL Alphabet Reference", font=("Georgia", 20, "bold"),
                 fg=ACCENT2, bg=BG).pack(anchor="w")
        tk.Label(ref_top, text="Browse every sign from A to Z in a cleaner study view",
                 font=("Segoe UI", 10), fg=TEXT_DIM, bg=BG).pack(anchor="w", pady=(4, 0))

        controls = tk.Frame(ref_top, bg=BG)
        controls.pack(anchor="e", pady=(8, 0))
        self._btn(controls, "Back", lambda: self._show_screen("home"),
                  color=SURFACE2, pady=0)

        body = tk.Frame(shell, bg=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        gallery_card = tk.Frame(body, bg=SURFACE, padx=18, pady=18)
        gallery_card.grid(row=0, column=0, sticky="nsew")
        gallery_card.grid_rowconfigure(1, weight=1)
        gallery_card.grid_columnconfigure(0, weight=1)

        tk.Label(gallery_card, text="Reference Gallery", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=SURFACE).grid(row=0, column=0, sticky="w")

        canvas_frame = tk.Frame(gallery_card, bg=SURFACE)
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_frame, bg=SURFACE, highlightthickness=0)
        scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")

        inner = tk.Frame(canvas, bg=SURFACE)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        cols = 4
        for i, letter in enumerate(LETTERS):
            r, c = divmod(i, cols)
            cell = tk.Frame(inner, bg=SURFACE2, padx=12, pady=12)
            cell.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            tk.Label(cell, text=letter, font=("Segoe UI", 12, "bold"),
                     fg=TEXT, bg=SURFACE2).pack(anchor="w", pady=(0, 8))
            if letter in self.sign_images:
                thumb = ImageTk.PhotoImage(
                    self._fit_image(
                        os.path.join(ASSETS_DIR, f"{letter}.png"),
                        (110, 110),
                        SURFACE2,
                    )
                )
                image_shell = tk.Frame(cell, bg=SURFACE, padx=10, pady=10)
                image_shell.pack()
                lbl = tk.Label(image_shell, image=thumb, bg=SURFACE)
                lbl.image = thumb
                lbl.pack()

        for col in range(cols):
            inner.grid_columnconfigure(col, weight=1)

        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    # ── Helper widgets ─────────────────────────────────────────────────────────
    def _rounded_label(self, parent, text, size, color):
        tk.Label(parent, text=text, font=("Segoe UI", size), fg=color, bg=parent["bg"]).pack(anchor="w")

    def _set_rounds(self, value):
        self.rounds_var.set(value)
        self._refresh_round_buttons()
        self._play_sound("button_click")

    def _refresh_round_buttons(self):
        for value, button in self.round_buttons.items():
            selected = self.rounds_var.get() == value
            button.config(
                bg=ACCENT2 if selected else SURFACE2,
                fg=WHITE if selected else TEXT_DIM,
                activebackground=ACCENT if selected else SURFACE,
                activeforeground=WHITE,
            )

    def _add_pill_interactions(self, button):
        default_pady = 8
        pressed_pady = 10

        def hover_in(_event):
            if button.cget("bg") != ACCENT2:
                button.config(bg=ACCENT, fg=WHITE)

        def hover_out(_event):
            self._refresh_round_buttons()
            button.config(relief="flat", bd=0, pady=default_pady)

        def press_in(_event):
            button.config(relief="sunken", bd=1, pady=pressed_pady)

        def press_out(_event):
            self._refresh_round_buttons()
            button.config(relief="flat", bd=0, pady=default_pady)

        button.bind("<Enter>", hover_in)
        button.bind("<Leave>", hover_out)
        button.bind("<ButtonPress-1>", press_in)
        button.bind("<ButtonRelease-1>", press_out)

    def _content_frame(self, parent, pady=24):
        shell = tk.Frame(parent, bg=BG)
        shell.pack(fill="both", expand=True, padx=24, pady=pady)

        content = tk.Frame(shell, bg=BG)
        content.pack(fill="both", expand=True, padx=48)
        return content

    def _btn(self, parent, text, cmd, color=ACCENT, pady=(0, 0),
             font_size=13, pack_side=None):
        def on_click():
            self._play_sound("button_click")
            cmd()

        b = tk.Button(parent, text=text, command=on_click,
                      font=("Helvetica", font_size, "bold"),
                      bg=color, fg=WHITE, activebackground=ACCENT,
                      activeforeground=WHITE, relief="flat", bd=0,
                      padx=40, pady=14, cursor="hand2",
                      highlightthickness=0, highlightbackground=color)

        default_pady = 14
        pressed_pady = 16
        hover_color = ACCENT2 if color == ACCENT else ACCENT

        def press_in(_event):
            b.config(relief="sunken", bd=1, pady=pressed_pady)

        def press_out(_event):
            b.config(relief="flat", bd=0, pady=default_pady)

        def hover_in(_event):
            b.config(bg=hover_color)

        def hover_out(_event):
            b.config(bg=color)
            press_out(_event)

        b.bind("<Enter>", hover_in)
        b.bind("<Leave>", hover_out)
        b.bind("<ButtonPress-1>", press_in)
        b.bind("<ButtonRelease-1>", press_out)

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
        self._play_sound("game_start")
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
            self._play_sound("correct")
        else:
            self.wrong += 1
            self.lbl_feedback.config(
                text=f"Wrong  —  it was {self.current_letter},  you typed {guess}", fg=RED)
            self._play_sound("wrong")

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
        self._play_sound("skip")
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
        self._play_sound("game_end")
        if accuracy >= 70:
            self._play_sound("good_grade")
        elif accuracy < 40:
            self._play_sound("failing_grade")

        # Clear old mistakes
        for w in self.mistakes_frame.winfo_children():
            w.destroy()

        mistakes = [(l, g) for l, g, ok in self.round_results if not ok]
        if mistakes:
            tk.Label(self.mistakes_frame, text="Missed letters:",
                     font=("Segoe UI", 12, "bold"), fg=TEXT_DIM, bg=SURFACE).pack(anchor="w")
            chips = tk.Frame(self.mistakes_frame, bg=SURFACE)
            chips.pack(anchor="w", pady=4)
            cols = 3
            for i, (letter, guess) in enumerate(mistakes):
                chip = tk.Frame(chips, bg=SURFACE, padx=8, pady=4)
                chip.grid(row=i // cols, column=i % cols, padx=4, pady=4, sticky="w")
                if guess == "—":
                    txt = f"{letter} (skipped)"
                else:
                    txt = f"{letter} → {guess}"
                tk.Label(chip, text=txt, font=("Segoe UI", 11),
                         fg=RED, bg=SURFACE).pack()
        else:
            tk.Label(self.mistakes_frame, text="Nice work. No missed signs this round.",
                     font=("Segoe UI", 11), fg=GREEN, bg=SURFACE).pack(anchor="w")

        self._show_screen("results")
        self.progress_var.set(100)

    # ── Reference ─────────────────────────────────────────────────────────────
    def _show_reference(self):
        self._show_screen("reference")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ASLSpeedTest()
    app.mainloop()

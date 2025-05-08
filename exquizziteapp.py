import tkinter as tk
from tkinter import filedialog, simpledialog
import csv
import random
import pygame
import os
import json

class FlashcardApp:
    def __init__(self, master):
        self.master = master
        master.title("Flashcard App")
        master.geometry("1200x500")

        self.settings_file = "settings.json"
        self.default_settings = {
            "last_flashcard_path": "",
            "sound_on": True,
            "theme": "Amber"
        }
        self.settings = self.load_settings()

        self.themes = {
            "CRT Green": {"bg": "#002b00", "fg": "#99ff99", "label_bg": "#003f00", "label_fg": "#80ff80"},
            "Amber": {"bg": "#2b1b00", "fg": "#ffdd99", "label_bg": "#3f2a00", "label_fg": "#ffd280"},
            "Monochrome": {"bg": "#1f1f1f", "fg": "#dcdcdc", "label_bg": "#2e2e2e", "label_fg": "#ffffff"},
            "DOS Blue": {"bg": "#0000aa", "fg": "#ffffff", "label_bg": "#000080", "label_fg": "#c0c0c0"},
            "Matrix": {"bg": "#000000", "fg": "#00ff00", "label_bg": "#001100", "label_fg": "#00cc00"},
            "Cyberpunk": {"bg": "#0f001a", "fg": "#ff00cc", "label_bg": "#1a0033", "label_fg": "#ff66ff"}
        }

        self.current_theme = self.settings.get("theme", "Amber")
        self.font = ("Courier New", 16)
        self.correct = 0
        self.incorrect = 0
        self.start_index = 0
        self.shuffle_mode = True
        self.sound_on = self.settings.get("sound_on", True)

        pygame.mixer.init()

        self.apply_theme()
        self.create_widgets()
        self.bind_keys()

        self.cards = []
        self.remaining_cards = []
        self.current_card = None
        self.showing_answer = False

    def play_sound(self, filename):
        if self.sound_on:
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, filename)
            if os.path.exists(full_path):
                try:
                    sound = pygame.mixer.Sound(full_path)
                    sound.play()
                except Exception as e:
                    print(f"Error playing sound {full_path}: {e}")
            else:
                print(f"File not found: {full_path}")

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.sound_button.config(text=f"Sound: {'ON' if self.sound_on else 'OFF'}")
        self.save_settings()

    def switch_theme(self):
        themes = list(self.themes.keys())
        idx = (themes.index(self.current_theme) + 1) % len(themes)
        self.current_theme = themes[idx]
        self.apply_theme()
        self.update_theme_colors()
        self.save_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self):
        self.settings["sound_on"] = self.sound_on
        self.settings["theme"] = self.current_theme
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def load_last_flashcards(self):
        path = self.settings.get("last_flashcard_path")
        if os.path.exists(path):
            self.load_file(path)
        else:
            print("No valid saved path.")

    def load_file(self, path):
        with open(path, newline='', encoding='utf-8') as file:
            try:
                reader = csv.reader(file, delimiter='\t')
                self.cards = [row for row in reader if len(row) >= 2]
                if not self.cards:
                    raise ValueError("Empty with tab")
            except:
                file.seek(0)
                reader = csv.reader(file, delimiter=',')
                self.cards = [row for row in reader if len(row) >= 2]
        self.settings["last_flashcard_path"] = path
        self.save_settings()
        self.correct = 0
        self.incorrect = 0
        self.update_stats()
        self.prepare_cards()

    def load_flashcards(self):
        file_path = filedialog.askopenfilename(filetypes=[("TSV Files", "*.tsv"), ("CSV Files", "*.csv")])
        if not file_path:
            return
        self.load_file(file_path)

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.master.configure(bg=theme["bg"])
        self.bg = theme["bg"]
        self.fg = theme["fg"]
        self.label_bg = theme["label_bg"]
        self.label_fg = theme["label_fg"]

    def create_widgets(self):
        self.display_frame = tk.Frame(self.master, bg=self.label_bg, bd=3, relief=tk.SUNKEN)
        self.display_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.question_label = tk.Label(
            self.display_frame,
            text="Load a flashcard file to start.",
            wraplength=600,
            font=self.font,
            bg=self.label_bg,
            fg=self.label_fg,
            justify="left"
        )
        self.question_label.pack(padx=10, pady=10, fill="both", expand=True) 

        self.control_frame = tk.Frame(self.master, bg=self.bg)
        self.control_frame.pack(pady=10)

        self.answer_button = tk.Button(self.control_frame, text="Show Answer", command=self.show_answer, state=tk.DISABLED, font=self.font, relief=tk.GROOVE)
        self.answer_button.grid(row=0, column=0, padx=5, pady=5)

        self.next_button = tk.Button(self.control_frame, text="Next", command=self.next_card, state=tk.DISABLED, font=self.font, relief=tk.GROOVE)
        self.next_button.grid(row=0, column=1, padx=5, pady=5)

        self.correct_button = tk.Button(self.control_frame, text="Correct", command=self.mark_correct, state=tk.DISABLED, font=self.font, relief=tk.GROOVE)
        self.correct_button.grid(row=0, column=2, padx=5, pady=5)

        self.incorrect_button = tk.Button(self.control_frame, text="Incorrect", command=self.mark_incorrect, state=tk.DISABLED, font=self.font, relief=tk.GROOVE)
        self.incorrect_button.grid(row=0, column=3, padx=5, pady=5)

        self.secondary_frame = tk.Frame(self.master, bg=self.bg)
        self.secondary_frame.pack(pady=5)

        self.load_button = tk.Button(self.secondary_frame, text="Load Flashcards", command=self.load_flashcards, font=self.font, relief=tk.GROOVE)
        self.load_button.grid(row=0, column=0, padx=5)

        self.last_button = tk.Button(self.secondary_frame, text="Open Last File", command=self.load_last_flashcards, font=self.font, relief=tk.GROOVE)
        self.last_button.grid(row=0, column=1, padx=5)

        self.shuffle_button = tk.Button(self.secondary_frame, text="Shuffle Mode", command=self.set_shuffle_mode, font=self.font, relief=tk.GROOVE)
        self.shuffle_button.grid(row=0, column=2, padx=5)

        self.ordered_button = tk.Button(self.secondary_frame, text="Ordered Mode", command=self.set_ordered_mode, font=self.font, relief=tk.GROOVE)
        self.ordered_button.grid(row=0, column=3, padx=5)

        self.jump_button = tk.Button(self.secondary_frame, text="Jump to Question", command=self.jump_to_question, font=self.font, relief=tk.GROOVE)
        self.jump_button.grid(row=0, column=4, padx=5)

        # New frame for theme and sound buttons
        self.settings_frame = tk.Frame(self.master, bg=self.bg)
        self.settings_frame.pack(pady=5)

        self.theme_button = tk.Button(self.settings_frame, text="Switch Theme", command=self.switch_theme, font=self.font, relief=tk.GROOVE)
        self.theme_button.grid(row=0, column=0, padx=20)

        self.sound_button = tk.Button(self.settings_frame, text=f"Sound: {'ON' if self.sound_on else 'OFF'}", command=self.toggle_sound, font=self.font, relief=tk.GROOVE)
        self.sound_button.grid(row=0, column=1, padx=20)

        self.stats_label = tk.Label(self.master, text="Correct: 0 | Incorrect: 0", font=self.font)
        self.stats_label.pack(pady=10)

        self.progress_label = tk.Label(self.master, text="", font=self.font)
        self.progress_label.pack(pady=5)

        self.update_theme_colors()

    def bind_keys(self):
        self.master.bind('<Return>', lambda event: self.show_answer())
        self.master.bind('<Right>', lambda event: self.mark_correct())
        self.master.bind('<Left>', lambda event: self.mark_incorrect())
        self.master.bind('<space>', lambda event: self.next_card())

    def update_theme_colors(self):
        self.master.configure(bg=self.bg)
        self.display_frame.configure(bg=self.label_bg)
        self.question_label.configure(bg=self.label_bg, fg=self.label_fg)
        widgets = [
            self.answer_button, self.next_button,
            self.correct_button, self.incorrect_button,
            self.load_button, self.last_button,
            self.shuffle_button, self.ordered_button,
            self.jump_button, self.theme_button,
            self.sound_button, self.stats_label,
            self.progress_label
        ]
        for widget in widgets:
            widget.configure(bg=self.bg, fg=self.fg)
        self.control_frame.configure(bg=self.bg)
        self.secondary_frame.configure(bg=self.bg)

    def next_card(self):
        if self.remaining_cards:
            self.current_card = self.remaining_cards.pop(0)
            self.question_label.config(text=self.current_card[0])
            self.showing_answer = False
            self.correct_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.DISABLED)
            self.answer_button.config(state=tk.NORMAL)
            self.update_progress()
        else:
            self.question_label.config(text="Koniec kartičiek!")
            self.answer_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.correct_button.config(state=tk.DISABLED)
            self.incorrect_button.config(state=tk.DISABLED)
            self.play_sound("all_done.wav")

    def mark_correct(self):
        self.correct += 1
        self.update_stats()
        self.play_sound("correct.wav")
        self.next_card()

    def mark_incorrect(self):
        self.incorrect += 1
        self.update_stats()
        self.play_sound("incorrect.wav")
        self.next_card()

    def show_answer(self):
        if self.current_card:
            self.question_label.config(text=self.current_card[1])
            self.showing_answer = True
            self.correct_button.config(state=tk.NORMAL)
            self.incorrect_button.config(state=tk.NORMAL)
            self.answer_button.config(state=tk.DISABLED)

    def update_stats(self):
        self.stats_label.config(text=f"Correct: {self.correct} | Incorrect: {self.incorrect}")

    def update_progress(self):
        total = len(self.cards)
        done = self.correct + self.incorrect
        self.progress_label.config(text=f"Progress: {done} / {total}")

    def prepare_cards(self):
        if self.shuffle_mode:
            self.remaining_cards = self.cards[:]
            random.shuffle(self.remaining_cards)
        else:
            self.remaining_cards = self.cards[self.start_index:]
        self.next_card()
        self.answer_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.correct_button.config(state=tk.DISABLED)
        self.incorrect_button.config(state=tk.DISABLED)

    def set_shuffle_mode(self):
        self.shuffle_mode = True
        self.start_index = 0
        self.prepare_cards()

    def set_ordered_mode(self):
        self.shuffle_mode = False
        try:
            start = simpledialog.askinteger("Začiatočná otázka", "Zadaj číslo otázky, od ktorej chceš začať (1-based):")
            self.start_index = max(0, start - 1) if start else 0
        except:
            self.start_index = 0
        self.prepare_cards()

    def jump_to_question(self):
        if not self.cards:
            return
        try:
            qnum = simpledialog.askinteger("Skok na otázku", "Zadaj číslo otázky (1-based):")
            if qnum and 0 < qnum <= len(self.cards):
                self.remaining_cards = self.cards[qnum - 1:]
                self.next_card()
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()

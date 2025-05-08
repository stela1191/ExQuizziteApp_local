# ExQuizzitApp – Flashcard App for Windows

**ExQuizzitApp** is a retro-styled flashcard application built in Python and compiled as a standalone `.exe` for offline studying.  
It supports `.tsv` and `.csv` flashcard files, plays sound effects, remembers your settings, and includes several retro visual themes.

---

## Included Files

- `ExQuizzitApp.exe` – the main application
- `correct.wav`, `incorrect.wav`, `all_done.wav` – optional sound effects
- `quiz_icon.ico` – optional application icon
- `settings.json` – automatically created and updated when the app runs

---

## How to Use

1. Double-click `ExQuizzitApp.exe` to open the app.
2. Click **“Load Flashcards”** and select a `.tsv` or `.csv` file:
   - Each row must contain two fields: `Question<TAB>Answer` or `Question,Answer`
3. Click **“Show Answer”** to reveal the card's back side.
4. Mark your response as **Correct** or **Incorrect**.
5. Click **“Next”** to proceed to the next flashcard.

---

## Features

- Shuffle mode or ordered question flow
- Jump to a specific question number
- Reload the last opened flashcard file
- Multiple retro-style visual themes (CRT Green, Amber, Matrix, etc.)
- Keyboard shortcuts:
  - `Enter` = Show Answer  
  - `Right Arrow` = Mark Correct  
  - `Left Arrow` = Mark Incorrect  
  - `Space` = Next Card
- Optional sound effects for feedback
- All user preferences saved automatically

---

## Sound Effects

To enable sounds, make sure these files are placed in the same folder as `ExQuizzitApp.exe`:

- `correct.wav`
- `incorrect.wav`
- `all_done.wav`

Files must be in `.wav` format.

---

## Settings File

When you run the application, a file named `settings.json` will be generated. It stores:

- Last opened flashcard file path
- Sound ON/OFF preference
- Currently selected theme

This ensures your preferences are restored each time you launch the app.

---

## Sample Flashcard File

You can create a sample `.csv` file like this:

```csv
What is the capital of France?,Paris
Who wrote Hamlet?,William Shakespeare

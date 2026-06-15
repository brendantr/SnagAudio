# SnagAudio

A lightweight desktop GUI for downloading audio and video from YouTube and other media sites. Built with `customtkinter` and powered by `yt-dlp`.

---

## Features

- Download media as **MP3**, **MP4**, or **both simultaneously**
- Categorize downloads as **Music** or **Spoken** (organized into subfolders)
- Auto-splits files longer than **20 minutes** into segments via `ffmpeg`
- Custom save directory with a built-in folder browser
- Dark-mode UI with a live progress bar and status indicator

---

## Requirements

### System Dependencies

These must be installed and available on your `PATH`:

- **Python 3.10+** (uses `float | None` union type syntax)
- **ffmpeg** — required for MP3 extraction and long-file splitting
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: [ffmpeg.org/download](https://ffmpeg.org/download.html)

### Python Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern dark-mode GUI framework |
| `yt-dlp` | Media downloading engine |

Install via pip:

```bash
pip install customtkinter yt-dlp
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/brendantr/SnagAudio.git
cd SnagAudio
```

### 2. Create and activate a virtual environment

This project was developed using Python's built-in `venv`. The `.venv` directory is excluded from version control via `.gitignore`.

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

> **Note on Python version:** The venv should be created with **Python 3.10 or later** due to the use of the `X | Y` union type syntax (e.g., `float | None`) introduced in PEP 604.

### 3. Install dependencies

```bash
pip install customtkinter yt-dlp
```

### 4. Run the app

```bash
python snag_audio.py
```

---

## Usage

1. Paste a media URL (YouTube, SoundCloud, etc.) into the **Media URL** field
2. Choose a **Save to** directory (defaults to `~/Downloads/SnagAudio`)
3. Select a **Category**: Music or Spoken
4. Select a **Download option**: MP3, MP4, or both
5. Click **Download**

Downloads are saved to:
```
<save_dir>/<Category>/<title_id>/
```

Files longer than 20 minutes are automatically split into 20-minute segments.

---

## Project Structure

```
SnagAudio/
├── snag_audio.py   # Main application
├── .gitignore      # Excludes .venv, __pycache__, etc.
└── README.md
```

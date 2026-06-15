import re
import subprocess
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp

APP_NAME = "Snag Audio"
DEFAULT_DIR = Path.home() / "Downloads" / "SnagAudio"

class SnagAudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")      # "light" or "system"
        ctk.set_default_color_theme("blue")  # "green", "dark-blue", etc.

        self.title(APP_NAME)
        self.geometry("640x360")
        self.resizable(False, False)

        self.download_dir = ctk.StringVar(value=str(DEFAULT_DIR))

        # Header
        header = ctk.CTkLabel(self, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(15, 5))

        # Main frame
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # URL
        url_label = ctk.CTkLabel(frame, text="Media URL:")
        url_label.grid(row=0, column=0, sticky="w", padx=8, pady=(10, 5))

        self.url_entry = ctk.CTkEntry(frame, width=420, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=8, pady=(10, 5))

        # Directory
        dir_label = ctk.CTkLabel(frame, text="Save to:")
        dir_label.grid(row=1, column=0, sticky="w", padx=8, pady=5)

        self.dir_entry = ctk.CTkEntry(frame, width=350, textvariable=self.download_dir)
        self.dir_entry.grid(row=1, column=1, padx=8, pady=5, sticky="we")

        browse_btn = ctk.CTkButton(frame, text="Browse…", width=80, command=self.choose_dir)
        browse_btn.grid(row=1, column=2, padx=8, pady=5)

        # Category
        category_label = ctk.CTkLabel(frame, text="Category:")
        category_label.grid(row=2, column=0, sticky="w", padx=8, pady=5)

        self.category_music_var = ctk.BooleanVar(value=True)
        self.category_spoken_var = ctk.BooleanVar(value=False)

        self.category_music_check = ctk.CTkCheckBox(
            frame,
            text="Music",
            variable=self.category_music_var,
            command=self.on_music_selected,
        )
        self.category_music_check.grid(row=2, column=1, sticky="w", padx=8, pady=2)

        self.category_spoken_check = ctk.CTkCheckBox(
            frame,
            text="Spoken",
            variable=self.category_spoken_var,
            command=self.on_spoken_selected,
        )
        self.category_spoken_check.grid(row=2, column=2, sticky="w", padx=8, pady=2)

        # Format
        format_label = ctk.CTkLabel(frame, text="Download options:")
        format_label.grid(row=3, column=0, sticky="w", padx=8, pady=5)

        self.mp3_var = ctk.BooleanVar(value=True)
        self.mp4_var = ctk.BooleanVar(value=False)

        self.mp3_check = ctk.CTkCheckBox(frame, text="MP3", variable=self.mp3_var, command=self.update_button_text)
        self.mp3_check.grid(row=4, column=1, sticky="w", padx=8, pady=5)

        self.mp4_check = ctk.CTkCheckBox(frame, text="MP4", variable=self.mp4_var, command=self.update_button_text)
        self.mp4_check.grid(row=4, column=2, sticky="w", padx=8, pady=5)

        # Progress + status
        self.progress = ctk.CTkProgressBar(frame)
        self.progress.grid(row=5, column=0, columnspan=3, sticky="we", padx=8, pady=(15, 5))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(frame, text="Idle")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 10))

        # Download button
        self.download_button = ctk.CTkButton(frame, text="Download MP3", command=self.on_download, width=200)
        self.download_button.grid(row=7, column=0, columnspan=3, pady=(0, 15))

        frame.columnconfigure(1, weight=1)

    def choose_dir(self):
        folder = filedialog.askdirectory(initialdir=self.download_dir.get())
        if folder:
            self.download_dir.set(folder)

    def update_button_text(self):
        mp3 = self.mp3_var.get()
        mp4 = self.mp4_var.get()
        if mp3 and mp4:
            text = "Download MP3 + MP4"
        elif mp4:
            text = "Download MP4"
        else:
            text = "Download MP3"
        self.download_button.configure(text=text)

    def on_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, "Please enter a URL.")
            return

        if not (self.mp3_var.get() or self.mp4_var.get()):
            messagebox.showwarning(APP_NAME, "Please select MP3, MP4, or both.")
            return

        out_dir = Path(self.download_dir.get())
        out_dir.mkdir(parents=True, exist_ok=True)

        t = threading.Thread(target=self.download_thread, args=(url, out_dir), daemon=True)
        t.start()

    def download_thread(self, url: str, out_dir: Path):
        self.set_status("Downloading…")
        self.set_button_enabled(False)
        self.progress.set(0.1)

        try:
            def hook(d):
                if d.get("total_bytes") or d.get("total_bytes_estimate"):
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    downloaded = d.get("downloaded_bytes", 0)
                    frac = max(0.0, min(1.0, downloaded / total))
                    self.progress.set(frac)

            mp3 = self.mp3_var.get()
            mp4 = self.mp4_var.get()

            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(url, download=False)

            categories = self.get_selected_categories()
            download_folder = out_dir / self.make_download_folder(info, categories)
            download_folder.mkdir(parents=True, exist_ok=True)

            ydl_opts = {
                "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
                "progress_hooks": [hook],
            }

            if mp3 and not mp4:
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                    }],
                })
            elif mp4 and not mp3:
                ydl_opts.update({
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                })
            else:
                ydl_opts.update({
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                        "keepvideo": True,
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                filename = Path(ydl.prepare_filename(info))
                ydl.download([url])

            if self.mp3_var.get():
                mp3_path = filename.with_suffix(".mp3")
                self.split_if_long(mp3_path)
            if self.mp4_var.get():
                mp4_path = filename.with_suffix(".mp4")
                self.split_if_long(mp4_path)

            self.progress.set(1.0)
            self.set_status("Done")
            messagebox.showinfo(APP_NAME, f"Download finished.\nSaved in:\n{download_folder}")
        except Exception as e:
            self.set_status("Error")
            self.progress.set(0)
            messagebox.showerror(APP_NAME, f"Download failed:\n{e}")
        finally:
            self.set_button_enabled(True)

    def sanitize_folder_name(self, name: str) -> str:
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", name).strip()
        return safe_name[:100] if safe_name else "download"

    def on_music_selected(self):
        if self.category_music_var.get():
            self.category_spoken_var.set(False)
        else:
            self.category_music_var.set(True)

    def on_spoken_selected(self):
        if self.category_spoken_var.get():
            self.category_music_var.set(False)
        else:
            self.category_spoken_var.set(True)

    def get_selected_categories(self) -> list[str]:
        if self.category_spoken_var.get():
            return ["Spoken"]
        return ["Music"]

    def make_download_folder(self, info: dict, categories: list[str]) -> Path:
        safe_category = self.sanitize_folder_name(categories[0])
        title = info.get("title", "download")
        safe_title = self.sanitize_folder_name(title)
        if info.get("id"):
            folder_name = f"{safe_title}_{info.get('id')}"
        else:
            folder_name = safe_title
        return Path(safe_category) / folder_name

    def split_if_long(self, file_path: Path, segment_seconds: int = 20 * 60):
        if not file_path.exists():
            return

        duration = self.get_media_duration(file_path)
        if duration is None or duration <= segment_seconds:
            return

        output_template = str(file_path.with_stem(f"{file_path.stem}_%d"))
        try:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-i",
                str(file_path),
                "-c",
                "copy",
                "-f",
                "segment",
                "-segment_time",
                str(segment_seconds),
                "-reset_timestamps",
                "1",
                "-segment_start_number",
                "1",
                output_template,
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            file_path.unlink()
        except subprocess.CalledProcessError:
            messagebox.showwarning(APP_NAME, f"Failed to split long file: {file_path.name}")
        except FileNotFoundError:
            messagebox.showwarning(APP_NAME, "ffmpeg is required to split large files but was not found.")

    def get_media_duration(self, file_path: Path) -> float | None:
        try:
            output = subprocess.check_output([
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ], stderr=subprocess.STDOUT, text=True)
            return float(output.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return None

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def set_button_enabled(self, enabled: bool):
        self.download_button.configure(state=("normal" if enabled else "disabled"))


if __name__ == "__main__":
    app = SnagAudioApp()
    app.mainloop()

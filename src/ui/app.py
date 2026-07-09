import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from threading import Thread
import time

from src.config import FONTE_PADRAO, FONTE_TITULO, APP_NAME
from src.ui.theme import Theme
from src.downloader.service import download
from src.diagnostics import diagnosis


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.theme = "light"
        self.last_update_time = 0
        self.setup_window()
        self.create_layout()
        self.create_widgets()
        self.toggle_theme()

    def set_status(self, status):
        self.label_status.delete("1.0", "end")
        self.label_status.insert("1.0", status)

    def setup_window(self):
        self.root.title(APP_NAME)
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.maxsize(1280, 720)
        self.root.minsize(400, 300)

    def create_layout(self):
        self.frame_top = ctk.CTkFrame(self.root, height=100)
        self.frame_top.pack(fill="x")

        self.frame_main = ctk.CTkFrame(self.root)
        self.frame_main.pack(fill="both", expand=True)

        self.frame_log = tk.Frame(self.root, bg="#000000")
        self.frame_log.pack(fill="both", expand=True, pady=5)

    def create_label(self):
        self.label_title = ctk.CTkLabel(
            self.frame_top,
            text="Cole o link do vídeo/playlist do YouTube abaixo 🎬",
            font=FONTE_TITULO,
            text_color=Theme.text_color
        )
        self.label_title.pack(pady=30)

        self.label_status = ctk.CTkTextbox(
            self.frame_log,
            width=700,
            height=150,
            font=FONTE_PADRAO,
            text_color=Theme.text_color
        )
        self.label_status.pack(pady=10, padx=10, fill="both", expand=True)

        self.progress_bar = ctk.CTkProgressBar(self.frame_main)
        self.progress_bar.pack_forget()

        self.progress_text = ctk.CTkLabel(
            self.frame_main,
            text="",
            font=FONTE_PADRAO,
            text_color=Theme.text_color
        )
        self.progress_text.pack_forget()

        self.speed_text = ctk.CTkLabel(
            self.frame_main,
            text="",
            font=FONTE_PADRAO,
            text_color=Theme.text_color
        )
        self.speed_text.pack_forget()

    def show_progress(self):
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=100, fill="x")
        self.progress_text.configure(text="")
        self.speed_text.configure(text="")
        self.progress_text.pack(pady=(5, 0))
        self.speed_text.pack(pady=(2, 10))
        self.last_update_time = 0

    def hide_progress(self):
        self.progress_bar.pack_forget()
        self.progress_text.pack_forget()
        self.speed_text.pack_forget()

    def update_progress(self, pct, now, total, speed, eta):
        def ui():
            current_time = time.time()

            if now is not None and total is not None and total > 0:
                if pct is not None:
                    pct_value = pct
                else:
                    pct_value = int((now / total) * 100)

                self.progress_bar.set(pct_value / 100)
                self.progress_text.configure(
                    text=f"{now} de {total} ({pct_value}%)"
                )

            if speed is not None and (current_time - self.last_update_time) > 1.2:
                self.speed_text.configure(
                    text=f"🚀 {speed} • ETA {eta} ⏳"
                )
                self.last_update_time = current_time

            if pct == 100:
                self.progress_bar.set(1)
                self.speed_text.configure(text="")
                self.progress_text.configure(text="✅ Download Finalizado")
                self.root.after(1500, self.hide_progress)

        self.root.after(0, ui)

    def create_entry(self):
        self.entry_url = ctk.CTkEntry(
            self.frame_main,
            width=400,
            height=40,
            placeholder_text="Cole o link do vídeo ou da playlist do YouTube aqui...",
            font=FONTE_PADRAO
        )
        self.entry_url.pack(pady=20)

    def toggle_theme(self):
        if self.theme == "light":
            ctk.set_appearance_mode("dark")
            self.theme = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.theme = "light"

    def reload(self):
        # Organizar músicas só faz sentido para MP3 (opção 2)
        if self.formato.get() == 2:
            self.organize_locked = False
            self.checkbox_organize.configure(
                state="normal",
                text_color=Theme.text_color
            )
        else:
            self.organizar_bool.set(False)
            self.organize_locked = True
            self.checkbox_organize.configure(
                state="disabled",
                text_color=("gray60", "gray30")
            )

    def block(self):
        if self.organize_locked:
            self.organizar_bool.set(False)

    def create_button(self):
        self.formato = ctk.IntVar(value=1)

        self.video = ctk.CTkRadioButton(
            self.frame_main,
            text="Vídeo (mp4)",
            variable=self.formato,
            value=1,
            font=FONTE_PADRAO,
            command=self.reload
        )
        self.video.pack(pady=10)

        self.audio = ctk.CTkRadioButton(
            self.frame_main,
            text="Áudio (mp3)",
            variable=self.formato,
            value=2,
            font=FONTE_PADRAO,
            command=self.reload
        )
        self.audio.pack(pady=10)

        self.audio_aac = ctk.CTkRadioButton(
            self.frame_main,
            text="Áudio (aac)",
            variable=self.formato,
            value=3,
            font=FONTE_PADRAO,
            command=self.reload
        )
        self.audio_aac.pack(pady=10)

        self.organizar_bool = ctk.BooleanVar(value=False)
        self.checkbox_organize = ctk.CTkCheckBox(
            self.frame_main,
            text="Organizar músicas (apenas mp3)",
            variable=self.organizar_bool,
            onvalue=True,
            offvalue=False,
            font=FONTE_PADRAO,
            command=self.block
        )
        self.checkbox_organize.pack(pady=10)

        self.button_download = ctk.CTkButton(
            self.frame_main,
            text="Baixar ⬇️",
            width=200,
            height=40,
            font=FONTE_PADRAO,
            command=self.start_download
        )
        self.button_download.pack(pady=10)

        self.button_toggle_theme = ctk.CTkButton(
            self.frame_main,
            text="Alternar Tema 🌗",
            width=200,
            height=40,
            font=FONTE_PADRAO,
            command=self.toggle_theme
        )
        self.button_toggle_theme.pack(pady=10)

        self.button_clear_log = ctk.CTkButton(
            self.frame_log,
            text="🧹",
            width=32,
            height=32,
            font=("Segoe UI", 10),
            command=self.clear_log,
            fg_color=("white", "black"),
            text_color=("black", "white"),
            hover_color="#222222",
            corner_radius=8
        )
        self.button_clear_log.place(relx=0.98, rely=0.94, anchor="se")

        self.reload()

    def create_widgets(self):
        self.create_label()
        self.create_entry()
        self.create_button()

    def log(self, msg):
        self.root.after(0, lambda: (
            self.label_status.insert("end", msg + "\n"),
            self.label_status.see("end")
        ))

    def clear_log(self):
        self.label_status.delete("1.0", "end")

    def start_download(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Cole um link do YouTube")
            return

        diagnosis()
        self.button_download.configure(state="disabled")
        self.log("Iniciando download...")
        self.show_progress()

        Thread(
            target=download,
            args=(
                self,
                url,
                self.formato.get(),
                self.organizar_bool.get(),
                self.log,
                self.update_progress
            ),
            daemon=True
        ).start()

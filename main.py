import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from yt_dlp import YoutubeDL
from threading import Thread
from mutagen.easyid3 import EasyID3
import time
import shutil
import sys
import os

# Fontes
FONTE_PADRAO = ("Segoe UI", 10)
FONTE_TITULO = ("Segoe UI", 14, "bold")

# Caminhos para cookies e arquivos de histórico
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = os.path.join(BASE_DIR, 'cookies.txt')

# Pastas de download
HOME = os.path.expanduser("~")
pasta_mp3 = os.path.join(HOME, "Downloads", "Audios_YouTube")
pasta_mp4 = os.path.join(HOME, "Downloads", "Videos_YouTube")
os.makedirs(pasta_mp3, exist_ok=True)
os.makedirs(pasta_mp4, exist_ok=True)

class Config:
    def download(app, url, option, organize, status, progress):
        try:
            # Opções inválidas
            if not url:
                status("❌ Nenhum link informado.")
                return
            if not url.startswith(("http://", "https://")):
                status("❌ Isso não parece um link válido.")
                return
            # Reconhecer quantidade de itens (vídeo ou playlist)
            try:
                app.progress_bar.configure(mode="indeterminate")
                app.progress_bar.start()
                info_opts = {
                    'quiet': True,
                    'ignoreerrors': True,
                    'raise_if_error': False,
                    'cachedir': False,
                    'extractor_retries': 3,
                    'extract_flat': 'in_playlist'
                }
                with YoutubeDL(info_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                if not info:
                    status("❌ URL inválida ou não reconhecida.")
                    return
                app.progress_bar.stop()
                app.progress_bar.configure(mode="determinate")
            except Exception as e:
                status(f"❌ Erro ao acessar vídeo/playlist:")
                status(str(e))
                return

            now = 0
            if 'entries' in info and info['entries']:
                entries = info['entries']
                all = sum(1 for e in entries if e)
            else:
                all = 1

            def progresso_hook(d):
                nonlocal now, all
                # Atualiza progresso para cada vídeo finalizado
                if d["status"] == "finished":
                    info = d.get("info_dict", {})
                    if info.get("_type") != "playlist":
                        now += 1
                        pct = int((now / all) * 100)
                        progress(pct, now, all, None, None)
                # Atualiza velocidade e ETA durante o download
                if d["status"] == "downloading":
                    speed = d.get("speed", 0)
                    eta = d.get("eta", 0)

                    if speed:
                        speed_mb = speed / 1024 / 1024
                        speed_text = f"{speed_mb:.2f} MB/s"
                    else:
                        speed_text = "Calculando..."

                    if eta:
                        mins = eta // 60
                        secs = eta % 60
                        eta_text = f"{mins:02d}:{secs:02d}"
                    else:
                        eta_text = "--:--"

                    progress(None, None, None, speed_text, eta_text)


            # Configurações download
            ydl_opts = {
                # progress
                'progress_hooks': [progresso_hook],

                # logs
                'ignoreerrors': True,
                'raise_if_error': False,
                'skip_unavailable_fragments': True,
                'quiet': True,
                'verbose': True,
                'nocheckcertificate': True,
                'no_warnings': True,

                # rede / estabilidade
                'force_ipv4': True,
                'sleep_interval': 3,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'nocheckcertificate': True,

                # opções avançadas do nodeJS (para vídeos com player complexo)
                'js_runtimes': {
                    'node': {
                        'cmd': 'node'
                    }
                },

                # headers
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                },

                # extratores
                'extractor_args': {
                    'youtube': {
                        'skip': ['private', 'deleted', 'copyright'],
                        'player_client': [
                            'android',
                            'tv',
                            'web_embedded',
                            'ios'
                        ]
                    }
                }
            }

            # Cookies (se existirem)
            if os.path.exists(COOKIE_PATH):
                ydl_opts['cookiefile'] = COOKIE_PATH
                status("🍪 cookies.txt carregado (Modo Privado)")
            else:
                status("❌ cookies.txt não encontrado (Modo Público).")

            # Vídeo MP4:
            if option == 1:
                ydl_opts.update({
                    # Historico de downloads mp4
                    'download_archive': 'downloaded_video.txt',
                    # Forçar vídeo MP4 + áudio M4A (100% compatíveis)
                    'format': '(bv*[ext=mp4]/bv*)+(ba[ext=m4a]/ba)/b',
                    # Garante merge final em MP4
                    'merge_output_format': 'mp4',
                    # Não extrair áudio
                    'outtmpl': (
                        os.path.join(
                            pasta_mp4,
                            '%(playlist_title|single)s',
                            '%(title)s[%(channel|uploader|creator)s][%(id)s].%(ext)s'
                        )
                    ),
                })

            # Áudio MP3
            else:
                ydl_opts.update({
                    # Historico de downloads mp3
                    'download_archive': 'downloaded_audio.txt',
                    # Melhor áudio disponível
                    'format': 'bestaudio/best',
                    # Converter para MP3 usando FFmpeg
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    # Organização de arquivos por playlist/canal
                    'outtmpl': (
                        os.path.join(
                            pasta_mp3,
                            '%(playlist_title|single)s',
                            '%(channel|uploader|creator)s - %(title)s[%(id)s].%(ext)s'
                        )
                    ),
                })

            # Download
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                status("✅ Download finalizado.")
                progress(100, all, all, None, None)
            except Exception as e:
                status("❌ Erro durante o download:")
                status(str(e))
                app.button_download.configure(state="normal")

            # 🎵 Organização automática
            if option == 2 and organize:
                Config.organize(status)
            pass
        finally:
            app.button_download.configure(state="normal")


    def organize(status):
        status("🎶 Organizando músicas...")

        for raiz, _, arquivos in os.walk(pasta_mp3):
            for arquivo in arquivos:
                if not arquivo.lower().endswith(".mp3"):
                    continue

                caminho = os.path.join(raiz, arquivo)

                try:
                    audio = EasyID3(caminho)
                    artista = audio.get("artist", ["Desconhecido"])[0]
                    titulo = audio.get("title", ["Sem título"])[0]

                    if artista.lower() in titulo.lower():
                        novo_nome = f"{titulo}.mp3"
                    else:
                        novo_nome = f"{artista} - {titulo}.mp3"

                    novo_caminho = os.path.join(raiz, novo_nome)

                    if not os.path.exists(novo_caminho):
                        os.rename(caminho, novo_caminho)
                        status(f"✅ {novo_nome}")
                    else:
                        status(f"⚠️ Já existe: {novo_nome}")

                except Exception as e:
                    status(f"❌ Erro em {arquivo}: {e}")
    
    def diagnosis():
        print("🔎 Diagnóstico do ambiente:")

        print(f"• Python: {sys.version.split()[0]}")

        if shutil.which("ffmpeg"):
            print("• FFmpeg: OK")
        else:
            print("❌ FFmpeg: NÃO encontrado")

        if shutil.which("node"):
            print("• Node.js: OK")
        else:
            print("❌ Node.js: NÃO encontrado")

        try:
            import yt_dlp
            print(f"• yt-dlp: OK ({yt_dlp.version.__version__})")
        except Exception as e:
            print(f"❌ yt-dlp: erro ({e})")

class Theme:
    text_color = ("black", "white")

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
        self.root.title("YouTube Downloader")
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
        ).pack(pady=30)
        
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

            # progresso
            if now is not None and total is not None and total > 0:
                if pct is not None:
                    pct_value = pct
                else:
                    pct_value = int((now / total) * 100)

                self.progress_bar.set(pct_value / 100)
                self.progress_text.configure(
                    text=f"{now} de {total} ({pct_value}%)"
                )

            # velocidade
            if speed is not None and (current_time - self.last_update_time) > 1.2:
                self.speed_text.configure(
                    text=f"🚀 {speed} • ETA {eta} ⏳"
                )
                self.last_update_time = current_time

            # finalizar
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
        #troca de tema
        if self.theme == "light":
            ctk.set_appearance_mode("dark")
            self.theme = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.theme = "light"

    def reload(self):
        if self.formato.get() == 1:
            self.organizar_bool.set(False)
            self.organize_locked = True
            self.checkbox_organize.configure(
                state="disabled",
                text_color=("gray60", "gray30")
            )
        else:
            self.organize_locked = False
            self.checkbox_organize.configure(
                state="normal",
                text_color=Theme.text_color
            )

    def block(self):
        if self.organize_locked:
            self.organizar_bool.set(False)

    def create_button(self):
        # Tipo selecionado
        self.formato = ctk.IntVar(value=1)

        # mp4
        self.video = ctk.CTkRadioButton(
            self.frame_main,
            text="Vídeo (mp4)",
            variable=self.formato,
            value=1,
            font=FONTE_PADRAO,
            command=self.reload
        )
        self.video.pack(pady=10)

        # mp3
        self.audio = ctk.CTkRadioButton(
            self.frame_main,
            text="Áudio (mp3)",
            variable=self.formato,
            value=2,
            font=FONTE_PADRAO,
            command=self.reload
        )
        self.audio.pack(pady=10)

        # Checkbox organizar
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
        
        # Button Baixar
        self.button_download = ctk.CTkButton(
            self.frame_main,
            text="Baixar ⬇️",
            width=200,
            height=40,
            font=FONTE_PADRAO,
            command=self.start_download
        )
        self.button_download.pack(pady=10)

        # Button Alternar Tema
        self.button_toggle_theme = ctk.CTkButton(
            self.frame_main,
            text="Alternar Tema 🌗",
            width=200,
            height=40,
            font=FONTE_PADRAO,
            command=self.toggle_theme
        )
        self.button_toggle_theme.pack(pady=10)

        # Button limpar log
        self.button_clear_log = ctk.CTkButton(
            self.frame_log,
            text="🧹",
            width=32,
            height=32,
            font=("Segoe UI", 10),
            command=self.clear_log,
            fg_color=("white", "black"),   # light / dark
            text_color=("black", "white"), # light / dark
            hover_color="#222222",   # leve efeito ao passar mouse
            corner_radius=8
        )

        self.button_clear_log.place(relx=0.98, rely=0.94, anchor="se")

        # Configurações iniciais
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
        Config.diagnosis()
        Config.sync_archive(self.log)
        self.button_download.configure(state="disabled")
        self.log("Iniciando download...")
        self.show_progress()
        Thread(
            target=Config.download,
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
    
# Janela
root = ctk.CTk()
YouTubeDownloaderApp(root)
root.mainloop()
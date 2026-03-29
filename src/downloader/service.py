from yt_dlp import YoutubeDL
from src.validators import validar_url
from src.downloader.options import (
    get_base_options,
    get_video_options,
    get_audio_options
)
from src.downloader.hooks import create_progress_hook
from src.organizer.music import organize

def download(app, url, option, organize_files, status, progress):
    try:
        valido, erro = validar_url(url)
        if not valido:
            status(erro)
            return

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
            status("❌ Erro ao acessar vídeo/playlist:")
            status(str(e))
            return

        if 'entries' in info and info['entries']:
            entries = info['entries']
            total = sum(1 for e in entries if e)
        else:
            total = 1

        total_ref = {"current": 0, "total": total}
        progresso_hook = create_progress_hook(progress, total_ref)

        ydl_opts = get_base_options(progresso_hook, status)

        if option == 1:
            ydl_opts = get_video_options(ydl_opts)
        else:
            ydl_opts = get_audio_options(ydl_opts)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            status("✅ Download finalizado.")
            progress(100, total, total, None, None)

        except Exception as e:
            status("❌ Erro durante o download:")
            status(str(e))
            return

        if option == 2 and organize_files:
            organize(status)

    finally:
        app.button_download.configure(state="normal")
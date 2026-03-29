import os
from src.paths import COOKIE_PATH, PASTA_MP3, PASTA_MP4

def get_base_options(progresso_hook, status):
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
    if os.path.exists(COOKIE_PATH):
        ydl_opts['cookiefile'] = COOKIE_PATH
        status("🍪 cookies.txt carregado (Modo Privado)")
    else:
        status("❌ cookies.txt não encontrado (Modo Público).")

    return ydl_opts

# Opções para baixar apenas o video
def get_video_options(ydl_opts):
    ydl_opts.update({
        'download_archive': 'downloaded_video.txt',
        'format': '(bv*[ext=mp4]/bv*)+(ba[ext=m4a]/ba)/b',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(
            PASTA_MP4,
            '%(playlist_title|single)s',
            '%(title)s[%(channel|uploader|creator)s][%(id)s].%(ext)s'
        ),
    })
    return ydl_opts

# Opções para baixar apenas o audio
def get_audio_options(ydl_opts):
    ydl_opts.update({
        'download_archive': 'downloaded_audio.txt',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(
            PASTA_MP3,
            '%(playlist_title|single)s',
            '%(channel|uploader|creator)s - %(title)s[%(id)s].%(ext)s'
        ),
    })
    return ydl_opts
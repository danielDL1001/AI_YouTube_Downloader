import sys
import sys
import shutil

def diagnosis():
    print("🔎 Diagnóstico do ambiente:")
    print(f"• Python: {sys.version.split()[0]}") # Python 3.10+ recomendado

    if shutil.which("ffmpeg"): # Verifica se o FFmpeg está disponível no PATH
        print("• FFmpeg: OK")
    else:
        print("❌ FFmpeg: NÃO encontrado")

    if shutil.which("node"): # Verifica se o Node.js está disponível no PATH
        print("• Node.js: OK")
    else:
        print("❌ Node.js: NÃO encontrado")

    try: # Verifica se o yt-dlp está instalado e acessível
        import yt_dlp
        print(f"• yt-dlp: OK ({yt_dlp.version.__version__})")
    except Exception as e:
        print(f"❌ yt-dlp: erro ({e})")
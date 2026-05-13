import os

# Diretórios base e do usuário
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")

# Caminhos para cookies
COOKIE_PATH = os.path.join(BASE_DIR, "cookies.txt")

# Arquivos de histórico
PASTA_MP3 = os.path.join(HOME, "Downloads", "Audios_YouTube")
PASTA_MP4 = os.path.join(HOME, "Downloads", "Videos_YouTube")

# Pastas de download
os.makedirs(PASTA_MP3, exist_ok=True)
os.makedirs(PASTA_MP4, exist_ok=True)
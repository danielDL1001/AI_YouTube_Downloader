import os
from mutagen.easyid3 import EasyID3
from src.paths import PASTA_MP3

def organize(status):
    status("🎶 Organizando músicas...")

    for raiz, _, arquivos in os.walk(PASTA_MP3):
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
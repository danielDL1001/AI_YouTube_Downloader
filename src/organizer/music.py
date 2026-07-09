import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from src.paths import PASTA_MP3

# Caracteres inválidos para nomes de arquivo (Windows/Linux/Mac)
CARACTERES_INVALIDOS = r'[\\/:*?"<>|]'


def sanitizar(nome):
    if not nome:
        return ""
    nome = re.sub(CARACTERES_INVALIDOS, "", nome)
    return nome.strip()


def extrair_de_tags(caminho):
    """Tenta ler artista/título das tags ID3. Retorna (artista, titulo) ou None se não houver tag útil."""
    try:
        audio = EasyID3(caminho)
    except ID3NoHeaderError:
        return None
    except Exception:
        return None

    artista = audio.get("artist", [None])[0]
    titulo = audio.get("title", [None])[0]

    if not artista or not titulo:
        return None

    return artista, titulo


def extrair_do_nome_arquivo(nome_arquivo):
    """
    Fallback quando não há tag ID3 (caso mais comum em downloads do YouTube).
    Usa o próprio nome do arquivo, que já vem no formato
    'Uploader - Titulo[id].mp3' definido no outtmpl do yt-dlp.
    """
    base = os.path.splitext(nome_arquivo)[0]
    base = re.sub(r'\[[^\]]*\]\s*$', '', base).strip()  # remove o [id] do final

    if " - " in base:
        artista, titulo = base.split(" - ", 1)
    else:
        artista, titulo = "Desconhecido", base

    return artista.strip(), titulo.strip()


def organize(status):
    status("🎶 Organizando músicas...")

    total = 0
    sucesso = 0
    erros = 0

    for raiz, _, arquivos in os.walk(PASTA_MP3):
        for arquivo in arquivos:
            if not arquivo.lower().endswith(".mp3"):
                continue

            total += 1
            caminho = os.path.join(raiz, arquivo)

            try:
                dados = extrair_de_tags(caminho)
                if dados is None:
                    dados = extrair_do_nome_arquivo(arquivo)

                artista, titulo = dados
                artista = sanitizar(artista) or "Desconhecido"
                titulo = sanitizar(titulo) or "Sem título"

                if artista.lower() in titulo.lower():
                    novo_nome = f"{titulo}.mp3"
                else:
                    novo_nome = f"{artista} - {titulo}.mp3"

                novo_caminho = os.path.join(raiz, novo_nome)

                if os.path.abspath(novo_caminho) == os.path.abspath(caminho):
                    status(f"➡️ Já organizado: {novo_nome}")
                    sucesso += 1
                    continue

                if not os.path.exists(novo_caminho):
                    os.rename(caminho, novo_caminho)
                    status(f"✅ {novo_nome}")
                    sucesso += 1
                else:
                    status(f"⚠️ Já existe: {novo_nome}")

            except Exception as e:
                erros += 1
                status(f"❌ Erro em {arquivo}: {e}")

    status(f"🏁 Concluído: {sucesso}/{total} organizados, {erros} erro(s).")
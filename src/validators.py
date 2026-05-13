def validar_url(url: str) -> tuple[bool, str]:
    if not url:
        return False, "❌ Nenhum link informado."
    if not url.startswith(("http://", "https://")):
        return False, "❌ Isso não parece um link válido."
    return True, ""
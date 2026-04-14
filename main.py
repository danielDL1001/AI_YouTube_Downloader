import customtkinter as ctk # type: ignore
from src.ui.app import YouTubeDownloaderApp

root = ctk.CTk() # Abre a janela principal da aplicação
YouTubeDownloaderApp(root)
root.mainloop() # Fecha a janela principal da aplicação # type: ignore
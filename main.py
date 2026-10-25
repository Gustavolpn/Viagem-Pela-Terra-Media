from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from grafo import Grafo
from interface import Interface


def main():
    pasta = Path(__file__).resolve().parent
    janela = tk.Tk()
    try:
        grafo = Grafo(pasta / "configuracoes" / "grafo.json")
        Interface(janela, grafo, pasta)
    except (OSError, ValueError, KeyError, tk.TclError) as erro:
        messagebox.showerror("Erro ao abrir o mapa", str(erro), parent=janela)
        janela.destroy()
        return
    janela.mainloop()


if __name__ == "__main__":
    main()

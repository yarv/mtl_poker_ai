import tkinter as tk
from poker_game.gui.game_window import GameWindow

if __name__ == "__main__":
    root = tk.Tk()
    game_window = GameWindow(root)
    root.mainloop() 
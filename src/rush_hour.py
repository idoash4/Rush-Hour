import tkinter
from tkinter import ttk
import numpy as np

from src.models.board import Board


class RushHour:
    board: Board

    def __init__(self, board=None):
        self.board = board if board else Board.from_matrix(np.zeros((6, 6), dtype=int))

    def start(self):
        root = tkinter.Tk()
        root.title("Rush Hour")

        style = ttk.Style()
        style.configure('BG.TFrame', background=(200, 200, 170))

        main_frame = ttk.Frame(root, padding=20, height=600, width=600, borderwidth=2, relief="groove")
        main_frame.configure(style="BG.TFrame")
        main_frame.grid()



        root.mainloop()

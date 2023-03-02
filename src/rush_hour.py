import tkinter
from tkinter import filedialog, TOP, LEFT, RIGHT
import numpy as np
from PIL import ImageTk, Image

from src.consts import *
from src.models.board import Board, Vehicle
from src.image_process.board_image import BoardImage


class RushHour:
    board: Board
    board_canvas: tkinter.Canvas
    solution_boards: list[Board]
    current_solution_board_index: int
    text_label: tkinter.Label
    upload_image_button: tkinter.Button
    solve_button: tkinter.Button
    next_button: tkinter.Button
    prev_button: tkinter.Button
    win_image: tkinter.Image

    def __init__(self, board=None):
        self.board = board if board else Board.from_matrix(np.zeros((6, 6), dtype=int))
        self.solution_boards = []
        self.current_solution_board_index = 0

    def start(self):
        root = tkinter.Tk()
        root.title("Rush Hour")

        board_frame = tkinter.Frame(root)
        board_frame.grid()
        self.board_canvas = tkinter.Canvas(board_frame, width=CELL_SIZE * 6, height=CELL_SIZE * 6)
        self.board_canvas.pack(fill='both', expand=True, side='top')
        self.draw_board_lines()
        button_frame = tkinter.Frame(board_frame)
        button_frame.pack(fill='both', expand=True, side='bottom')

        upload_image = Image.open("resources/upload.jpeg")
        upload_image = upload_image.resize((55, 60))
        upload_photo_image = ImageTk.PhotoImage(upload_image)

        solve_image = Image.open("resources/solve.jpeg")
        solve_image = solve_image.resize((40, 60))
        solve_photo_image = ImageTk.PhotoImage(solve_image)

        prev_image = Image.open("resources/prev.jpeg")
        prev_image = prev_image.resize((75, 60))
        prev_photo_image = ImageTk.PhotoImage(prev_image)

        next_image = Image.open("resources/next.jpeg")
        next_image = next_image.resize((75, 60))
        next_photo_image = ImageTk.PhotoImage(next_image)

        self.upload_image_button = tkinter.Button(button_frame, image=upload_photo_image, command=self.upload_image)

        self.solve_button = tkinter.Button(button_frame, image=solve_photo_image, state='disabled', command=self.solve)

        self.prev_button = tkinter.Button(button_frame, image=prev_photo_image, state='disabled', command=self.prev)

        self.next_button = tkinter.Button(button_frame, image=next_photo_image, state='disabled', command=self.next)

        self.text_label = tkinter.Label(button_frame, fg='red', font=('Arial', 20, 'bold'))

        self.upload_image_button.grid(row=0, column=0, columnspan=1)
        self.solve_button.grid(row=0, column=1, columnspan=1)
        self.text_label.grid(row=0, column=2, columnspan=1)
        button_frame.columnconfigure(2, weight=1)
        self.prev_button.grid(row=0, column=3, columnspan=1)
        self.next_button.grid(row=0, column=4, columnspan=1)

        self.win_image = tkinter.PhotoImage(file='resources/win.png')

        if not self.board.is_empty():
            self.draw_board(self.board)
            self.solve_button["state"] = "normal"

        root.mainloop()

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            board_image = BoardImage(file_path)
            self.board = Board.from_matrix(board_image.process(VEHICLES))
            self.text_label["text"] = ""
            self.next_button["state"] = "disabled"
            self.prev_button["state"] = "disabled"
            self.draw_board(self.board)
            self.solve_button["state"] = "normal"

    def solve(self):
        node = self.board.solve()
        self.solution_boards = []
        curr_node = node
        while curr_node:
            self.solution_boards.insert(0, curr_node.board)
            curr_node = curr_node.parent
        self.current_solution_board_index = 0
        self.solve_button["state"] = "disabled"
        if len(self.solution_boards) > 0:
            self.next_button["state"] = "normal"
        else:
            self.text_label["text"] = "No solution"

    def next(self):
        if self.solution_boards and self.current_solution_board_index <= len(self.solution_boards):
            self.current_solution_board_index += 1
            if self.current_solution_board_index == len(self.solution_boards):
                self.next_button["state"] = "disabled"
                self.board_canvas.delete('vehicle')
                self.board_canvas.create_image(200, 200, image=self.win_image, tag='win')
            else:
                self.draw_board(self.solution_boards[self.current_solution_board_index])
            self.prev_button["state"] = "normal"

    def prev(self):
        if self.solution_boards and self.current_solution_board_index > 0:
            self.current_solution_board_index -= 1
            self.draw_board(self.solution_boards[self.current_solution_board_index])
            self.next_button["state"] = "normal"
            self.board_canvas.delete('win')
            if self.current_solution_board_index == 0:
                self.prev_button["state"] = "disabled"

    def draw_board_lines(self):
        xmin, ymin = 0, 0
        xmax = 6 * CELL_SIZE
        ymax = 6 * CELL_SIZE
        for row in range(1, 6):
            y = row * CELL_SIZE
            self.board_canvas.create_line((xmin, y, xmax, y), fill='#969696')
        for column in range(1, 6):
            x = column * CELL_SIZE
            self.board_canvas.create_line((x, ymin, x, ymax), fill='#969696')

    def draw_board(self, board: Board):
        self.board_canvas.delete('vehicle')
        self.board_canvas.delete('win')
        self.draw_vehicles(board.vehicles)

    def draw_vehicles(self, vehicles: tuple[Vehicle]):
        for vehicle in vehicles:
            self.draw_vehicle(vehicle)

    def draw_vehicle(self, vehicle):
        min_row, min_col = map(min, zip(*vehicle.slots))
        max_row, max_col = map(max, zip(*vehicle.slots))
        if min_row == max_row:
            xmin = min_col * CELL_SIZE + MARGIN
            ymin = min_row * CELL_SIZE + MARGIN
            xmax = (max_col + 1) * CELL_SIZE - MARGIN
            ymax = (max_row + 1) * CELL_SIZE - MARGIN
        else:
            xmin = min_col * CELL_SIZE + MARGIN
            ymin = min_row * CELL_SIZE + MARGIN
            xmax = (max_col + 1) * CELL_SIZE - MARGIN
            ymax = (max_row + 1) * CELL_SIZE - MARGIN
        self.board_canvas.create_rectangle((xmin, ymin, xmax, ymax), width=2, fill=VEHICLE_COLORS[vehicle.id], tags='vehicle')

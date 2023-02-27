import tkinter
from tkinter import ttk, filedialog
import numpy as np

from src.models.board import Board
from src.image_process.board_image import BoardImage
from src.image_process.image_vehicle import VehicleImage

CELL_SIZE = 75
MARGIN = CELL_SIZE // 8
VEHICLE_COLORS = {
                  1: '#D62133', #Red
                  2: '#F0F167', #Light Yellow Car
                  3: '#FFA1D8', #Pink Car
                  4: '#007E64', #Green Car
                  5: '#828400', #Olive Green Car
                  6: '#7B5956', #Light Brown Car
                  7: '#B0C6CD', #Gray Car
                  8: '#E6C998', #Beige Car
                  9: '#00BAFD', #Cyan Car
                  10: '#00EABF', #Light Green Car
                  11: '#5162CE', #Purple Car
                  12: '#FF823A', #Orange Car
                  13: '#FAD444', #Sunflower Yellow Trunk
                  14: '#9E94F0', #Light Purple Trunk
                  15: '#0043C8', #Blue Trunk
                  16: '#00B9BA' #Jade Trunk
                  }

vehicles = [VehicleImage(1, "Red Car", 2, (((173, 173, 94), (180, 232, 227)), ((0, 160, 150), (5, 220, 220)))),
            VehicleImage(2, "Light Yellow Car", 2, (((25, 90, 185), (35, 152, 250)),)),
            VehicleImage(3, "Pink Car", 2, (((150, 30, 100), (172, 255, 255)),)),
            VehicleImage(4, "Green Car", 2, (((66, 130, 38), (87, 256, 175)),)),
            VehicleImage(5, "Olive Green Car", 2, (((29, 150, 48), (36, 256, 256)),)),
            VehicleImage(6, "Light Brown Car", 2, (((0, 0, 0), (8, 120, 255)),)),
            VehicleImage(7, "Gray Car", 2, (((85, 20, 120), (105, 60, 255)),)),
            VehicleImage(8, "Beige Car", 2, (((18, 40, 115), (35, 80, 250)),)),
            VehicleImage(9, "Cyan Car", 2, (((95, 125, 160), (103, 180, 255)),)),
            VehicleImage(10, "Light Green Car", 2, (((74, 0, 145), (88, 256, 256)),)),
            VehicleImage(11, "Purple Car", 2, (((110, 90, 140), (120, 140, 255)),)),
            VehicleImage(12, "Orange Car", 2, (((6, 80, 130), (15, 255, 255)),)),
            VehicleImage(13, "Sunflower Yellow Trunk", 3, (((14, 158, 117), (29, 256, 256)),)),
            VehicleImage(14, "Light Purple Trunk", 3, (((120, 50, 120), (142, 145, 240)),)),
            VehicleImage(15, "Blue Trunk", 3, (((107, 160, 48), (114, 255, 210)),)),
            VehicleImage(16, "Jade Trunk", 3, (((86, 107, 70), (94, 225, 209)),))]


class RushHour:
    board: Board
    board_canvas: tkinter.Canvas
    solution: list[Board]
    current_board_index: int
    solve_button: ttk.Button
    next_button: ttk.Button
    prev_button: ttk.Button

    def __init__(self, board=None):
        self.board = board if board else Board.from_matrix(np.zeros((6, 6), dtype=int))
        self.solution = []
        self.current_board_index = 0

    def start(self):
        root = tkinter.Tk()
        root.title("Rush Hour")

        board_frame = tkinter.Frame(root, height=800, width=1600)
        board_frame.grid()
        self.board_canvas = tkinter.Canvas(board_frame, width=CELL_SIZE * 6, height=CELL_SIZE * 6)
        self.board_canvas.pack(fill='both', expand=True, side='top')
        self.draw_board_lines()

        upload_image_button = ttk.Button(board_frame, text="Upload Image", command=self.upload_image)
        upload_image_button.pack()

        self.solve_button = ttk.Button(board_frame, text="Solve Board", command=self.solve, state='disabled')
        self.solve_button.pack()

        self.next_button = ttk.Button(board_frame, text="Next", command=self.next, state='disabled')
        self.next_button.pack()

        self.prev_button = ttk.Button(board_frame, text="Prev", command=self.prev, state='disabled')
        self.prev_button.pack()

        if not self.board.is_empty():
            self.draw_board(self.board)
            self.solve_button["state"] = "normal"

        root.mainloop()

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        board_image = BoardImage(file_path)
        self.board = Board.from_matrix(board_image.process(vehicles))
        self.next_button["state"] = "disabled"
        self.prev_button["state"] = "disabled"
        self.draw_board(self.board)
        self.solve_button["state"] = "normal"

    def solve(self):
        node = self.board.solve()
        self.solution = []
        curr_node = node
        while curr_node:
            self.solution.insert(0, curr_node.board)
            curr_node = curr_node.parent
        self.current_board_index = 0
        self.solve_button["state"] = "disabled"
        self.next_button["state"] = "normal"
        self.prev_button["state"] = "normal"

    def next(self):
        if self.solution:
            self.current_board_index = min(len(self.solution)-1, self.current_board_index+1)
            self.draw_board(self.solution[self.current_board_index])

    def prev(self):
        if self.solution:
            self.current_board_index = max(0, self.current_board_index - 1)
            self.draw_board(self.solution[self.current_board_index])

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
        self.draw_vehicles(board.vehicles)

    def draw_vehicles(self, vehicles: tuple[vehicles]):
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

from src.image_process.image_vehicle import VehicleImage
from src.image_process.board_image import BoardImage
from src.models.board import Board
from rush_hour import RushHour


def main():
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
    board_image_process = BoardImage('../samples4/half_angle3_300.JPG')
    board_matrix = board_image_process.process(vehicles)
    board = Board.from_matrix(board_matrix)
    print(board)
    node = board.solve()
    print(node)
    rh = RushHour()
    rh.start()


if __name__ == '__main__':
    main()

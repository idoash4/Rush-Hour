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
VEHICLES = [VehicleImage(1, "Red Car", 2, (((173, 173, 94), (180, 232, 227)), ((0, 160, 150), (5, 220, 220)))),
            VehicleImage(2, "Light Yellow Car", 2, (((25, 90, 150), (35, 152, 250)),)),
            VehicleImage(3, "Pink Car", 2, (((150, 30, 100), (172, 255, 255)),)),
            VehicleImage(4, "Green Car", 2, (((66, 130, 38), (87, 256, 175)),)),
            VehicleImage(5, "Olive Green Car", 2, (((29, 150, 48), (36, 256, 256)),)),
            VehicleImage(6, "Light Brown Car", 2, (((0, 0, 0), (8, 120, 255)),)),
            VehicleImage(7, "Gray Car", 2, (((85, 0, 120), (105, 60, 255)),)),
            VehicleImage(8, "Beige Car", 2, (((18, 40, 115), (35, 80, 250)),)),
            VehicleImage(9, "Cyan Car", 2, (((95, 125, 160), (103, 180, 255)),)),
            VehicleImage(10, "Light Green Car", 2, (((74, 0, 145), (88, 256, 256)),)),
            VehicleImage(11, "Purple Car", 2, (((110, 90, 140), (120, 140, 255)),)),
            VehicleImage(12, "Orange Car", 2, (((6, 80, 130), (15, 255, 255)),)),
            VehicleImage(13, "Sunflower Yellow Trunk", 3, (((14, 158, 117), (29, 256, 256)),)),
            VehicleImage(14, "Light Purple Trunk", 3, (((120, 50, 120), (142, 145, 240)),)),
            VehicleImage(15, "Blue Trunk", 3, (((107, 160, 48), (114, 255, 210)),)),
            VehicleImage(16, "Jade Trunk", 3, (((86, 107, 70), (94, 225, 209)),))]

from dataclasses import dataclass
import numpy as np
from collections import defaultdict
from collections.abc import Iterator
from .vehicle import Vehicle, VehicleOrientation, MoveDirection
from operator import add, sub

BOARD_SIZE = 6


@dataclass(frozen=True)
class Node:
    board: "Board"
    parent: "Node"
    depth: int


@dataclass(frozen=True)
class Board:
    vehicles: tuple[Vehicle]

    @staticmethod
    def from_matrix(matrix: np.ndarray) -> "Board":
        vehicles_dict = defaultdict(list)
        for row_index, row in enumerate(matrix):
            for col_index, col in enumerate(row):
                if col:
                    vehicles_dict[col].append((row_index, col_index))

        vehicles = [
            Vehicle(
                id=vehicle_id,
                slots=tuple(slots),
                orientation=VehicleOrientation.HORIZONTAL if slots[0][0] == slots[-1][0] else VehicleOrientation.VERTICAL
            ) for vehicle_id, slots in sorted(vehicles_dict.items())]

        return Board(vehicles=tuple(vehicles))

    def is_slot_available(self, row_index, col_index):
        if not (0 <= row_index < BOARD_SIZE and 0 <= col_index < BOARD_SIZE):
            return False
        for vehicle in self.vehicles:
            if (row_index, col_index) in vehicle.slots:
                return False
        return True

    def move_vehicle(self, vehicle_index, direction: MoveDirection):
        vehicles_list = list(self.vehicles)
        vehicles_list[vehicle_index] = vehicles_list[vehicle_index].move(direction)
        return Board(tuple(vehicles_list))

    def get_child_boards(self) -> Iterator["Board"]:
        for vehicle_index, vehicle in enumerate(self.vehicles):
            if vehicle.orientation == VehicleOrientation.VERTICAL:
                move = (1, 0)
            else:
                move = (0, 1)
            # Forward
            if self.is_slot_available(*map(add, vehicle.slots[-1], move)):
                yield self.move_vehicle(vehicle_index, MoveDirection.FORWARD)
            # Backward
            if self.is_slot_available(*map(sub, vehicle.slots[0], move)):
                yield self.move_vehicle(vehicle_index, MoveDirection.BACKWARD)

    def is_complete(self):
        return self.vehicles[0].id == 1 \
            and self.vehicles[0].orientation == VehicleOrientation.HORIZONTAL \
            and self.vehicles[0].slots[-1][1] == BOARD_SIZE - 1

    def solve(self, max_depth=93):
        root = Node(board=self, parent=None, depth=0)
        visited_boards = set()
        queue = [root]
        depth = 0

        while depth <= max_depth:
            node = queue.pop(0)
            depth = node.depth

            if node.board.is_complete():
                return node

            for child_board in node.board.get_child_boards():
                if child_board not in visited_boards:
                    next_node = Node(board=child_board, parent=node, depth=depth + 1)
                    visited_boards.add(child_board)
                    queue.append(next_node)

                    if child_board.is_complete():
                        return next_node

    def __repr__(self):
        matrix = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        for vehicle in self.vehicles:
            for slot in vehicle.slots:
                matrix[slot[0], slot[1]] = vehicle.id
        return str(matrix)

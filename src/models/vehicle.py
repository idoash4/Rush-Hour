from enum import Enum, IntEnum
from dataclasses import dataclass, replace


class VehicleOrientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class MoveDirection(IntEnum):
    FORWARD = 1
    BACKWARD = -1


@dataclass(frozen=True)
class Vehicle:
    id: int
    slots: tuple[tuple[int, int]]
    orientation: VehicleOrientation

    def move(self, direction: MoveDirection) -> "Vehicle":
        slots = map(
            lambda s: (s[0] + direction.value, s[1])
            if self.orientation == VehicleOrientation.VERTICAL
            else (s[0], s[1] + direction.value),
            self.slots
        )
        return replace(self, slots=tuple(slots))

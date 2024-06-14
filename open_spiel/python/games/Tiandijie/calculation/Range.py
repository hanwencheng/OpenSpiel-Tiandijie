from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives import Context
    from primitives.hero.Hero import Hero
    from typing import List

from primitives.hero.HeroBasics import Professions
from math import ceil, floor
from calculation.RangeType import RangeType
from basics import Position


# return the area in the right bottom direction based on the actor point
def calculate_direction_area(
    base_point: Position, current_action_point: Position, length: int, width: int
) -> List[Position]:
    area_map = []
    # in right direction
    if (
        current_action_point[0] - base_point[0] > 0
        and base_point[1] == current_action_point[1]
    ):
        print("in right direction")
        for i in range(length):
            for j in range(width):
                area_map.append(
                    (base_point[0] + i + 1, base_point[1] - floor(width / 2) + j)
                )
    # in left direction
    elif (
        base_point[0] - current_action_point[0] > 0
        and base_point[1] == current_action_point[1]
    ):
        print("in left direction")
        for i in range(length):
            for j in range(ceil(width / 2) + 1):
                area_map.append(
                    (base_point[0] - i - 1, base_point[1] - floor(width / 2) + j)
                )
    # in top direction
    elif (
        base_point[0] == current_action_point[0]
        and base_point[1] - current_action_point[1] > 0
    ):
        print("in top direction")
        for i in range(length):
            for j in range(width):
                area_map.append(
                    (base_point[0] - floor(width / 2) + j, base_point[1] - i - 1)
                )
    # in bottom direction
    elif (
        current_action_point[0] == base_point[0]
        and current_action_point[1] - base_point[1] > 0
    ):
        print("in bottom direction")
        for i in range(length):
            for j in range(width):
                area_map.append(
                    (base_point[0] - floor(width / 2) + j, base_point[1] + i + 1)
                )
    return area_map


def calculate_diamond_area(action_point: Position, range_value: int):
    area_map = []
    for i in range(range_value + 1):
        for j in range(range_value + 1):
            if i + j < range_value + 1:
                if i + j == 0:
                    area_map.append((action_point[0], action_point[1]))
                else:
                    area_map.append((action_point[0] + i, action_point[1] + j))
                    area_map.append((action_point[0] + i, action_point[1] - j))
                    area_map.append((action_point[0] - i, action_point[1] + j))
                    area_map.append((action_point[0] - i, action_point[1] - j))
    return area_map


def calculate_archer_area(action_point: Position, range_value: int):
    area_map = []
    for i in range(range_value + 1):
        for j in range(range_value + 1):
            if 1 < i + j < range_value + 1:
                area_map.append((action_point[0] + i, action_point[1] + j))
                area_map.append((action_point[0] + i, action_point[1] - j))
                area_map.append((action_point[0] - i, action_point[1] + j))
                area_map.append((action_point[0] - i, action_point[1] - j))
    return area_map


def calculate_square_area(action_point: Position, range_value: int):
    area_map = set()
    for i in range(-range_value, range_value + 1):
        for j in range(-range_value, range_value + 1):
            area_map.add((action_point[0] + i, action_point[1] + j))
    return list(area_map)


def calculate_cross_area(action_point, range_value: int):
    area_map = []
    for i in range(range_value + 1):
        if i == 0:
            area_map.append((action_point[0] + i, action_point[1]))
        else:
            area_map.append((action_point[0] + i, action_point[1]))
            area_map.append((action_point[0] - i, action_point[1]))
            area_map.append((action_point[0], action_point[1] + i))
            area_map.append((action_point[0], action_point[1] - i))
    return area_map


class Range:
    def __init__(
        self, range_type: RangeType, range_value: int = 0, length=None, width=None
    ):
        self.range_type = range_type
        self.range_value = range_value
        self.length = length
        self.width = width

    def get_area(
        self, base_position: Position, action_point: Position
    ) -> List[Position]:
        if self.range_type == RangeType.DIRECTIONAL:
            return calculate_direction_area(
                base_position, action_point, self.length, self.width
            )
        elif self.range_type == RangeType.POINT:
            return [action_point]
        elif self.range_type == RangeType.DIAMOND:
            return calculate_diamond_area(base_position, self.range_value)
        elif self.range_type == RangeType.ARCHER:
            return calculate_archer_area(base_position, self.range_value)
        elif self.range_type == RangeType.CROSS:
            return calculate_cross_area(base_position, self.range_value)
        else:
            return calculate_square_area(base_position, self.range_value)

    def check_if_target_in_range(
        self, base_position: Position, action_point: Position, target_position: Position
    ) -> bool:
        area_map = self.get_area(base_position, action_point)
        return target_position in area_map


def create_directional_range(length: int, width: int) -> Range:
    return Range(RangeType.DIRECTIONAL, 0, length, width)


def create_point_range() -> Range:
    return Range(RangeType.POINT, 0)


def create_diamond_range(range_value: int) -> Range:
    return Range(RangeType.DIAMOND, range_value)


def create_square_range(range_value: int) -> Range:
    return Range(RangeType.SQUARE, range_value)


def calculate_if_targe_in_diamond_range(
    base_position: Position, target_position: Position, range_value: int
) -> bool:
    return (
        abs(base_position[0] - target_position[0])
        + abs(base_position[1] - target_position[1])
        <= range_value
    )


def check_if_target_in_skill_attack_range(actor: Hero, target: Hero, skill) -> bool:
    return calculate_if_targe_in_diamond_range(
        actor.position, target.position, skill.temp.range_instance.range_value
    )


# class DirectionalRange(Range):
#     def __int__(self, is_directional: True, length, width, start, end):
#         self.range_type = RangeType.DIRECTIONAL
#         self.start = 0
#         self.end = 0
#         self.length = length
#         self.width = width
#
#
# class SelfRange(Range):
#     def __int__(self, is_directional: False, length, width, start, end):
#         self.range_type = RangeType.SELF
#         self.length = 0
#         self.width = 0
#         self.start = start
#         self.end = end

# test calculate_direction_area function
import unittest
from calculation.Range import calculate_direction_area


class TestCalculateDirectionArea(unittest.TestCase):
    def test_calculate_direction_area(self):
        # Sample input attributes and growth coefficients
        actor_point = (0, 0)
        length = 3
        width = 3

        # in the right direction
        current_action_point = (1, 0)
        area_map = calculate_direction_area(
            actor_point, current_action_point, length, width
        )
        self.assertEqual(
            area_map,
            [(1, -1), (1, 0), (1, 1), (2, -1), (2, 0), (2, 1), (3, -1), (3, 0), (3, 1)],
        )

        # in the left direction
        current_action_point = (-1, 0)
        area_map = calculate_direction_area(
            actor_point, current_action_point, length, width
        )
        self.assertEqual(
            area_map,
            [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (-2, -1),
                (-2, 0),
                (-2, 1),
                (-3, -1),
                (-3, 0),
                (-3, 1),
            ],
        )

        # in the bottom direction
        current_action_point = (0, 1)
        area_map = calculate_direction_area(
            actor_point, current_action_point, length, width
        )
        self.assertEqual(
            area_map,
            [(-1, 1), (0, 1), (1, 1), (-1, 2), (0, 2), (1, 2), (-1, 3), (0, 3), (1, 3)],
        )

        # in the top direction
        current_action_point = (0, -1)
        area_map = calculate_direction_area(
            actor_point, current_action_point, length, width
        )
        self.assertEqual(
            area_map,
            [
                (-1, -1),
                (0, -1),
                (1, -1),
                (-1, -2),
                (0, -2),
                (1, -2),
                (-1, -3),
                (0, -3),
                (1, -3),
            ],
        )

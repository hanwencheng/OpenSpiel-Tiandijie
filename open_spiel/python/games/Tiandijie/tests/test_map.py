import unittest

from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import generate_max_level_attributes, a_star_search
from open_spiel.python.games.Tiandijie.primitives.map.BattleMap import BattleMap


class TestMap(unittest.TestCase):
    # set up the test suite with a initial map
    def setUp(self):
        super().setUp()  # This is not strictly necessary for setUp
        self.initial_terrain_map = [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 2, 2, 0],
            [0, 0, 0, 0, 0],
        ]
        self.initial_map = BattleMap(5, 5, self.initial_terrain_map)
        # display the initial map
        self.initial_map.display_map()

    def test_bfs_move_range(self):
        # test the move range of the actor
        actor_point = [2, 2]
        move_range = 3
        self.initial_map.set_map(
            [
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 2, 0],
                [0, 1, 0, 2, 0],
                [0, 0, 0, 0, 0],
            ]
        )
        move_range_map = bfs_move_range(actor_point, move_range, self.initial_map, True)
        self.assertEqual(
            move_range_map,
            {
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 0),
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 0),
                (2, 1),
                (2, 2),
                (2, 3),
                (2, 4),
                (3, 0),
                (3, 1),
                (3, 4),
                (4, 1),
            },
        )

    def test_a_start_search(self):
        # test the shortest path of the actor
        start_point = (2, 2)
        end_point = (4, 4)
        self.initial_map.set_map(
            [
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 2, 0],
                [0, 1, 0, 2, 0],
                [0, 0, 0, 0, 0],
            ]
        )
        shortest_path = a_star_search(start_point, end_point, self.initial_map, False)
        self.assertEqual(shortest_path, [(2, 2), (2, 3), (2, 4), (3, 4), (4, 4)])

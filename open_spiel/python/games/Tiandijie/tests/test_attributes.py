from __future__ import annotations

import unittest
from primitives.hero.Attributes import Attributes
from primitives.hero.Attributes import (
    generate_max_level_attributes,
    multiply_attributes,
)


class TestGenerateMaxLevelAttributes(unittest.TestCase):
    def test_generate_max_level_attributes(self):
        # Sample input attributes and growth coefficients
        level0_attributes = Attributes(166, 20, 23, 81, 34, 66)
        growth_coefficients = (24.96, 3.02, 3.49, 12.08, 5.1, 0.66)

        # Call the function
        added_attributes = generate_max_level_attributes(
            level0_attributes, growth_coefficients, "SORCERER_DAMAGE"
        )
        final_attributes = multiply_attributes(added_attributes, "SORCERER_DAMAGE")

        # Assert that the results are as expected
        self.assertEqual(final_attributes.life, 5808)
        self.assertEqual(final_attributes.attack, 404)
        self.assertEqual(final_attributes.defense, 1042)
        self.assertEqual(final_attributes.magic_attack, 3013)
        self.assertEqual(final_attributes.magic_defense, 1433)
        self.assertEqual(final_attributes.luck, 222)


if __name__ == "__main__":
    unittest.main()

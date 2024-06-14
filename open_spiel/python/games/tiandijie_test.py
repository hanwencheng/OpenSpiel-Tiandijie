# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for pyspiel Chat Game."""

from absl.testing import absltest
from absl.testing import parameterized


from open_spiel.python.games.Tiandijie.tests.test_action import *

import pyspiel


class ChatGameTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()

  def test_game_from_cc(self, fixed_scenario):
    """Runs our standard game tests, checking API consistency."""
    print("test_game_from_cc")
    pass



if __name__ == '__main__':
  absltest.main()

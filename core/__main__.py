import unittest
from unittest.mock import patch

from core.game import Game
from core.player import Player, PlayerType


class TestGameInitialization(unittest.TestCase):
    def setUp(self):
        self.game = Game(player1_type=PlayerType.HUMAN, player2_type=PlayerType.AI)

    @patch('builtins.input', return_value='w')
    def test_start_game_initializes_correctly(self, mock_input):
        """Test that starting the game sets up the correct initial state"""
        # Act - Start the game
        self.game.start_game()

        mock_input.assert_called_once_with('Choose your deck color (wubrg): ')


if __name__ == '__main__':
    unittest.main()
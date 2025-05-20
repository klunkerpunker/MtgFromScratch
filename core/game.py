from random import random

from data.historical_repository import HistoricalRepository
from player import Player, PlayerType
from core.decisions import PlayDrawDecision


class Game:
    def __init__(self,
                 player1_type=PlayerType.HUMAN,
                 player2_type=PlayerType.AI,
                 game_format: str = "sparky"):
        # Players
        self.players = [
            Player("Player 1", player1_type),
            Player("Player 2", player2_type)
        ]
        self.ai_model = None
        self.game_format = game_format
        self.historical = HistoricalRepository()

        self.current_player = self.players[0]
        self.active_player = self.players[0]
        self.turn_phase = "Beginning"

        # Zones
        self.battlefield = []
        self.stack = []
        self.exile = []

        # Game state tracking
        self.turn_count = 1
        self.step = "Untap"
        self.priority = None
        self.losers = []
        self.event_queue = []

        # Turn history
        self.life_changes_this_turn = []
        self.creatures_died_this_turn = []
        self.spells_cast_this_turn = []

    def start_game(self):
        """Initialize a new game"""
        starting_player = random.choice(self.players)
        for player in self.players

    def choose_first_player(self):
        decider = random.choice(self.players)

        if decider.type == PlayerType.HUMAN:
            decision = PlayDrawDecision.human_decision(decider.name)
        else:
            game_state = self._get_play_draw_state()
            decision = PlayDrawDecision.ai_decision(game_state, self.ai_model)

        self._apply_decision(decider, decision)

    def _get_play_draw_state(self, requesting_player):
        my_archetype = requesting_player.deck.achetype
        opponent_archetype = None if self.match_game_number == 1 else self._infer_opponent_archetype()

        win_rates = self.historical.get_win_rates(
            deck_archetype=my_archetype,
            opponent_archetype=opponent_archetype,
            format=self.game_format)

        return {
            "my_archetype": my_archetype,
            "opponent_archetype": opponent_archetype,
            "historical_win_rates": win_rates
        }

    def record_game_result(self, winner):
        """Update stats after game ends"""
        self.historical.update_win_rates(
            deck_archetype=self.current_player.deck.achetype,
            played_first=(self.play_order[0] == self.current_player),
            won=(winner == self.current_player),
            opponent_archetype=self._get_opponent(self.current_player).deck.archetype,
            format=self.game_format
        )
    def _get_deck_archetype(self, player):
        """Returns limited into about opponent's deck"""
        opponent = self._get_opponent(player)

        if self.open_decklist:
            return opponent.deck.archetype
        else:
            return {
                "likely_colors": self._infer_colors(opponent),
                "meta_percentage": 0.15
            }

    def _infer_colors(self, player):
        """Guess colors based on visible information"""

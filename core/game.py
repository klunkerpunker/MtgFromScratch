from random import random

from player import Player

class Game:
    def __init__(self, player1_name="Player 1", player2_name="Player 2"):
        # Players
        self.players = [
            Player(player1_name),
            Player(player2_name)
        ]
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

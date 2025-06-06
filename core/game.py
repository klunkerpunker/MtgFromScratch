import json
from random import random
from pathlib import Path
from typing import Dict, Optional

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

        self.match_game_number = 1
        self.current_player = self.players[0]
        self.active_player = self.players[0]
        self.turn_phase = "Beginning"

        self.seen_cards = {player: set() for player in self.players}
        self.suspected_archetypes = {player: None for player in self.players}

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
        self.choose_first_player()
        self.draw_starting_hands()

    def choose_first_player(self):
        decider = random.choice(self.players)

        if decider.type == PlayerType.HUMAN:
            decision = PlayDrawDecision.human_decision(decider.name)
        else:
            game_state = self._get_play_draw_state(decider)
            decision = PlayDrawDecision.ai_decision(game_state, self.ai_model)

        self._apply_play_draw(decider, decision)

    def _apply_play_draw(self, decider, decision):
        if decision == "p":
            self.current_player = decider
        else:
            self.current_player = self._get_opponent(decider)

    def draw_starting_hands(self):
        for player in self.players:
            player.draw_card(self, amount=7)



    def _get_opponent(self, requesting_player):
        return next(p for p in self.players if p != requesting_player)

    def _get_play_draw_state(self, requesting_player):
        my_archetype = requesting_player.deck.achetype
        opponent_archetype = None if self.match_game_number == 1 else self._infer_opponent_archetype(requesting_player)

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

    def reveal_card(self, card, revealing_player, observing_player):
        """Called whenever a card becomes visible to opponent"""
        self.seen_cards[observing_player].add(card.name)

        self._update_suspected_archetype(observing_player, card, revealing_player)

    def _update_suspected_archetype(self, observer, target):
        """Re-evaluate archetype guess after new card seen"""
        seen = self.seen_cards[observer]
        target_deck = target.deck

        # Get all meta decks in current format
        format_decks = self._load_decks_meta_info(self.game_format)

        # Key-card matching
        possible_decks = []
        for deck_name, deck_data in format_decks.items():
            key_matches = len(seen & set(deck_data["key_cards"]))
            secondary_matches = len(seen & set(deck_data["secondary_cards"]))

            if key_matches > 0:
                possible_decks.append({
                    "deck_name": deck_name,
                    "confidence": key_matches * 0.6 + secondary_matches * 0.4,
                    "archetype": deck_data["archetype"],
                })

        if possible_decks:
            best_guess = max(possible_decks, key=lambda x: x["confidence"])
            if best_guess["confidence"] > 0.5:
                self.suspected_archetypes[observer] = best_guess["deck_name"]

    def _load_decks_meta_info(self, game_format):
        self._archetype_cache: Dict[str, dict] = {}
        path = Path(f"data/decks/{game_format}/deck_archetypes.json")
        try:
            with open(path) as f:
                self._archetype_cache[game_format] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._archetype_cache[game_format] = {}
        return self._archetype_cache[game_format]

    def _infer_opponent_archetype(self, requesting_player):
        """Guess opponent's deck based on seen cards"""
        opponent = self._get_opponent(requesting_player)

        # Check if we have a high confidence guess
        if self.suspected_archetypes[opponent]:
            # Maybe change this to deck name?
            return self.suspected_archetypes[opponent]["archetype"]

        return self._meta_frequency_guess(requesting_player)

    def _meta_frequency_guess(self, requesting_player):
        """Fallback when no key cards seen"""
        format_meta = self._load_decks_meta_info(self.game_format)
        if not format_meta:
            return "unknown"

        # Get most popular deck
        top_deck = sorted(
            format_meta.items(),
            key=lambda x: x[1]["meta_percentage"],
            reverse=True
        )[:1]

        # Check to see if this line is running correctly when finished
        return top_deck[0][1]["archetype"]

    def queue_event(
            self,
            event: str,
            player: Player,
            reason: str
    ):
        self.event_queue.append((event, player, reason))

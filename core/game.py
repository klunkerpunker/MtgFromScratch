import json
import random
from pathlib import Path
from typing import Dict, Optional

from core import Card
from core.decisions.mulligan import MulliganDecision
from data.historical_repository import HistoricalRepository
from core.player import Player, PlayerType
from core.decisions import PlayDrawDecision
from core.Deck import load_deck

PROJ_DIR = Path(__file__).parent.parent


class Game:
    def __init__(self,
                 player1_type=PlayerType.HUMAN,
                 player2_type=PlayerType.AI,
                 game_format: str = "sparky"):
        # Players
        self.archetypes = None
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
        self.setup()
        self.load_decks()
        self.choose_first_player()
        self.draw_starting_hands()
        mull_dec = {'choice': 'm', 'times': 0}
        while mull_dec['choice'] == 'm':
            mull_dec = self.mulligan_decisions(mull_dec)

    def setup(self):
        self.load_archetypes()

    def load_archetypes(self):
        """Loads deck archetype data from JSON file into self.archetypes"""
        try:
            archetypes_path = PROJ_DIR / 'data'/ 'decks' / self.game_format / 'deck_archetypes.json'

            if not archetypes_path.exists():
                raise FileNotFoundError(f"Archetypes file not found at {archetypes_path}")

            with open(archetypes_path, 'r', encoding='utf-8') as f:
                self.archetypes = json.load(f)

            print(f"Loaded archetype data for {len(self.archetypes)} decks")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in archetypes file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error loading archetypes: {str(e)}")

    def load_decks(self):
        global deck_color
        deck_dict = {
            'w': 'sparky_white',
            'u': 'sparky_blue',
            'b': 'sparky_black',
            'r': 'sparky_red',
            'g': 'sparky_green'
        }
        for player in self.players:
            if player.type == PlayerType.HUMAN:
                #Edit this later to keep prompting if the deck name does not exist
                deck_color = input("Choose your deck color (wubrg): ")
                player.library = load_deck(deck_dict[deck_color], self.game_format)
            if player.type == PlayerType.AI:
                deck_color = random.choice(list(deck_dict.keys()))
                player.library = load_deck(deck_dict[deck_color], self.game_format)
            player.deck_archetype = self.archetypes[deck_dict[deck_color]]
            del deck_color
            self.shuffle_deck(player)

    def shuffle_deck(self, requesting_player):
        random.shuffle(requesting_player.library)

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
        my_archetype = requesting_player.deck_archetype["archetype"]
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

    # Add more factors to this function as model progresses
    # Factors to add later: Did your opponent mulligan, cmc of cards in hand, number of tap lands, combo pieces
    def _get_mulligan_state(self, requesting_player, mull_state):
        hand = requesting_player.hand
        meta_data = {'n_cards': len(hand), 'n_mull': mull_state['times']}

        def count_hand_lands(hand: list[Card]) -> int:
            running_count = 0
            for card in hand:
                for face_name, face_obj in card.faces.items():
                    if 'land' in face_obj.type_line.lower():
                        running_count += 1
                        break
            return running_count
        n_lands = count_hand_lands(hand)
        meta_data['n_lands'] = n_lands
        return meta_data

    def mulligan_decisions(self, mull_state):
        decider = self.current_player
        if decider.type == PlayerType.HUMAN:
            decision = MulliganDecision.human_decision(decider.name, decider.hand)
        else:
            hand_state = self._get_mulligan_state(decider, mull_state)
            decision = MulliganDecision.ai_decision(hand_state, self.ai_model)
        temp_mull_dec = {'choice': decision}
        temp_mull_dec['times']
        return
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
            meta_data: dict
    ):
        self.event_queue.append((event, player, meta_data))


from enum import Enum, auto


class PlayerType(Enum):
    HUMAN = auto()
    AI = auto()


class Player:
    def __init__(self, name: str, playerType: PlayerType) -> None:
        self.name = name
        self.type = playerType
        self.life_total = 20
        self.life_lost_this_turn = 0
        self.life_gained_this_turn = 0
        self.poison_counters = 0
        self.mana_pool = {
            'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0
        }
        self.hand = []
        self.graveyard = []
        self.library = []

    def draw_card(self, game, amount=1):
        """
        Args:
            game: Game object
            amount: Number of cards to draw
        Returns:
            list: Drawn cards (may be shorter than amount if library empties)
            or None if player loses during draw
        """
        drawn_cards = []
        for _ in range(amount):
            if not self.library:
                game.queue_event("player_loses", player=self, reason="empty_library")
                return None

            card = self.library.pop(0)
            self.hand.append(card)
            drawn_cards.append(card)
            game.queue_event("card_drawn", player=self, meta_data={'reason': 'empty_library'})
        return drawn_cards

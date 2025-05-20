from enum import Enum, auto


class PlayerType(Enum):
    HUMAN = auto()
    AI = auto()

class Player:
    def __init__(self, name:str, playerType:PlayerType) -> None:
        self.name = name
        self.type = player_type
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

    def draw_card(self, game):
        """Returns the drawn card or None if player loses"""
        if not self.library:
            game.queue_event("player_loses", player=self, reason="empty_library")
            return None

        card = self.library.pop(0)
        self.hand.append(card)
        game.queue_event("card_drawn", player=self, card=card)
        return card
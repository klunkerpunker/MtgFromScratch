from random import random


class MulliganDecision:
    @staticmethod
    def human_decision(player_name, hand):
        card_names = ""
        for card in hand:
            card_names + f"{card.name},"
        decision = input(f"{player_name}, choose to (k)eep or (m)ulligan this hand:\n{card_names}\n")
        return decision

    @staticmethod
    def ai_decision(hand_state, ai_model=None):
        if ai_model:
            if hand_state['n_mull'] > 2:
                return "k"
            elif hand_state['n_lands'] > 2 & hand_state['n_lands'] < 6:
                return "k"
            else:
                return "m"
        return "k"

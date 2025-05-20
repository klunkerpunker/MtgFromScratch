class PlayDrawDecision:
    @staticmethod
    def human_decision(player_name):
        decision = input(f"{player_name}, choose to (p)lay or (d)raw: ")
        return decision

    @staticmethod
    def ai_decision(game_state, ai_model=None):
        if ai_model:
            return ai_model.predict(game_state)
        return "p" if random.random() > 0.6 else "d"
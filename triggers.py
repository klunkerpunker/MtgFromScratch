from enum import Enum
from typing import Callable, Dict, Any

class TriggerType(Enum):
    CREATURE_DIES = "CREATURE_DIES"
    CREAUTURE_ETB = "CREATURE_ETB"

class TriggerScope(Enum):
    ANY_PLAYER = "ANY_PLAYER"
    OPPONENT_CONTROLLED = "OPPONENT_CONTROLLED"
    YOU_CONTROLLED = "YOU_CONTROLLED"

class EffectType(Enum):
    ADD_COUNTERS = "ADD_COUNTERS"
    DRAW_CARD = "DRAW_CARD"

class TriggeredAbility:
    def __init__(
    self,
    trigger_type: TriggerType,
    scope: TriggerScope,
    effect_type: EffectType,
    effect_config: Dict[str, Any],
    condition: Callable[[Dict], bool] = None
    ):
        self.trigger_type = trigger_type
        self.scope = scope
        self.effect_type = effect_type
        self.effect_config = effect_config
        self.condition = condition or (lambda _: True)

    def execute(self, game, event_data: Dict):
        if self._should_trigger(event_data):
            self._apply_effect(game, event_data)

    def _should_trigger(self, event_data: Dict) -> bool:
        """Check scope and conditions"""
        scope_ok = (
            (self.scope == TriggerScope.ANY_PLAYER) or
            (self.scope == TriggerScope.OPPONENT_CONTROLLED and
             game.is_opponent(event_data['controller'])) or
            (self.scope == TriggerScope.YOU_CONTROLLED and
             not game.is_opponent(event_data['controller']))
        )
        return scope_ok and self.condition(event_data)

    def _apply_effect(self, game, event_data: Dict):
        """Effect dispatcher"""
        if self.effect_type == EffectType.ADD_COUNTERS:
            self._add_counters(game)
        elif self.effect_type == EffectType.DRAW_CARD:
            self._draw_card(game)

    def _add_counters(self, game):
        target = self._resolve_target(self.effect_config['target'])
        game.add_counters(
            target,
            self.effect_config['counter_type'],
            self.effect_config.get('amount', 1),
        )
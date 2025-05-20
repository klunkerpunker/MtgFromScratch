import json
from pathlib import Path
from typing import Dict, Optional
import os

class HistoricalRepository:
    def __init__(self, data_dir: str = "data/historical"):
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, dict] = {}

    def _load_format_data(self, format: str) -> dict:

        if format not in self._cache:
            path = self.data_dir / f"{format}.json"
            try:
                with open(path) as f:
                    self._cache[format] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self._cache[format] = {}
        return self._cache[format]

    def get_win_rates(
            self,
            deck_archetype: str,
            opponent_archetype: Optional[str] = None,
            format: str = "sparky"
                      ) -> Optional[dict]:
        """
        Returns:
            {
                "play_win_rate": float,
                "draw_win_rate": float,
                "confidence" float (0-1 based on sample size)
            }
            or None is no data exists
        """
        format_data = self._load_format_data(format)
        archetype_data = format_data.get(deck_archetype, {})

        #Try specific matchup first
        if opponent_archetype:
            matchup_key = f"vs_{opponent_archetype.lower().replace(' ', '_')}"
            if matchup_key in archetype_data:
                return self._add_confidence(archetype_data[matchup_key])

        if "vs_general" in archetype_data:
            return self._add_confidence(archetype_data["vs_general"])

        return None

    def _add_confidence(self, data: dict) -> dict:
        """Add condidence metric based on sample size"""
        confidence = min(1.0, data["samples"] / 1000)
        return {**data, "confidence": confidence}

    def update_win_rates(
            self,
            deck_archetype: str,
            played_first: bool,
            won: bool,
            opponent_archetype: Optional[str] = None,
            format: str = "sparky"
            ) -> None:
        """Update historical data with new game result"""
        format_data = self._load_format_data(format)

        # Get or initialize archetype entry
        if deck_archetype not in format_data:
            format_data[deck_archetype] = {}

        # Determine matchup key
        matchup_key = (
            f"vs{opponent_archetype.lower().replace(' ', '_')}"
            if opponent_archetype
            else "vs_general"
        )

        # Get or initialize matchup entry
        if matchup_key not in format_data[deck_archetype]:
            format_data[deck_archetype][matchup_key] = {
                "play_win_rate": 0.5,
                "draw_win_rate": 0.5,
                "samples": 0
            }

        stats = format_data[deck_archetype][matchup_key]

        # Update stats
        if played_first:
            new_play = (stats["play_win_rate"] * stats["samples"] + won) / (stats["samples"] + 1)
            stats["play_win_rate"] = round(new_play, 4)
        else:
            new_draw = (stats["draw_win_rate"] * stats["samples"] + won) / (stats["samples"] + 1)
            stats["draw_win_rate"] = round(new_draw, 4)

        stats["samples"] += 1

        self._save_format_data(format, format_data)

    def _save_format_data(self, format: str, data: dict) -> None:
        """Persist data to JSON file"""
        path = self.data_dir / f"{format}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
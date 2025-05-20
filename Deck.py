import json
from json import JSONEncoder
import os
from datetime import datetime
from pathlib import Path

from Card import Card
from scyfall import fetch_card

DECK_DIR = Path(__file__).parent / 'decks'

def parse_decklist(decklist_str):
    deck_str = []
    for line in decklist_str.strip().split('\n'):
        if not line.strip():
            continue
        quantity, card_name = line.split(' ', 1)
        quantity = int(quantity)
        deck_str.extend([card_name] * quantity)

        deck = []
        for card in deck_str:
            card_data = fetch_card(card)
            deck.append(Card(card_data))

    return deck


def save_deck(deck, deck_name):
    """Saves deck to project/decks/ directory using proper serialization"""
    try:
        # Ensure deck directory exists
        DECK_DIR.mkdir(exist_ok=True)

        # Create the full file path
        path = DECK_DIR / f'{deck_name}.json'

        # Prepare the deck data with proper serialization
        deck_data = {
            'cards': [card.to_dict() for card in deck],
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_cards': len(deck),
                'version': '1.1',
                'deck_name': deck_name
            }
        }

        # Save with pretty formatting
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(deck_data, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved deck '{deck_name}' with {len(deck)} cards")
        return True

    except Exception as e:
        print(f"Error saving deck '{deck_name}': {str(e)}")
        return False


def load_deck(deck_name):
    """Loads deck from project/decks/ and reconstructs Card objects"""
    try:
        path = DECK_DIR / f'{deck_name}.json'

        if not path.exists():
            raise FileNotFoundError(f"Deck file '{deck_name}.json' not found")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Validate the data structure
            if 'cards' not in data:
                raise ValueError("Invalid deck format: missing 'cards' key")

            # Reconstruct the deck
            deck = [Card(card_data) for card_data in data['cards']]

            print(f"Successfully loaded deck '{deck_name}' with {len(deck)} cards")
            if 'metadata' in data:
                print(f"Originally created: {data['metadata'].get('created', 'unknown')}")

            return deck

    except Exception as e:
        print(f"Error loading deck '{deck_name}': {str(e)}")
        return None

class CardEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            # Handle Card and Face objects
            d = obj.__dict__.copy()
            # Convert any nested Face objects to dicts
            if 'faces' in d:
                d['faces'] = [face.__dict__ for face in d['faces']]
            return d
        return super().default(obj)

decklist = """
4 Tin Street Cadet
4 Nest Robber
2 Raging Goblin
2 Fearless Halberdier
1 Goblin Gang Leader
3 Goblin Gathering
4 Hurloon Minotaur
2 Storm Strike
3 Shock
3 Reduce to Ashes
2 Raid Bombardment
30 Mountain
"""

spark_black = parse_decklist(decklist)
save_deck(spark_black, 'Sparky Red')
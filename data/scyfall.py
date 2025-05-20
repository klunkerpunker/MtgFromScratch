import requests, copy
import pandas as pd

def fetch_card(name:str):
    card_search = requests.get(f"https://api.scryfall.com/cards/search?q=!\"{name}\"").json()
    return card_search['data'][0]

print(fetch_card('Altar of Bhaal'))
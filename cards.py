import random
from database import save_player

class Card:
    def __init__(self, name, power, effect, deck_type):
        self.name = name
        self.power = power
        self.effect = effect
        self.deck_type = deck_type

class Deck:
    def __init__(self):
        self.tarot = [
            Card("Il Matto", 1, "Pesca 2, perdi 5", "Tarot"),
            Card("La Torre", 7, "Danno +3 se >10", "Tarot"),
            Card("La Luna", 4, "Riduci prossimo attacco", "Tarot"),
            Card("Il Sole", 6, "Cura 5", "Tarot"),
            Card("La Morte", 8, "Elimina carta avversaria", "Tarot")
        ]
        self.elements = [
            Card("Fuoco", 5, "Danno +2 prossimo", "Element"),
            Card("Terra", 3, "Blocca attacco", "Element"),
            Card("Acqua", 4, "Pesca e scarta", "Element"),
            Card("Aria", 6, "Potenzia Tarot", "Element"),
            Card("Etere", 7, "Danno diretto", "Element")
        ]
        self.player_deck = random.sample(self.tarot, 5) + random.sample(self.elements, 5)

def start_card_game(player_id, opponent_id, writer):
    from server import players  # Import dinamico per evitare circular import
    players[player_id]["state"] = "card_game"
    if opponent_id and opponent_id in players:
        players[player_id]["opponent"] = {"fate_points": 20, "deck": players[opponent_id]["deck"]}
    else:  # NPC
        players[player_id]["opponent"] = {"fate_points": 20, "deck": Deck().player_deck}
    deck = players[player_id]["deck"]
    output = "Ombre del Fato - Scegli una carta:\n"
    for i, card in enumerate(deck[:5], 1):  # Prime 5 carte
        output += f"{i}: {card.name} (Potere: {card.power})\n"
    writer.write(output.encode() + b"> ")

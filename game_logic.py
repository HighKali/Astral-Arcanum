import random
from cards import start_card_game
from database import save_player

levels = {i: {"enemies": [], "items": [], "exits": []} for i in range(1, 21)}
players = {}
MYSTERIOUS_ADDRESS = "0xfc90516a1f736FaC557e09D8853dB80dA192c296"

def move_player(player_id, direction, writer):
    x, y = players[player_id]["position"]
    moves = {"su": (0, -1), "giù": (0, 1), "sinistra": (-1, 0), "destra": (1, 0)}
    dx, dy = moves[direction]
    new_x, new_y = x + dx, y + dy
    if (new_x, new_y) in levels[players[player_id]["level"]]["exits"]:
        players[player_id]["level"] += 1
        players[player_id]["position"] = (0, 0)
        save_player(player_id, players[player_id])
    elif 0 <= new_x < 5 and 0 <= new_y < 5:  # Griglia 5x5 semplificata
        players[player_id]["position"] = (new_x, new_y)
        save_player(player_id, players[player_id])
    
    # Probabilità di ottenere 5 Frammenti Astrali dall'indirizzo misterioso
    if random.random() < 0.05:  # 5% di possibilità
        players[player_id]["fragments"] += 5
        writer.write(f"Un dono dall'Abisso! Ottieni 5 Frammenti Astrali da {MYSTERIOUS_ADDRESS}\n".encode())
        save_player(player_id, players[player_id])

def attack(player_id, writer):
    level = players[player_id]["level"]
    if levels[level]["enemies"]:
        enemy = levels[level]["enemies"][0]
        damage = random.randint(5, 10)
        writer.write(f"Attacchi {enemy} per {damage} danni!\n".encode())
        if random.random() < 0.5:  # Nemico contrattacca
            players[player_id]["hp"] -= 5
            writer.write(b"Subisci 5 danni!\n")
        if random.random() < 0.3:
            levels[level]["enemies"].pop(0)
            writer.write(b"Nemico sconfitto!\n")
        save_player(player_id, players[player_id])
    else:
        writer.write(b"Nessun nemico qui.\n")

def use_item(player_id, writer):
    if players[player_id]["inventory"]:
        item = players[player_id]["inventory"][0]
        if item == "Calice Velato":
            players[player_id]["sanity"] += 20
            writer.write(b"Usi il Calice Velato: +20 Sanità\n")
        players[player_id]["inventory"].pop(0)
        save_player(player_id, players[player_id])
    else:
        writer.write(b"Nessun oggetto nell'inventario.\n")

def process_level(player_id, writer):
    level = players[player_id]["level"]
    x, y = players[player_id]["position"]
    output = f"Livello {level}: ({x}, {y})\n"
    output += f"HP: {players[player_id]['hp']} | Sanità: {players[player_id]['sanity']} | Frammenti Astrali: {players[player_id]['fragments']}\n"
    if levels[level]["enemies"]:
        output += f"Nemici: {', '.join(levels[level]['enemies'])}\n"
    if levels[level]["items"]:
        output += f"Oggetti: {', '.join(levels[level]['items'])}\n"
        players[player_id]["inventory"].extend(levels[level]["items"])
        levels[level]["items"] = []
        save_player(player_id, players[player_id])
    if level in [4, 9, 14, 18, 20]:  # Livelli con gioco di carte
        writer.write(b"Una sfida di carte appare! Premi 9 per giocare.\n")
    writer.write(output.encode() + b"> ")

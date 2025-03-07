import asyncio
import random
import tweepy
from game_logic import move_player, attack, use_item, process_level
from cards import Deck, start_card_game
from chat import send_chat, send_room_chat
from database import init_db, save_player, load_player

# Configurazione Twitter (sostituisci con le tue credenziali reali)
TWITTER_API_KEY = "YOUR_API_KEY"
TWITTER_API_SECRET = "YOUR_API_SECRET"
TWITTER_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
TWITTER_ACCESS_TOKEN_SECRET = "YOUR_ACCESS_TOKEN_SECRET"

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Stato globale
players = {}  # {id: {hp, sanity, inventory, position, level, state, deck, fate_points, fragments}}
levels = {i: {"enemies": [], "items": [], "exits": []} for i in range(1, 21)}
active_writers = {}

# Configurazione iniziale dei livelli
for lvl in levels:
    levels[lvl]["enemies"] = ["Medusa Volante"] if lvl <= 5 else ["Cerbero"]
    levels[lvl]["items"] = ["Calice Velato"] if lvl == 1 else ["Pietra Cieca"] if lvl == 6 else []
    levels Pary[lvl]["exits"] = [(0, 1)]  # Esempio: uscita a sud

async def handle_client(reader, writer):
    global players, active_writers
    player_id = f"player_{random.randint(1000, 9999)}"
    active_writers[player_id] = writer

    # Inizializza database
    init_db()

    # Autenticazione
    writer.write(b"Login con X (1), MetaMask (2) o Gioca come Ospite (3): ")
    choice = (await reader.read(100)).decode().strip()

    if choice == "1":  # Login con X
        writer.write(b"Visita questo URL e inserisci il PIN: ")
        verifier = auth.get_authorization_url()
        writer.write(f"{verifier}\nPIN: ".encode())
        pin = (await reader.read(100)).decode().strip()
        auth.request_token["oauth_verifier"] = pin
        token = auth.get_access_token(pin)
        api = tweepy.API(auth)
        user = api.verify_credentials()
        player_id = f"x_{user.id}"
        player_data = load_player(player_id)
        if not player_data:
            players[player_id] = {"hp": 100, "sanity": 100, "inventory": [], "position": (0, 0), "level": 1, "state": "game", "fragments": 100}
            save_player(player_id, players[player_id])
        else:
            players[player_id] = player_data
        writer.write(b"Autenticato con X. +100 Frammenti Astrali\n")
    elif choice == "2":  # Login con MetaMask (simulato)
        writer.write(b"Inserisci il tuo indirizzo Ethereum (es. 0x...): ")
        eth_address = (await reader.read(100)).decode().strip()
        player_id = f"eth_{eth_address[-8:]}"
        player_data = load_player(player_id)
        if not player_data:
            players[player_id] = {"hp": 100, "sanity": 100, "inventory": ["NFT: Spada Primordiale"], "position": (0, 0), "level": 1, "state": "game", "fragments": 500}
            save_player(player_id, players[player_id])
        else:
            players[player_id] = player_data
        writer.write(b"Autenticato con MetaMask. +500 Frammenti + NFT\n")
    elif choice == "3":  # Gioca come Ospite
        players[player_id] = {"hp": 100, "sanity": 100, "inventory": [], "position": (0, 0), "level": 1, "state": "game", "fragments": 0}
        writer.write(b"Benvenuto come Ospite. Nessun bonus iniziale.\n")
    else:
        writer.write(b"Scelta non valida. Connessione terminata.\n")
        writer.close()
        return

    # Inizializza mazzo di carte
    players[player_id]["deck"] = Deck().player_deck
    players[player_id]["fate_points"] = 20

    writer.write(b"Benvenuto in Kali's Inferno! Usa i numeri:\n1: Su, 2: Giù, 3: Sinistra, 4: Destra, 5: Attacca, 6: Usa oggetto, 7: Chat globale, 8: Chat stanza, 9: Sfida carte\n> ")
    
    while True:
        cmd = (await reader.read(100)).decode().strip()
        if not cmd:
            continue

        if players[player_id]["state"] == "game":
            if cmd == "1":  # Su
                move_player(player_id, "su", writer)
                process_level(player_id, writer)
            elif cmd == "2":  # Giù
                move_player(player_id, "giù", writer)
                process_level(player_id, writer)
            elif cmd == "3":  # Sinistra
                move_player(player_id, "sinistra", writer)
                process_level(player_id, writer)
            elif cmd == "4":  # Destra
                move_player(player_id, "destra", writer)
                process_level(player_id, writer)
            elif cmd == "5":  # Attacca
                attack(player_id, writer)
            elif cmd == "6":  # Usa oggetto
                use_item(player_id, writer)
            elif cmd == "7":  # Chat globale
                writer.write(b"Messaggio globale: ")
                msg = (await reader.read(100)).decode().strip()
                send_chat(player_id, msg)
            elif cmd == "8":  # Chat stanza
                writer.write(b"Messaggio stanza: ")
                msg = (await reader.read(100)).decode().strip()
                send_room_chat(player_id, msg)
            elif cmd == "9":  # Sfida carte
                writer.write(b"Sfida un giocatore (ID) o NPC (0): ")
                opponent = (await reader.read(100)).decode().strip()
                start_card_game(player_id, opponent if opponent != "0" else None, writer)
            else:
                writer.write(b"Comando non valido. Usa 1-9.\n> ")

        elif players[player_id]["state"] == "card_game":
            if cmd.isdigit() and 1 <= int(cmd) <= len(players[player_id]["deck"]):
                card_idx = int(cmd) - 1
                card = players[player_id]["deck"][card_idx]
                opponent = players[player_id]["opponent"]
                opponent["fate_points"] -= card.power
                writer.write(f"Giocata {card.name} ({card.power}). Avversario: {opponent['fate_points']} Punti Fato\n".encode())
                if opponent["fate_points"] <= 0:
                    writer.write(b"Vittoria! Torni al gioco.\n> ")
                    players[player_id]["state"] = "game"
                    if "fragments" in opponent:
                        players[player_id]["fragments"] += 50
                    else:
                        players[player_id]["inventory"].append("Chiave Velata")
                    save_player(player_id, players[player_id])
                else:
                    opp_card = random.choice(opponent["deck"])
                    players[player_id]["fate_points"] -= opp_card.power
                    writer.write(f"Avversario gioca {opp_card.name} ({opp_card.power}). Tu: {players[player_id]['fate_points']} Punti Fato\n".encode())
                    if players[player_id]["fate_points"] <= 0:
                        writer.write(b"Sconfitta! Torni al gioco.\n> ")
                        players[player_id]["state"] = "game"
                        players[player_id]["sanity"] -= 10
                        save_player(player_id, players[player_id])
            writer.write(b"Scegli una carta (1-5): ")

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 2323)
    print("Server Telnet avviato su porta 2323")
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())

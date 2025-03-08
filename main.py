from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random
import json
import os

# Dati del Gioco
player = {"x": 1, "y": 1, "hp": 100, "sanity": 100, "inventory": [], "username": ""}
labyrinth = []
monsters = ["Minotauro", "Chimera", "Basilisco"]
tarot_cards = ["La Morte", "Il Diavolo", "La Torre"]
ouija_messages = ["IL SANGUE È LA CHIAVE", "BAPHOMET TI OSSERVA", "NON C'È SCAMPO"]
riddles = [
    {"text": "Ho ali ma non volo, sono temuta da tutti. Chi sono?", "answer": "morte"},
    {"text": "Tre teste ho, ma un solo corpo. Cosa sono?", "answer": "chimera"}
]
alchemy_recipes = {
    "Pozione di Vita": ["Erba Rossa", "Sangue di Mostro"],
    "Pozione di Sanità": ["Cristallo Lunare", "Polvere d'Ossa"]
}

# Funzioni di Salvataggio
def save_user_data(username, password):
    data = {"username": username, "password": password}
    with open("users.json", "w") as f:
        json.dump(data, f)

def load_user_data():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return None

# Generazione Labirinto
def generate_labyrinth():
    global labyrinth
    labyrinth = [[1 if random.random() < 0.3 else 0 for _ in range(10)] for _ in range(10)]
    labyrinth[1][1] = 0  # Start
    labyrinth[8][8] = 2  # Exit

# Classe Principale del Gioco
class LabyrinthGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.game_running = False
        self.message = ""
        
        # Schermata di Login
        self.login_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        self.username_input = Label(text="Username: ")
        self.password_input = Label(text="Password: ")
        self.login_button = Button(text="Login", on_press=self.login)
        self.login_layout.add_widget(self.username_input)
        self.login_layout.add_widget(self.password_input)
        self.login_layout.add_widget(self.login_button)
        self.add_widget(self.login_layout)

        # Layout del Gioco
        self.game_layout = BoxLayout(orientation='vertical')
        self.labyrinth_grid = GridLayout(cols=10, size_hint=(1, 0.6))
        self.status_label = Label(text="", size_hint=(1, 0.1))
        self.message_label = Label(text="", size_hint=(1, 0.1))
        self.controls = BoxLayout(size_hint=(1, 0.2))
        
        # Pulsanti di Controllo
        self.up_btn = Button(text="Su", on_press=lambda x: self.move(0, -1))
        self.down_btn = Button(text="Giù", on_press=lambda x: self.move(0, 1))
        self.left_btn = Button(text="Sinistra", on_press=lambda x: self.move(-1, 0))
        self.right_btn = Button(text="Destra", on_press=lambda x: self.move(1, 0))
        self.tarot_btn = Button(text="Tarocchi", on_press=self.draw_tarot)
        self.ouija_btn = Button(text="Ouija", on_press=self.use_ouija)
        self.craft_btn = Button(text="Craft", on_press=self.craft_item)
        
        self.controls.add_widget(self.up_btn)
        self.controls.add_widget(self.down_btn)
        self.controls.add_widget(self.left_btn)
        self.controls.add_widget(self.right_btn)
        self.controls.add_widget(self.tarot_btn)
        self.controls.add_widget(self.ouija_btn)
        self.controls.add_widget(self.craft_btn)
        
        self.game_layout.add_widget(self.labyrinth_grid)
        self.game_layout.add_widget(self.status_label)
        self.game_layout.add_widget(self.message_label)
        self.game_layout.add_widget(self.controls)

    def login(self, instance):
        username = "user"  # Simulato per semplicità, puoi aggiungere input reale
        password = "pass"
        save_user_data(username, password)
        player["username"] = username
        self.remove_widget(self.login_layout)
        self.add_widget(self.game_layout)
        self.start_game()

    def start_game(self):
        generate_labyrinth()
        self.game_running = True
        self.update_labyrinth()
        Clock.schedule_interval(self.check_events, 1.0)

    def update_labyrinth(self):
        self.labyrinth_grid.clear_widgets()
        for y, row in enumerate(labyrinth):
            for x, cell in enumerate(row):
                if player["x"] == x and player["y"] == y:
                    btn = Button(text="P", background_color=(0, 1, 0, 1))
                elif cell == 1:
                    btn = Button(text="#", background_color=(0, 0, 0, 1))
                elif cell == 2:
                    btn = Button(text="X", background_color=(1, 0, 0, 1))
                else:
                    btn = Button(text=".", background_color=(1, 1, 1, 1))
                self.labyrinth_grid.add_widget(btn)
        self.status_label.text = f"HP: {player['hp']} | Sanity: {player['sanity']} | Inventario: {player['inventory']}"
        self.message_label.text = self.message

    def move(self, dx, dy):
        new_x, new_y = player["x"] + dx, player["y"] + dy
        if 0 <= new_x < 10 and 0 <= new_y < 10 and labyrinth[new_y][new_x] != 1:
            player["x"], player["y"] = new_x, new_y
            self.update_labyrinth()

    def fight_monster(self, monster):
        monster_hp = 50
        self.message = f"Hai incontrato un {monster}!"
        self.update_labyrinth()
        while monster_hp > 0 and player["hp"] > 0:
            damage = random.randint(10, 20)
            monster_hp -= damage
            player["hp"] -= random.randint(5, 15)
            if player["hp"] <= 0:
                self.message = "Sei morto..."
                self.game_running = False
                return False
        self.message = f"Hai sconfitto il {monster}!"
        player["inventory"].append("Sangue di Mostro")
        return True

    def draw_tarot(self, instance):
        card = random.choice(tarot_cards)
        self.message = f"Hai pescato: {card}"
        if card == "La Morte":
            player["sanity"] -= 20
        elif card == "Il Diavolo":
            player["hp"] -= 10
        self.update_labyrinth()

    def use_ouija(self, instance):
        message = random.choice(ouija_messages)
        self.message = f"La tavola Ouija rivela: '{message}'"
        player["sanity"] -= 10
        self.update_labyrinth()

    def craft_item(self, instance):
        if "Erba Rossa" in player["inventory"] and "Sangue di Mostro" in player["inventory"]:
            player["inventory"].remove("Erba Rossa")
            player["inventory"].remove("Sangue di Mostro")
            player["inventory"].append("Pozione di Vita")
            self.message = "Hai creato una Pozione di Vita!"
        else:
            self.message = "Ingredienti mancanti!"
        self.update_labyrinth()

    def solve_riddle(self):
        riddle = random.choice(riddles)
        self.message = riddle["text"] + " (Risposta simulata: corretta al 50%)"
        if random.random() < 0.5:
            player["inventory"].append("Cristallo Lunare")
            self.message += "\nCorretto! Trovi un Cristallo Lunare."
        else:
            player["sanity"] -= 15
            self.message += "\nSbagliato... Qualcosa ti osserva."
        self.update_labyrinth()

    def baphomet_encounter(self):
        self.message = "Un'ombra emerge. È Baphomet.\n'Baphomet parla: Mortale, io sono il signore delle tenebre, venerato dai Templari. Il tuo sangue è mio.'"
        self.update_labyrinth()
        if self.fight_monster("Baphomet"):
            self.message = "Hai sconfitto Baphomet... ma un sussurro ti segue.\nVinci... ma sei davvero libero?"
            self.game_running = False
        else:
            self.message = "Scappi, ma il labirinto ti intrappola."
            self.game_running = False
        self.update_labyrinth()

    def check_events(self, dt):
        if not self.game_running:
            return
        if random.random() < 0.2:
            self.fight_monster(random.choice(monsters))
        elif random.random() < 0.3:
            self.solve_riddle()
        elif labyrinth[player["y"]][player["x"]] == 2:
            self.baphomet_encounter()
        self.update_labyrinth()

class LabyrinthApp(App):
    def build(self):
        return LabyrinthGame()

if __name__ == "__main__":
    LabyrinthApp().run()

# Labyrinth of the Occult
Un RPG horror esoterico per Android (Termux) con Kivy.

## Installazione
1. Installa Termux.
2. Abilita il repository X11:
3. pkg update && pkg upgrade -y
   pkg install x11-repo -y


3. Installa le dipendenze:



   pkg install libffi sdl2 sdl2-image sdl2-mixer sdl2-ttf python -y
   pip install -r requirements.txt


4. Clona il repository:



   git clone https://github.com/HighKali/Kalis-Inferno.git
   cd Kalis-Inferno


5. Installa XServer XSDL dal Play Store, avvialo, ed esporta il display:



   export DISPLAY=:0
   python main.py


## Comandi
- Usa i pulsanti per muoverti e interagire.


Push su GitHub:

bash


git add main.py requirements.txt README.md
git commit -m "Fixed SDL2 installation issues and updated README for Termux"
git push origin main

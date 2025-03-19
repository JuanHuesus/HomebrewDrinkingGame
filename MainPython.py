import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cards.normal_deck import NormalDeck
from cards.penalty_deck import PenaltyDeck
from views.player_setup import PlayerSetupFrame
from views.game_frame import GameFrame

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homebrew Drinking")
        self.geometry("900x600")

        # Ladataan taustakuva
        try:
            self.bg_image = Image.open("Images/background.jpg")
            self.bg_image = self.bg_image.resize((900, 600), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
            self.canvas = tk.Canvas(self, width=900, height=600)
            self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print("Background image not found:", e)

        # ttk-tyylit
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 14), background="#f0f0f0")
        
        self.players = []
        self.current_player_index = 0

        # Luodaan pakat suoraan ilman ulkoisia tiedostoja
        self.normal_deck = NormalDeck()
        self.penalty_deck = PenaltyDeck()
        
        # Header
        header_frame = ttk.Frame(self, padding=10)
        header_frame.place(x=0, y=0, relwidth=1)
        header_label = ttk.Label(header_frame, text="Homebrew Drinking Game", font=("Helvetica", 20, "bold"))
        header_label.pack(side="top", pady=10)
        
        # Näkymien container
        self.container = ttk.Frame(self, padding=10)
        self.container.place(x=0, y=50, relwidth=0.75, relheight=0.85)
        
        self.frames = {}
        for F in (PlayerSetupFrame, GameFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("PlayerSetupFrame")
        
        # Pelaajalista
        self.player_list_frame = ttk.Frame(self, padding=10, relief="ridge")
        self.player_list_frame.place(relx=0.75, rely=0.1, relwidth=0.25, relheight=0.75)
        self.player_list_label = ttk.Label(self.player_list_frame, text="Players:", font=("Helvetica", 16))
        self.player_list_label.pack(pady=10)
        self.player_listbox = tk.Listbox(self.player_list_frame, font=("Helvetica", 12))
        self.player_listbox.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Exit-painike
        self.exit_button = ttk.Button(self, text="Exit", command=self.exit_game)
        self.exit_button.place(relx=0.95, rely=0.95, anchor='se')
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    
    def add_player(self, player_name):
        if player_name and player_name not in self.players:
            self.players.append(player_name)
            self.player_listbox.insert(tk.END, player_name)
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.frames["GameFrame"].update_for_new_turn()
    
    def exit_game(self):
        self.destroy()

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()

import tkinter as tk
from tkinter import ttk
from cards.normal_deck import NormalDeck
from cards.penalty_deck import PenaltyDeck
from views.player_setup import PlayerSetupFrame
from views.game_frame import GameFrame

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homebrew Drinking")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")  # Vaalea taustaväri

        # ttk-tyylin määrittely
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 14), background="#f0f0f0")

        self.players = []
        self.current_player_index = 0
        self.normal_deck = NormalDeck()
        self.penalty_deck = PenaltyDeck()

        # Lisätään esimerkkikortit normaaliin pakkaan
        sample_cards = [
            "Drink 2", "Drink 1, Give 1", "Drink 2",
            "Give 3", "Crowd Challenge", "Drink 1",
            "Give 1", "Surprise Card"
        ]
        for card in sample_cards:
            self.normal_deck.add_card(card)

        # Lisätään rangaistuskortteja rangaistuspakkaan
        penalty_cards = ["Penalty Drink 1", "Penalty Drink 2", "Penalty Drink 3"]
        for card in penalty_cards:
            self.penalty_deck.add_penalty_card(card)

        # Yläreuna: otsikkokehys
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(side="top", fill="x")
        header_label = ttk.Label(header_frame, text="Homebrew Drinking Game", font=("Helvetica", 20, "bold"))
        header_label.pack(side="top", pady=10)

        # Pääalue: näkymille varattu kontti
        self.container = ttk.Frame(self, padding=10)
        self.container.pack(side="left", fill="both", expand=True)

        self.frames = {}
        for F in (PlayerSetupFrame, GameFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PlayerSetupFrame")

        # Oikea sivupaneeli pelaajalistaa varten
        self.player_list_frame = ttk.Frame(self, padding=10, relief="ridge")
        self.player_list_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.player_list_label = ttk.Label(self.player_list_frame, text="Players:", font=("Helvetica", 16))
        self.player_list_label.pack(pady=10)
        self.player_listbox = tk.Listbox(self.player_list_frame, font=("Helvetica", 12))
        self.player_listbox.pack(fill="both", padx=10, pady=10, expand=True)

        # Exit-nappi alareunaan
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

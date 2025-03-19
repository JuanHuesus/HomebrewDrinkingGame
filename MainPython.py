import tkinter as tk
import random

class Deck:
    def __init__(self):
        self.cards = []

    def add_card(self, card_name):
        if card_name and card_name not in self.cards:
            self.cards.append(card_name)

    def remove_card(self, card_name):
        if card_name in self.cards:
            self.cards.remove(card_name)

    def draw_cards(self, num):
        if len(self.cards) >= num:
            drawn_cards = random.sample(self.cards, num)
            return self.handle_special_cards(drawn_cards)
        return []

    def handle_special_cards(self, drawn_cards):
        """Handles special cards that change behavior or trigger actions."""
        transformed_cards = []
        for card in drawn_cards:
            if card == "Surprise Card":
                # Example of a special card that transforms into another card
                transformed_cards.append("Drink 5")  # Turns into a "Drink 5" card
            elif card == "Crowd Challenge":
                # Example of a card that triggers an action
                transformed_cards.append("Crowd Challenge")  # Keeps the card, but it will trigger an action
            else:
                transformed_cards.append(card)
        return transformed_cards

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homebrew Drinking")
        self.geometry("800x600")

        self.players = []
        self.current_player_index = 0
        self.deck = Deck()

        # Sample cards for demonstration, including a "Surprise Card"
        sample_cards = ["Drink 2", "Drink 1, Give 1", "Drink 2", "Give 3", "Crowd Challenge", "Drink 1", "Give 1", "Surprise Card"]
        for card in sample_cards:
            self.deck.add_card(card)

        # Container to hold frames
        self.container = tk.Frame(self)
        self.container.pack(side="left", fill="both", expand=True)

        self.frames = {}
        for F in (PlayerSetupFrame, GameFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PlayerSetupFrame")

        # Player list on the right
        self.player_list_frame = tk.Frame(self, width=200)
        self.player_list_frame.pack(side="right", fill="y")
        self.player_list_label = tk.Label(self.player_list_frame, text="Players:")
        self.player_list_label.pack(pady=10)
        self.player_listbox = tk.Listbox(self.player_list_frame)
        self.player_listbox.pack(fill="y", padx=10, pady=10)

        # Exit button
        self.exit_button = tk.Button(self, text="Exit", command=self.exit_game)
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

class PlayerSetupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.center_frame = tk.Frame(self)
        self.center_frame.pack(expand=True)

        self.label = tk.Label(self.center_frame, text="Enter Player Name:")
        self.label.pack(pady=10)

        self.player_entry = tk.Entry(self.center_frame)
        self.player_entry.pack(pady=5)

        self.add_button = tk.Button(self.center_frame, text="Add Player", command=self.add_player)
        self.add_button.pack(pady=5)

        self.start_button = tk.Button(self.center_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=20)

    def add_player(self):
        player_name = self.player_entry.get().strip()
        if player_name:
            self.controller.add_player(player_name)
            self.player_entry.delete(0, tk.END)

    def start_game(self):
        if self.controller.players:
            self.controller.show_frame("GameFrame")
            self.controller.frames["GameFrame"].update_for_new_turn()

class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.center_frame = tk.Frame(self)
        self.center_frame.pack(expand=True)

        self.label = tk.Label(self.center_frame, text="Game Started!")
        self.label.pack(pady=20)

        self.card_buttons = []
        for _ in range(3):
            btn = tk.Button(self.center_frame, text="", command=lambda b=_: self.select_card(b))
            btn.pack(pady=5)
            self.card_buttons.append(btn)

        self.turn_label = tk.Label(self.center_frame, text="")
        self.turn_label.pack(pady=10)

    def update_for_new_turn(self):
        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")
        cards = self.controller.deck.draw_cards(3)
        for btn, card in zip(self.card_buttons, cards):
            btn.config(text=card, state=tk.NORMAL)

    def select_card(self, button_index):
        selected_card = self.card_buttons[button_index].cget("text")
        print(f"{self.controller.players[self.controller.current_player_index]} selected {selected_card}")
        if selected_card == "Crowd Challenge":
            self.handle_crowd_challenge()
        for btn in self.card_buttons:
            btn.config(state=tk.DISABLED)
        self.controller.next_player()

    def handle_crowd_challenge(self):
        # Implement behavior for crowd challenge, such as showing a pop-up or prompting all players.
        print("Crowd Challenge triggered! All players must do something special!")
        # Here you could add logic to pop up a challenge for all players.

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()

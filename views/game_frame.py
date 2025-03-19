import tkinter as tk

class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.center_frame = tk.Frame(self)
        self.center_frame.pack(expand=True)

        self.label = tk.Label(self.center_frame, text="Game Started!")
        self.label.pack(pady=20)

        # Näytetään kolme normaalia korttipainiketta
        self.card_buttons = []
        for i in range(3):
            btn = tk.Button(self.center_frame, text="", command=lambda idx=i: self.select_card(idx))
            btn.pack(pady=5)
            self.card_buttons.append(btn)

        # Redraw-nappi, joka laukaisee rangaistuskortin arvonnan, mikäli pelaaja ei valinnut mitään
        self.redraw_button = tk.Button(self.center_frame, text="Redraw (Penalty)", command=self.redraw_penalty)
        self.redraw_button.pack(pady=10)

        self.turn_label = tk.Label(self.center_frame, text="")
        self.turn_label.pack(pady=10)

    def update_for_new_turn(self):
        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")
        # Arvotaan kolme korttia normaalista pakasta
        cards = self.controller.normal_deck.draw_cards(3)
        for btn, card in zip(self.card_buttons, cards):
            btn.config(text=card, state=tk.NORMAL)

    def select_card(self, button_index):
        selected_card = self.card_buttons[button_index].cget("text")
        print(f"{self.controller.players[self.controller.current_player_index]} selected {selected_card}")
        if selected_card == "Crowd Challenge":
            self.handle_crowd_challenge()
        # Poistetaan käytöstä kaikki korttipainikkeet valinnan jälkeen
        for btn in self.card_buttons:
            btn.config(state=tk.DISABLED)
        self.controller.next_player()

    def redraw_penalty(self):
        """Jos pelaaja ei valinnut mitään, arvotaan rangaistuskortti."""
        penalty_card = self.controller.penalty_deck.draw_penalty_card()
        if penalty_card:
            print(f"{self.controller.players[self.controller.current_player_index]} drew penalty card: {penalty_card}")
        else:
            print("No penalty cards available.")
        # Poistetaan käytöstä normaalikortit ja siirrytään seuraavalle pelaajalle
        for btn in self.card_buttons:
            btn.config(state=tk.DISABLED)
        self.controller.next_player()

    def handle_crowd_challenge(self):
        print("Crowd Challenge triggered! All players must do something special!")

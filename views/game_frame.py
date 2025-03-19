import tkinter as tk
from tkinter import ttk

class CardWidget(tk.Canvas):
    def __init__(self, parent, text="", command=None, width=120, height=180, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.command = command
        self.text_item = None
        self.draw_card(text)
        self.bind("<Button-1>", self.on_click)
    
    def draw_card(self, text):
        self.delete("all")
        # Piirretään kortin tausta
        self.create_rectangle(5, 5, self.width-5, self.height-5, fill="white", outline="black", width=2)
        # Piirretään kortin teksti keskelle
        self.text_item = self.create_text(self.width/2, self.height/2, text=text, font=("Helvetica", 12), fill="black", width=self.width-10)
    
    def update_text(self, text):
        self.draw_card(text)
    
    def on_click(self, event):
        if self.command:
            self.command()

class GameFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.center_frame = ttk.Frame(self)
        self.center_frame.pack(expand=True, fill="both")
        
        self.turn_label = ttk.Label(self.center_frame, text="", font=("Helvetica", 16))
        self.turn_label.pack(pady=10)
        
        # Keskitetään kortit erilliseen frameen
        self.card_frame = ttk.Frame(self.center_frame)
        self.card_frame.pack(pady=20)
        
        # Luodaan kolme korttia vierekkäin
        self.card_widgets = []
        for i in range(3):
            card = CardWidget(self.card_frame, text="", command=lambda idx=i: self.select_card(idx))
            card.grid(row=0, column=i, padx=10)
            self.card_widgets.append(card)
        
        # Redraw-nappi, joka myös arpoo rangaistuskortin
        self.redraw_button = ttk.Button(self.center_frame, text="Redraw (Penalty)", command=self.redraw_penalty)
        self.redraw_button.pack(pady=10)
    
    def update_for_new_turn(self):
        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")
        # Arvotaan kolme korttia normaalista pakasta
        cards = self.controller.normal_deck.draw_cards(3)
        for widget, card in zip(self.card_widgets, cards):
            widget.update_text(card)
            widget.config(state="normal")
    
    def select_card(self, button_index):
        # Haetaan valitun kortin teksti
        selected_card = self.card_widgets[button_index].itemcget(self.card_widgets[button_index].text_item, "text")
        print(f"{self.controller.players[self.controller.current_player_index]} selected {selected_card}")
        if selected_card == "Crowd Challenge":
            self.handle_crowd_challenge()
        # Estetään muiden korttien klikkaus
        for widget in self.card_widgets:
            widget.config(state="disabled")
        self.controller.next_player()
    
    def redraw_penalty(self):
        """Jos pelaaja haluaa uudelleen arvotut kortit, arvotaan myös rangaistuskortti."""
        penalty_card = self.controller.penalty_deck.draw_penalty_card()
        if penalty_card:
            print(f"{self.controller.players[self.controller.current_player_index]} drew penalty card: {penalty_card}")
        else:
            print("No penalty cards available.")
        for widget in self.card_widgets:
            widget.config(state="disabled")
        self.controller.next_player()
    
    def handle_crowd_challenge(self):
        print("Crowd Challenge triggered! All players must do something special!")

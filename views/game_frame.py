import tkinter as tk
from tkinter import ttk

class CardWidget(tk.Canvas):
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.text_item = None

        # Ensimmäinen piirto
        self.draw_card()
        
        # Päivittää kortin, jos sen koko muuttuu
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)
    
    def draw_card(self):
        """Piirtää kortin dynaamisesti skaalautuvana."""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        if width < 10 or height < 10:
            return  # Vältetään piirtämistä, jos koko on liian pieni

        margin = int(min(width, height) * 0.05)  # Skaalautuva marginaali
        font_size = max(10, int(height / 10))  # Skaalautuva fontti

        # Piirretään kortti
        self.create_rectangle(margin, margin, width - margin, height - margin,
                              fill="white", outline="black", width=3)

        # Kortin teksti keskelle
        self.text_item = self.create_text(width/2, height/2,
                                          text=self.text,
                                          font=("Helvetica", font_size, "bold"),
                                          fill="black",
                                          width=width - margin*2)

    def update_text(self, text):
        """Päivittää kortin tekstin ja piirtää kortin uudelleen."""
        self.text = text
        self.draw_card()
    
    def on_resize(self, event):
        """Uudelleenpiirto, kun kortin koko muuttuu."""
        self.draw_card()
    
    def on_click(self, event):
        """Kortin klikkaustoiminto."""
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

        # Korttikehys, jossa kortit sijoitetaan vierekkäin
        self.card_frame = ttk.Frame(self.center_frame)
        self.card_frame.pack(expand=True, fill="both")

        # Korttien luonti (käytetään grid-layoutia keskityksen varmistamiseksi)
        self.card_widgets = []
        for i in range(3):
            card = CardWidget(self.card_frame, text="", command=lambda idx=i: self.select_card(idx))
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.card_widgets.append(card)

        # Skaalautuvuuden varmistaminen
        for i in range(3):
            self.card_frame.columnconfigure(i, weight=1)
        self.card_frame.rowconfigure(0, weight=1)

        # Redraw-painike
        self.redraw_button = ttk.Button(self.center_frame, text="Redraw (Penalty)", command=self.redraw_penalty)
        self.redraw_button.pack(pady=10)

        # Tallennetaan tieto siitä, onko redraw käytetty, mutta oletusarvoisesti sitä ei tarvitse käyttää
        self.redraw_used = False

    def update_for_new_turn(self):
        """Päivittää käyttöliittymän uuden vuoron alkaessa."""
        self.redraw_used = False  # Resetoi redraw-tilan uudelle kierrokselle

        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")

        # Nostetaan kolme korttia normaalipakasta
        cards = self.controller.normal_deck.draw_cards(3)

        for widget, card in zip(self.card_widgets, cards):
            widget.update_text(card)
            widget.bind("<Button-1>", lambda event, idx=self.card_widgets.index(widget): self.select_card(idx))

    def select_card(self, button_index):
        """Käsittelee pelaajan korttivalinnan."""
        selected_card = self.card_widgets[button_index].text
        print(f"{self.controller.players[self.controller.current_player_index]} selected {selected_card}")

        if selected_card == "Crowd Challenge":
            self.handle_crowd_challenge()

        # Siirrytään seuraavalle pelaajalle, olipa redraw käytetty tai ei
        self.controller.next_player()

    def redraw_penalty(self):
        """Arpoo rangaistuskortin, antaa uudet kortit, mutta pelaaja ei menetä vuoroaan."""
        if self.redraw_used:
            print("Redraw is already used this turn.")
            return
        
        penalty_card = self.controller.penalty_deck.draw_penalty_card()
        if penalty_card:
            print(f"{self.controller.players[self.controller.current_player_index]} drew penalty card: {penalty_card}")
        else:
            print("No penalty cards available.")

        # Nostetaan uudet kortit, mutta pidetään pelaaja samana
        cards = self.controller.normal_deck.draw_cards(3)
        for widget, card in zip(self.card_widgets, cards):
            widget.update_text(card)
            widget.bind("<Button-1>", lambda event, idx=self.card_widgets.index(widget): self.select_card(idx))

        # Merkkaa että redraw on käytetty, mutta ei pakota sen käyttämistä
        self.redraw_used = True

    def handle_crowd_challenge(self):
        print("Crowd Challenge triggered! All players must do something special!")

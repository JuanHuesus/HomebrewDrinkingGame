import tkinter as tk
from tkinter import ttk
import random

class CardWidget(tk.Canvas):
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.text_item = None
        self.border_color = "black"  
        self.draw_card()
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)

    def draw_card(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        m = int(min(w, h) * 0.05)
        fs = max(10, int(h / 10))
        self.create_rectangle(m, m, w - m, h - m, fill="white", outline=self.border_color, width=3)
        self.text_item = self.create_text(w/2, h/2, text=self.text, font=("Helvetica", fs, "bold"),
                                          fill="black", width=w - m*2)

    def update_text(self, text):
        self.text = text
        self.draw_card()

    def update_border_color(self, color):
        self.border_color = color
        self.draw_card()

    def on_resize(self, event):
        self.draw_card()

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

        self.card_frame = ttk.Frame(self.center_frame)
        self.card_frame.pack(expand=True, fill="both")

        self.card_widgets = []
        for i in range(3):
            c = CardWidget(self.card_frame, text="", command=lambda idx=i: self.select_card(idx))
            c.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.card_widgets.append(c)
        for i in range(3):
            self.card_frame.columnconfigure(i, weight=1)
        self.card_frame.rowconfigure(0, weight=1)

        self.redraw_button = ttk.Button(self.center_frame, text="Redraw (Penalty)", command=self.redraw_penalty)
        self.redraw_button.pack(pady=10)

        self.penalty_label = ttk.Label(self.center_frame, text="", font=("Helvetica", 14),
                                       background="#f0f0f0", foreground="red")
        self.penalty_label.place(relx=0.5, rely=0.1, anchor="center")

        self.redraw_used = False

        self.current_cards = []
        self.hidden_index = None
        self.revealed = []
        self.ditto_active = []

    def update_for_new_turn(self):
        self.redraw_used = False
        self.penalty_label.config(text="")

        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")

        self.current_cards = self.controller.normal_deck.draw_cards(3)
        self.hidden_index = random.randint(0, 2)
        self.revealed = [True, True, True]
        self.revealed[self.hidden_index] = False
        self.ditto_active = [False, False, False]

        for i, (widget, card_value) in enumerate(zip(self.card_widgets, self.current_cards)):
            widget.update_border_color("black")
            if not self.revealed[i]:
                widget.update_text("???")
            else:
                widget.update_text(card_value)
            widget.bind("<Button-1>", lambda e, idx=i: self.select_card(idx))

    def select_card(self, i):
        if self.ditto_active[i]:
            self.controller.log_message(f"{self.controller.players[self.controller.current_player_index]} confirmed Ditto card selection.")
            self.card_widgets[i].unbind("<Button-1>")
            self.controller.next_player()
            return

        for widget in self.card_widgets:
            widget.unbind("<Button-1>")

        if not self.revealed[i]:
            self.revealed[i] = True
            actual_value = self.current_cards[i]
            self.card_widgets[i].update_text(actual_value)
        else:
            actual_value = self.current_cards[i]

        if random.random() < 0.25:
            self.ditto_active[i] = True
            self.card_widgets[i].update_text("Ditto")
            self.card_widgets[i].update_border_color("purple")
            self.controller.log_message("Ditto effect activated! Click the card again to confirm.")
            self.card_widgets[i].bind("<Button-1>", lambda e, idx=i: self.select_card(idx))
            return
        else:
            self.controller.log_message(f"{self.controller.players[self.controller.current_player_index]} selected {actual_value}")
            self.controller.next_player()

    def redraw_penalty(self):
        if self.redraw_used:
            self.controller.log_message("Redraw is already used this turn.")
            return

        p = self.controller.penalty_deck.draw_penalty_card()
        if p:
            self.controller.log_message(f"{self.controller.players[self.controller.current_player_index]} drew penalty card: {p}")
            self.penalty_label.config(text=p)
        else:
            self.penalty_label.config(text="")

        self.current_cards = self.controller.normal_deck.draw_cards(3)
        self.hidden_index = random.randint(0, 2)
        self.revealed = [True, True, True]
        self.revealed[self.hidden_index] = False
        self.ditto_active = [False, False, False]

        for i, (widget, card_value) in enumerate(zip(self.card_widgets, self.current_cards)):
            widget.update_border_color("black")
            if not self.revealed[i]:
                widget.update_text("???")
            else:
                widget.update_text(card_value)
            widget.bind("<Button-1>", lambda e, idx=i: self.select_card(idx))
        self.redraw_used = True

    def handle_crowd_challenge(self):
        self.controller.log_message("Crowd Challenge triggered! All players must do something special!")

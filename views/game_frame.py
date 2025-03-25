import tkinter as tk
from tkinter import ttk
import random
# Jos haluat käyttää taustakuvaa, poista kommentit:
# from PIL import Image, ImageTk

class CardWidget(tk.Canvas):
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.text_item = None
        self.border_color = "black"
        self.bg_color = "white"
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
        self.create_rectangle(m, m, w - m, h - m, fill=self.bg_color,
                              outline=self.border_color, width=3)
        self.text_item = self.create_text(w/2, h/2, text=self.text,
                                          font=("Helvetica", fs, "bold"),
                                          fill="black",
                                          width=w - m*2)

    def update_text(self, text):
        self.text = text
        self.draw_card()

    def update_border_color(self, color):
        self.border_color = color
        self.draw_card()
        
    def update_fill_color(self, color):
        self.bg_color = color
        self.draw_card()

    def on_resize(self, event):
        self.draw_card()

    def on_click(self, event):
        if self.command:
            self.command()

    def flip_animation(self, final_text, steps=3, delay=100):
        def animate(i):
            if i < steps:
                self.update_text("." * (i + 1))
                self.after(delay, lambda: animate(i + 1))
            else:
                self.update_text(final_text)
        animate(0)

    def flash_card(self, flash_color="yellow", flash_duration=200):
        original_color = self.border_color
        self.update_border_color(flash_color)
        self.after(flash_duration, lambda: self.update_border_color(original_color))


class GameFrame(ttk.Frame):
    def __init__(self, parent, controller):
        # Voit valita haluamasi ttk-teeman
        style = ttk.Style()
        style.theme_use("clam")  # esim. "clam", "default", "alt" jne.

        # Määritellään mukautetut tyylit
        style.configure("GameFrame.TFrame",
                        background="#ADD8E6")  # vaaleansininen
        style.configure("GameLabel.TLabel",
                        background="#ADD8E6",
                        foreground="#00008B",
                        font=("Helvetica", 14, "bold"))
        style.configure("GameButton.TButton",
                        font=("Helvetica", 12, "bold"),
                        foreground="white",
                        padding=6)
        style.map("GameButton.TButton",
                  background=[("active", "#5F9EA0"), ("!disabled", "#4682B4")])

        super().__init__(parent, style="GameFrame.TFrame")
        self.controller = controller

        # Halutessasi taustakuva (kommentoi pois, jos et käytä)
        # self.set_background_image("path/to/your/background.png")

        self.ITEM_CARDS = {"Shield", "Reveal Free", "Extra Life", "test1", "test2"}

        # Keskikehys (kaikki kortit ja pelaajateksti sen sisällä)
        self.center_frame = ttk.Frame(self, style="GameFrame.TFrame")
        self.center_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.turn_label = ttk.Label(self.center_frame, text="", style="GameLabel.TLabel")
        self.turn_label.pack(pady=10)

        # Korttikehys
        self.card_frame = ttk.Frame(self.center_frame, style="GameFrame.TFrame")
        self.card_frame.pack(expand=True, fill="both")

        self.card_widgets = []
        for i in range(3):
            c = CardWidget(self.card_frame, text="", command=lambda idx=i: self.select_card(idx),
                           bg="#FFFFFF")  # Canvasin taustaväri
            c.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.card_widgets.append(c)
        for i in range(3):
            self.card_frame.columnconfigure(i, weight=1)
        self.card_frame.rowconfigure(0, weight=1)

        # Erotellaan penalty-napit omaan kehykseensä
        self.penalty_frame = ttk.Frame(self.center_frame, style="GameFrame.TFrame")
        self.penalty_frame.pack(pady=10, fill="x")

        self.roll_button = ttk.Button(self.penalty_frame,
                                      text="Roll Penalty Deck",
                                      command=self.roll_penalty,
                                      style="GameButton.TButton")
        self.roll_button.grid(row=0, column=0, padx=(20, 10))

        self.redraw_button = ttk.Button(self.penalty_frame,
                                        text="Redraw (Penalty)",
                                        command=self.redraw_penalty,
                                        style="GameButton.TButton")
        self.redraw_button.grid(row=0, column=1, padx=(10, 20))

        # Penalty-label
        self.penalty_label = ttk.Label(self.center_frame, text="",
                                       font=self.controller.label_font,
                                       background="#FFFACD",
                                       foreground="red")
        self.penalty_label.place(relx=0.5, rely=0.1, anchor="center")

        self.redraw_used = False

        # Vuoron kortit
        self.current_cards = []
        self.hidden_index = None
        self.revealed = []
        self.ditto_active = [False, False, False]

    def set_background_image(self, image_path):
        """
        Asettaa taustakuvan koko GameFrame-alueelle.
        Käytä PIL (Pillow) -kirjastoa:
            pip install pillow
        """
        from PIL import Image, ImageTk
        self.bg_image = Image.open(image_path)
        # Skaalaa kuva kehyksen kokoon (jos haluat automaattisesti)
        # w, h = self.controller.winfo_width(), self.controller.winfo_height()
        # self.bg_image = self.bg_image.resize((w, h), Image.ANTIALIAS)

        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.image = self.bg_photo
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # Nostetaan muut kehykset taustakuvan päälle
        self.center_frame.lift()

    def roll_penalty(self):
        p = self.controller.penalty_deck.draw_penalty_card()
        if p:
            self.controller.log_message(
                f"{self.controller.players[self.controller.current_player_index]} rolled penalty card: {p}")
            self.penalty_label.config(text=p)
            self.penalty_label.after(100, lambda: self.penalty_label.config(background="yellow"))
            self.penalty_label.after(300, lambda: self.penalty_label.config(background="#FFFACD"))
        else:
            self.penalty_label.config(text="")

    def update_for_new_turn(self):
        self.redraw_used = False
        self.penalty_label.config(text="")

        current_player = self.controller.players[self.controller.current_player_index]
        self.turn_label.config(text=f"{current_player}'s Turn")

        self.current_cards = self.controller.normal_deck.draw_cards(3)
        for i in range(len(self.current_cards)):
            if random.random() < 0.3:
                self.current_cards[i] = random.choice(list(self.ITEM_CARDS))

        self.hidden_index = random.randint(0, 2)
        self.revealed = [True, True, True]
        self.revealed[self.hidden_index] = False
        self.ditto_active = [False, False, False]

        for i, (widget, card_value) in enumerate(zip(self.card_widgets, self.current_cards)):
            widget.update_border_color("black")
            widget.update_fill_color("white")
            if not self.revealed[i]:
                widget.update_text("???")
            else:
                widget.update_text(card_value)
            widget.bind("<Button-1>", lambda e, idx=i: self.select_card(idx))

    def select_card(self, i):
        for widget in self.card_widgets:
            widget.unbind("<Button-1>")
        current_player = self.controller.players[self.controller.current_player_index]

        if not self.revealed[i]:
            self.revealed[i] = True
            self.card_widgets[i].flip_animation(self.current_cards[i])
            self.card_widgets[i].bind("<Button-1>", lambda e, idx=i: self.select_card(idx))
            return

        if self.ditto_active[i]:
            self.controller.log_message(f"{current_player} confirmed Ditto card.")
            self.card_widgets[i].unbind("<Button-1>")
            self.card_widgets[i].update_fill_color("white")
            self.card_widgets[i].update_border_color("black")
            self.controller.next_player()
            return

        revealed_value = self.card_widgets[i].text
        if revealed_value in self.ITEM_CARDS:
            self.controller.log_message(f"{current_player} acquired item: {revealed_value}")
            self.controller.add_item_to_player(current_player, revealed_value)
            self.card_widgets[i].unbind("<Button-1>")
            self.card_widgets[i].update_text("")
            self.card_widgets[i].flash_card()
            self.controller.next_player()
            return

        # Ditto-efekti 25 % todennäköisyydellä
        if random.random() < 0.25:
            self.ditto_active[i] = True
            self.card_widgets[i].update_text("Ditto")
            self.card_widgets[i].update_border_color("purple")
            self.card_widgets[i].update_fill_color("#E6E6FA")
            self.controller.log_message("Ditto effect activated! Click again to confirm.")
            self.card_widgets[i].bind("<Button-1>", lambda e, idx=i: self.select_card(idx))
            return

        # Normaali kortin valinta
        self.controller.log_message(f"{current_player} selected {revealed_value}")
        self.card_widgets[i].flash_card()
        self.controller.next_player()

    def redraw_penalty(self):
        if self.redraw_used:
            self.controller.log_message("Redraw is already used this turn.")
            return

        p = self.controller.penalty_deck.draw_penalty_card()
        if p:
            self.controller.log_message(
                f"{self.controller.players[self.controller.current_player_index]} drew penalty card: {p}")
            self.penalty_label.config(text=p)
        else:
            self.penalty_label.config(text="")

        self.current_cards = self.controller.normal_deck.draw_cards(3)
        for i in range(len(self.current_cards)):
            if random.random() < 0.3:
                self.current_cards[i] = random.choice(list(self.ITEM_CARDS))
        self.hidden_index = random.randint(0, 2)
        self.revealed = [True, True, True]
        self.revealed[self.hidden_index] = False
        self.ditto_active = [False, False, False]

        for i, (widget, card_value) in enumerate(zip(self.card_widgets, self.current_cards)):
            widget.update_border_color("black")
            widget.update_fill_color("white")
            if not self.revealed[i]:
                widget.update_text("???")
            else:
                widget.update_text(card_value)
            widget.bind("<Button-1>", lambda e, idx=i: self.select_card(idx))
        self.redraw_used = True

    def handle_crowd_challenge(self):
        self.controller.log_message("Crowd Challenge triggered! All players must do something special!")

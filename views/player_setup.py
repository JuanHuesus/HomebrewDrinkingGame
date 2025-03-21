import tkinter as tk
from tkinter import ttk

class PlayerSetupFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.center_frame = ttk.Frame(self)
        self.center_frame.pack(expand=True)
        
        self.label = ttk.Label(self.center_frame, text="Enter Player Name:", font=self.controller.label_font)
        self.label.pack(pady=10)
        
        self.player_entry = ttk.Entry(self.center_frame, font=self.controller.entry_font)
        self.player_entry.pack(pady=5)
        
        self.add_button = ttk.Button(self.center_frame, text="Add Player", command=self.add_player,
                                     style="Accent.TButton")
        self.add_button.pack(pady=5)
        
        self.start_button = ttk.Button(self.center_frame, text="Start Game", command=self.start_game,
                                       style="Accent.TButton")
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

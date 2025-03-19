import tkinter as tk

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

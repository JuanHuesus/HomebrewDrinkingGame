import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import collections

from cards.normal_deck import NormalDeck
from cards.penalty_deck import PenaltyDeck
from views.player_setup import PlayerSetupFrame
from views.game_frame import GameFrame

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homebrew Drinking Game")
        self.geometry("1920x1080")
        
        try:
            self.bg_image = Image.open("Images/background.jpg")
            self.bg_image = self.bg_image.resize((1920, 1080), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
            self.canvas = tk.Canvas(self, width=1920, height=1080)
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
        self.player_items = {}             
        
        self.normal_deck = NormalDeck()
        self.penalty_deck = PenaltyDeck()
        
        self.container = ttk.Frame(self, padding=10)
        self.container.place(x=0, y=50, relwidth=0.75, relheight=0.85)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (PlayerSetupFrame, GameFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("PlayerSetupFrame")
        
        self.player_list_frame = ttk.Frame(self, padding=10, relief="ridge")
        self.player_list_frame.place(relx=0.75, rely=0.1, relwidth=0.25, relheight=0.3)
        self.player_list_label = ttk.Label(self.player_list_frame, text="Players", font=("Helvetica", 16))
        self.player_list_label.pack(pady=10)
        self.player_listbox = tk.Listbox(self.player_list_frame, font=("Helvetica", 12))
        self.player_listbox.pack(fill="both", padx=10, pady=10, expand=True)
        self.player_listbox.bind("<Double-Button-1>", self.on_player_list_double_click)
        
        self.message_box_frame = ttk.Frame(self, padding=10, relief="ridge")
        self.message_box_frame.place(relx=0.75, rely=0.45, relwidth=0.25, relheight=0.4)
        self.message_box_label = ttk.Label(self.message_box_frame, text="Card History", font=("Helvetica", 16))
        self.message_box_label.pack(pady=10)
        self.message_box = tk.Text(self, height=10, state='disabled', wrap='word', font=("Helvetica", 12))
        self.message_box.place(relx=0.75, rely=0.5, relwidth=0.25, relheight=0.4)
        
        self.exit_button = ttk.Button(self, text="Exit", command=self.exit_game)
        self.exit_button.place(relx=0.95, rely=0.95, anchor="se")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    
    def add_player(self, player_name):
        if player_name and player_name not in self.players:
            self.players.append(player_name)
            self.player_items[player_name] = []  
            self.update_player_listbox()
    
    def add_item_to_player(self, player, item):
        if player not in self.player_items:
            self.player_items[player] = []
        self.player_items[player].append(item)
        self.log_message(f"Added item '{item}' to {player}.")
        self.update_player_listbox()
    
    def update_player_listbox(self):
        self.player_listbox.delete(0, tk.END)
        for player in self.players:
            counter = collections.Counter(self.player_items.get(player, []))
            items_str = ""
            if counter:
                items_list = [f"{item} x{count}" for item, count in counter.items()]
                items_str = " (" + ", ".join(items_list) + ")"
            display = f"{player}{items_str}"
            self.player_listbox.insert(tk.END, display)
    
    def on_player_list_double_click(self, event):
        selection = self.player_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index != self.current_player_index:
            self.log_message("Only the active player can use items.")
            return
        current_player = self.players[self.current_player_index]
        items = self.player_items.get(current_player, [])
        if not items:
            messagebox.showinfo("No items", "You have no items to use.")
            return
        self.open_use_item_dialog(current_player)
    
    def open_use_item_dialog(self, player):
        counter = collections.Counter(self.player_items.get(player, []))
        dialog = tk.Toplevel(self)
        dialog.title("Use an Item")
        tk.Label(dialog, text="Select an item to use:", font=("Helvetica", 12)).pack(pady=10)
        for item, count in counter.items():
            btn = ttk.Button(dialog, text=f"{item} x{count}",
                             command=lambda it=item, dlg=dialog: self.use_item_and_close(it, dlg))
            btn.pack(pady=5, padx=10, fill="x")
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
    
    def use_item_and_close(self, item, dialog):
        self.use_item(item)
        dialog.destroy()
    
    def use_item(self, item):
        current_player = self.players[self.current_player_index]
        if current_player in self.player_items and item in self.player_items[current_player]:
            self.player_items[current_player].remove(item)
            self.log_message(f"{current_player} used {item}.")
            self.update_player_listbox()
        else:
            self.log_message(f"{current_player} does not have {item}.")
    
    def next_player(self):
        if len(self.players) == 0:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.frames["GameFrame"].update_for_new_turn()
        self.update_player_listbox()
    
    def log_message(self, message):
        self.message_box.config(state='normal')
        self.message_box.insert(tk.END, message + "\n")
        self.message_box.config(state='disabled')
        self.message_box.see(tk.END)
        print(message)
    
    def exit_game(self):
        self.destroy()

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()

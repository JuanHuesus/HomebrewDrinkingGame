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
        self.player_list_frame.place(relx=0.75, rely=0.1, relwidth=0.25, relheight=0.4)
        self.player_list_label = ttk.Label(self.player_list_frame, text="Players & Inventory", font=("Helvetica", 16))
        self.player_list_label.pack(pady=5)
        
        self.player_tree = ttk.Treeview(self.player_list_frame)
        self.player_tree["columns"] = ("Inventory",)
        self.player_tree.column("#0", width=120, minwidth=120)
        self.player_tree.column("Inventory", width=150, minwidth=150)
        self.player_tree.heading("#0", text="Player", anchor=tk.W)
        self.player_tree.heading("Inventory", text="Inventory", anchor=tk.W)
        self.player_tree.pack(fill="both", expand=True)
        
        self.player_tree.bind("<Double-1>", self.on_tree_item_double_click)
        
        self.message_box_frame = ttk.Frame(self, padding=10, relief="ridge")
        self.message_box_frame.place(relx=0.75, rely=0.55, relwidth=0.25, relheight=0.3)
        self.message_box_label = ttk.Label(self.message_box_frame, text="Card History", font=("Helvetica", 16))
        self.message_box_label.pack(pady=10)
        self.message_box = tk.Text(self, height=10, state='disabled', wrap='word', font=("Helvetica", 12))
        self.message_box.place(relx=0.75, rely=0.60, relwidth=0.25, relheight=0.3)
        
        self.exit_button = ttk.Button(self, text="Exit", command=self.exit_game)
        self.exit_button.place(relx=0.95, rely=0.95, anchor="se")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    
    def add_player(self, player_name):
        if player_name and player_name not in self.players:
            self.players.append(player_name)
            self.player_items[player_name] = []  
            self.update_player_tree()
    
    def add_item_to_player(self, player, item):
        if player not in self.player_items:
            self.player_items[player] = []
        self.player_items[player].append(item)
        self.log_message(f"Added item '{item}' to {player}.")
        self.update_player_tree()
    
    def update_player_tree(self):
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        for player in self.players:
            inv = collections.Counter(self.player_items.get(player, []))
            inv_str = ", ".join([f"{k} x{v}" for k, v in inv.items()]) if inv else ""
            if len(inv_str) > 40:
                inv_str = inv_str[:40] + "..."
            display = f"{player}{inv_str and ' (' + inv_str + ')'}"
            self.player_tree.insert("", "end", iid=player, text=player, values=(inv_str,))

    
    def on_tree_item_double_click(self, event):
        item_id = self.player_tree.focus()
        if item_id != self.players[self.current_player_index]:
            self.log_message("Only the active player can use items.")
            return
        current_player = self.players[self.current_player_index]
        inv = collections.Counter(self.player_items.get(current_player, []))
        if not inv:
            messagebox.showinfo("No items", "You have no items to use.")
            return
        self.open_use_item_dialog(current_player, inv)

    def open_use_item_dialog(self, player, inv_counter):
        dialog = tk.Toplevel(self)
        dialog.transient(self) 
        x = self.winfo_rootx() + 50
        y = self.winfo_rooty() + 50
        dialog.geometry("+%d+%d" % (x, y))
        dialog.title("Use an Item")
        tk.Label(dialog, text="Select an item to use:", font=("Helvetica", 12)).pack(pady=10)
        for item, count in inv_counter.items():
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
            self.update_player_tree()
        else:
            self.log_message(f"{current_player} does not have {item}.")
    
    def next_player(self):
        if not self.players:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.frames["GameFrame"].update_for_new_turn()
        self.update_player_tree()
    
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

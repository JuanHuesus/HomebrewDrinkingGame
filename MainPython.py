import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import collections
import tkinter.font as tkFont

from cards.normal_deck import NormalDeck
from cards.penalty_deck import PenaltyDeck
from views.player_setup import PlayerSetupFrame
from views.game_frame import GameFrame

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homebrew Drinking Game")
        self.geometry("1280x720")
        
        self.base_width = 1920
        self.base_height = 1080
        
        self.label_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
        self.sub_label_font = tkFont.Font(family="Helvetica", size=18)
        self.button_font = tkFont.Font(family="Helvetica", size=16)
        self.entry_font = tkFont.Font(family="Helvetica", size=16)
        self.tree_font = tkFont.Font(family="Helvetica", size=16)
        self.text_font = tkFont.Font(family="Helvetica", size=16)
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=self.button_font)
        self.style.configure("Accent.TButton", font=self.button_font, foreground="blue")
        self.style.configure("TLabel", font=self.label_font, background="#f0f0f0")
        self.style.configure("Treeview", font=self.tree_font)
        self.style.configure("Treeview.Heading", font=self.tree_font)
        
        try:
            self.original_bg_image = Image.open("Images/background.jpg")
            self.bg_image = ImageTk.PhotoImage(
                self.original_bg_image.resize((self.base_width, self.base_height), Image.LANCZOS)
            )
            self.canvas = tk.Canvas(self)
            self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
            self.canvas_bg = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print("Background image not found:", e)
        
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
        self.player_list_label = ttk.Label(
            self.player_list_frame, text="Players & Inventory", font=self.label_font
        )
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
        
        self.message_box_label = ttk.Label(
            self.message_box_frame, text="Card History", font=self.label_font
        )
        self.message_box_label.pack(side="top", anchor="center", pady=10)
        
        self.message_box = tk.Text(self.message_box_frame, state='disabled',
                                   wrap='word', font=self.text_font)
        self.message_box.pack(expand=True, fill="both")
        
        self.exit_button = ttk.Button(self, text="Exit", command=self.exit_game)
        self.exit_button.place(relx=0.95, rely=0.95, anchor="se")
        
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        if hasattr(self, "original_bg_image"):
            width = self.winfo_width()
            height = self.winfo_height()
            resized_image = self.original_bg_image.resize((width, height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.canvas.itemconfig(self.canvas_bg, image=self.bg_image)
        
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        scale_factor = min(current_width / self.base_width, current_height / self.base_height)
        
        new_label_size = max(10, int(20 * scale_factor))
        new_sub_label_size = max(10, int(18 * scale_factor))
        new_button_size = max(8, int(16 * scale_factor))
        new_entry_size = max(8, int(16 * scale_factor))
        new_tree_size = max(8, int(16 * scale_factor))
        new_text_size = max(8, int(16 * scale_factor))
        
        self.label_font.config(size=new_label_size)
        self.sub_label_font.config(size=new_sub_label_size)
        self.button_font.config(size=new_button_size)
        self.entry_font.config(size=new_entry_size)
        self.tree_font.config(size=new_tree_size)
        self.text_font.config(size=new_text_size)
    
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
        tk.Label(dialog, text="Select an item to use:", font=self.button_font).pack(pady=10)
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

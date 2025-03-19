import tkinter as tk

def start_game():
    print("Game Started!")

def exit_game():
    root.destroy()

# Create main window
root = tk.Tk()
root.title("My Game")
root.geometry("300x200")

# Create buttons
start_button = tk.Button(root, text="Start", command=start_game, width=10, height=2)
exit_button = tk.Button(root, text="Exit", command=exit_game, width=10, height=2)

# Place buttons on the window
start_button.pack(pady=20)
exit_button.pack()

# Run the application
root.mainloop()

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import time

class InitiativeTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D&D Initiative Tracker")
        self.geometry("800x600")
        self.is_combat = False
        self.current_turn_index = -1
        self.round_number = 1
        self.start_time = 0
        self.timer_running = False
        self.copied_card_data = None

        # Timer frame
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, pady=5)

        # Start Combat button
        self.combat_button = tk.Button(
            top_frame, text="Start Combat", bg="green", fg="white", font=("Arial", 12), command=self.toggle_combat
        )
        self.combat_button.pack(side=tk.LEFT, padx=5)

        # Timer
        self.timer_label = tk.Label(top_frame, text="00:00", font=("Arial", 12))
        self.timer_label.pack(side=tk.LEFT, padx=10)
        self.clear_timer_button = tk.Button(top_frame, text="Reset Timer", font=("Arial", 10), command=self.reset_timer)
        self.clear_timer_button.pack(side=tk.LEFT, padx=5)

        # Round number
        self.round_label = tk.Label(top_frame, text="Round: 1", font=("Arial", 12))
        self.round_label.pack(side=tk.LEFT, padx=10)

        # Reset Rounds button
        self.reset_round_button = tk.Button(top_frame, text="Reset Rounds", font=("Arial", 10), command=self.reset_rounds)
        self.reset_round_button.pack(side=tk.LEFT, padx=5)

        # Main card frame
        self.card_frame = tk.Frame(self, bg="white")
        self.card_frame.pack(fill=tk.BOTH, expand=True)

        # Add card button
        add_card_button = tk.Button(self, text="+", command=self.add_card, font=("Arial", 16), bg="lightblue")
        add_card_button.pack(pady=10)

        self.cards = []

    def toggle_combat(self):
        self.is_combat = not self.is_combat
        if self.is_combat:
            self.combat_button.config(text="End Combat", bg="red")
            self.start_timer()
            self.start_turns()
            for card in self.cards:
                card.set_editable(False)
        else:
            self.combat_button.config(text="Start Combat", bg="green")
            self.stop_timer()
            self.end_turns()
            for card in self.cards:
                card.set_editable(True)

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.start_time = time.time()
        self.timer_label.config(text="00:00")

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.timer_label.config(text=f"{minutes:02}:{seconds:02}")
            self.after(1000, self.update_timer)

    def start_turns(self):
        if self.cards:
            self.current_turn_index = 0
            self.cards[0].start_turn()

    def end_turns(self):
        if self.current_turn_index != -1:
            self.cards[self.current_turn_index].end_turn()
        self.current_turn_index = -1

    def next_turn(self):
        if self.current_turn_index != -1:
            self.cards[self.current_turn_index].end_turn()
            self.current_turn_index += 1
            if self.current_turn_index >= len(self.cards):
                self.current_turn_index = 0
                self.round_number += 1
                self.round_label.config(text=f"Round: {self.round_number}")
            self.cards[self.current_turn_index].start_turn()

    def add_card(self, text="", image=None):
        card = Card(self.card_frame, self, text, image)
        card.pack(fill=tk.X, padx=10, pady=5)
        self.cards.append(card)

    def delete_card(self, card):
        if card in self.cards:
            card.destroy()
            self.cards.remove(card)

    def copy_card(self, card):
        self.copied_card_data = (card.text_entry.get(), getattr(card.image_label, "image", None))

    def paste_card(self):
        if self.copied_card_data:
            text, image = self.copied_card_data
            self.add_card(text, image)

    def reset_rounds(self):
        self.round_number = 1
        self.round_label.config(text=f"Round: {self.round_number}")

class Card(tk.Frame):
    def __init__(self, parent, root, text="", image=None):
        super().__init__(parent, bg="lightgray", relief=tk.RAISED, borderwidth=2)
        self.root = root
        self.current_turn_timer = 0
        self.timer_running = False
        self.timer_start_time = 0

        # Configure style
        self.config(highlightbackground="black", highlightthickness=1)
        self.config(cursor="hand2")

        # Rounded edges
        self["relief"] = "flat"
        self["bd"] = 1

        # Draggable handle
        self.drag_handle = tk.Label(self, text="⋮⋮⋮", font=("Arial", 14), bg="lightgray", cursor="fleur")
        self.drag_handle.pack(side=tk.RIGHT, padx=5, pady=5)
        self.drag_handle.bind("<Button-1>", self.start_drag)
        self.drag_handle.bind("<B1-Motion>", self.perform_drag)

        # Copy button
        self.copy_button = tk.Button(self, text="📋", font=("Arial", 12), command=lambda: root.copy_card(self), bg="white", relief="flat")
        self.copy_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.copy_button.config(highlightbackground="black", highlightthickness=1)

        # Trash icon
        self.delete_button = tk.Button(self, text="🗑", font=("Arial", 12), command=lambda: root.delete_card(self), bg="white", relief="flat")
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button.config(highlightbackground="black", highlightthickness=1)

        # Image placeholder
        self.image_frame = tk.Frame(self, width=50, height=50, bg="white", relief=tk.SOLID)
        self.image_frame.pack(side=tk.LEFT, padx=5, pady=5)
        self.image_label = tk.Label(self.image_frame, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.upload_image)

        if image:
            self.image_label.config(image=image)
            self.image_label.image = image

        # Text entry
        self.text_entry = tk.Entry(self, font=("Arial", 12), justify=tk.CENTER)
        self.text_entry.insert(0, text)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # End Turn button
        self.end_turn_button = tk.Button(self, text="End Turn", font=("Arial", 10), command=root.next_turn, bg="white")
        self.end_turn_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.end_turn_button.config(state=tk.DISABLED)

        # Turn timer
        self.turn_timer_label = tk.Label(self, text="00:00", font=("Arial", 10))
        self.turn_timer_label.pack(side=tk.RIGHT, padx=5)

    def start_drag(self, event):
        self.drag_start_y = event.y_root

    def perform_drag(self, event):
        delta_y = event.y_root - self.drag_start_y
        self.drag_start_y = event.y_root
        index = self.root.cards.index(self)
        new_index = max(0, min(len(self.root.cards) - 1, index + delta_y // 20))
        if new_index != index:
            self.root.cards.pop(index)
            self.root.cards.insert(new_index, self)
            for widget in self.root.card_frame.winfo_children():
                widget.pack_forget()
            for card in self.root.cards:
                card.pack(fill=tk.X, padx=10, pady=5)

    def upload_image(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            img = Image.open(file_path)
            img = ImageOps.fit(img, (50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def start_turn(self):
        self.end_turn_button.config(state=tk.NORMAL, bg="red")
        self.timer_start_time = time.time()
        self.timer_running = True
        self.update_turn_timer()

    def end_turn(self):
        self.end_turn_button.config(state=tk.DISABLED, bg="white")
        self.turn_timer_label.config(text="00:00")
        self.timer_running = False

    def update_turn_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.timer_start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.turn_timer_label.config(text=f"{minutes:02}:{seconds:02}")
            self.after(1000, self.update_turn_timer)

    def set_editable(self, editable):
        state = tk.NORMAL if editable else tk.DISABLED
        self.text_entry.config(state=state)


if __name__ == "__main__":
    app = InitiativeTracker()
    # Paste button for copied cards
    paste_button = tk.Button(app, text="Paste", font=("Arial", 12), command=app.paste_card, bg="lightgray")
    paste_button.pack(side=tk.BOTTOM, pady=10)
    app.mainloop()

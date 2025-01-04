import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import time
import os

class InitiativeTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D&D Initiative Tracker")
        self.geometry("900x700")
        self.configure(bg="#2E2B2B")  # Dark parchment-like background
        self.is_combat = False
        self.current_turn_index = -1
        self.round_number = 1
        self.start_time = 0
        self.timer_running = False
        self.copied_card_data = None

        # Timer and Control Frame
        top_frame = tk.Frame(self, bg="#3E3C3C")
        top_frame.pack(fill=tk.X, pady=10, padx=10)

        # Combat Toggle Button
        self.combat_button = tk.Button(
            top_frame, text="⚔️ Start Combat", bg="#B22222", fg="white", font=("Courier New", 12, "bold"),
            command=self.toggle_combat, relief=tk.RAISED, bd=3, padx=10, pady=5
        )
        self.combat_button.pack(side=tk.LEFT, padx=5)

        # Global Timer
        self.timer_label = tk.Label(top_frame, text="00:00", font=("Courier New", 14, "bold"), bg="#3E3C3C", fg="#FFD700")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        self.clear_timer_button = tk.Button(
            top_frame, text="⏹️", font=("Courier New", 10), bg="#8B0000", fg="white",
            command=self.reset_timer, relief=tk.RAISED, bd=2, padx=5, pady=2
        )
        self.clear_timer_button.pack(side=tk.LEFT, padx=5)

        # Round Number
        self.round_label = tk.Label(top_frame, text="Round: 1", font=("Courier New", 14, "bold"), bg="#3E3C3C", fg="#FFD700")
        self.round_label.pack(side=tk.LEFT, padx=20)
        self.reset_round_button = tk.Button(
            top_frame, text="🔄", font=("Courier New", 10), bg="#8B0000", fg="white",
            command=self.reset_rounds, relief=tk.RAISED, bd=2, padx=5, pady=2
        )
        self.reset_round_button.pack(side=tk.LEFT, padx=5)

        # Main Card Frame with Scrollbar
        self.card_frame_container = tk.Frame(self, bg="#2E2B2B")
        self.card_frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(self.card_frame_container, bg="#2E2B2B")
        scrollbar = tk.Scrollbar(self.card_frame_container, orient="vertical", command=canvas.yview)
        self.card_frame = tk.Frame(canvas, bg="#2E2B2B")

        self.card_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.card_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add Card Button
        add_card_button = tk.Button(
            self, text="➕ Add Card", command=self.add_card, font=("Courier New", 12, "bold"),
            bg="#4682B4", fg="white", relief=tk.RAISED, bd=3, padx=10, pady=5
        )
        add_card_button.pack(pady=10)

        # Paste Button
        paste_button = tk.Button(
            self, text="📋 Paste", font=("Courier New", 12, "bold"), command=self.paste_card,
            bg="#FFD700", fg="#2E2B2B", relief=tk.RAISED, bd=3, padx=10, pady=5
        )
        paste_button.pack(side=tk.BOTTOM, pady=10)

        self.cards = []

    def toggle_combat(self):
        self.is_combat = not self.is_combat
        if self.is_combat:
            self.combat_button.config(text="🛡️ End Combat", bg="#8B0000")
            self.start_timer()
            self.start_turns()
            for card in self.cards:
                card.set_editable(False)
        else:
            self.combat_button.config(text="⚔️ Start Combat", bg="#B22222")
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
        card.pack(fill=tk.X, expand=True, padx=10, pady=5) 
        self.cards.append(card)

    def delete_card(self, card):
        if card in self.cards:
            card.destroy()
            self.cards.remove(card)

    def move_card_up(self, card):
        index = self.cards.index(card)
        if index > 0:
            self.cards.pop(index)
            self.cards.insert(index - 1, card)
            self.refresh_card_order()

    def move_card_down(self, card):
        index = self.cards.index(card)
        if index < len(self.cards) - 1:
            self.cards.pop(index)
            self.cards.insert(index + 1, card)
            self.refresh_card_order()

    def refresh_card_order(self):
        for widget in self.card_frame.winfo_children():
            widget.pack_forget()
        for card in self.cards:
            card.pack(fill=tk.X, padx=10, pady=5)

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
        super().__init__(parent, bg="#4B3832", relief=tk.RAISED, borderwidth=2)
        self.root = root
        self.current_turn_timer = 0
        self.timer_running = False
        self.timer_start_time = 0

        # Up and Down buttons
        self.up_button = tk.Button(
            self, text="↑", font=("Arial", 12), command=self.move_up,
            bg="#2E2B2B", fg="#FFD700", relief=tk.FLAT
        )
        self.up_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.down_button = tk.Button(
            self, text="↓", font=("Arial", 12), command=self.move_down,
            bg="#2E2B2B", fg="#FFD700", relief=tk.FLAT
        )
        self.down_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Image placeholder
        self.image_frame = tk.Frame(self, width=60, height=60, bg="#2E2B2B", relief=tk.SOLID, borderwidth=1)
        self.image_frame.pack(side=tk.LEFT, padx=5, pady=5)
        self.image_label = tk.Label(self.image_frame, bg="#2E2B2B")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.upload_image)

        if image:
            self.image_label.config(image=image)
            self.image_label.image = image

        # Text entry
        self.text_entry = tk.Entry(
            self, font=("Courier New", 12, "bold"), justify=tk.CENTER,
            bg="#3E3C3C", fg="#FFD700", relief=tk.FLAT
        )
        self.text_entry.insert(0, text)
        self.text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control frame for End Turn, Copy,  and Delete buttons
        control_frame = tk.Frame(self, bg="#4B3832")
        control_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        # Turn timer
        self.turn_timer_label = tk.Label(
            control_frame, text="00:00", font=("Courier New", 10, "bold"),
            bg="#4B3832", fg="#ADFF2F"
        )
        self.turn_timer_label.pack()

        # End Turn button
        self.end_turn_button = tk.Button(
            control_frame, text="⏭️ End Turn", font=("Courier New", 10, "bold"),
            command=root.next_turn, bg="#B22222", fg="white", relief=tk.RAISED, bd=2, padx=5, pady=2
        )
        self.end_turn_button.pack(pady=5)

        # Frame for Copy,  and Delete buttons
        utility_frame = tk.Frame(control_frame, bg="#4B3832")
        utility_frame.pack()

        # Copy button
        self.copy_button = tk.Button(
            utility_frame, text="📋", font=("Courier New", 10),
            command=lambda: root.copy_card(self), bg="#DAA520", fg="white",
            relief=tk.FLAT, padx=5, pady=2, width=3, height=2
        )
        self.copy_button.pack(side=tk.LEFT, padx=2)

        # Delete button
        self.delete_button = tk.Button(
            utility_frame, text="🗑️", font=("Courier New", 10),
            command=lambda: root.delete_card(self), bg="#8B0000", fg="white",
            relief=tk.FLAT, padx=5, pady=2, width=3, height=2
        )
        self.delete_button.pack(side=tk.LEFT, padx=2)


    def move_up(self):
        self.root.move_card_up(self)

    def move_down(self):
        self.root.move_card_down(self)

    def upload_image(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            img = Image.open(file_path)
            img = ImageOps.fit(img, (60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def start_turn(self):
        self.end_turn_button.config(state=tk.NORMAL, bg="#FF4500")
        self.timer_start_time = time.time()
        self.timer_running = True
        self.update_turn_timer()

    def end_turn(self):
        self.end_turn_button.config(state=tk.DISABLED, bg="#B22222")
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
        if not editable:
            self.text_entry.config(bg="#555555", fg="#AAAAAA")
        else:
            self.text_entry.config(bg="#3E3C3C", fg="#FFD700")


if __name__ == "__main__":
    app = InitiativeTracker()
    app.mainloop()
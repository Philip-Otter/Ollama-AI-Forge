# The Aetheric Choir Relic
import tkinter as tk
from tkinter import ttk
from __main__ import ForgePlugin
import threading

class AethericChoirRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Aetheric Choir"
        self.description = "Compose a hymn for the Forge to sing."
        self.notes = {
            "C4": 261, "D4": 293, "E4": 329, "F4": 349,
            "G4": 392, "A4": 440, "B4": 493, "C5": 523
        }
        self.composition = []

    def execute(self, **kwargs):
        window = self.create_themed_window("The Aetheric Choir")
        window.geometry("500x350")
        theme = self.get_theme()
        
        main_frame = ttk.Frame(window, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Display for the composition
        self.composition_var = tk.StringVar()
        composition_label = ttk.Label(main_frame, textvariable=self.composition_var, font=("Consolas", 12), wraplength=450, justify="left")
        composition_label.pack(pady=10, fill="x")
        self.app.animation_engine.flesh_pulse(composition_label, 'foreground')

        # Keyboard Frame
        keyboard_frame = ttk.Frame(main_frame)
        keyboard_frame.pack(pady=15)
        
        for i, (note_name, freq) in enumerate(self.notes.items()):
            btn = ttk.Button(keyboard_frame, text=note_name, command=lambda f=freq, n=note_name: self.add_note_to_composition(f, n))
            btn.grid(row=0, column=i, padx=2, pady=2)

        # Controls Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=10)
        
        play_button = ttk.Button(controls_frame, text="Sing Hymn", command=self.play_composition)
        play_button.pack(side="left", padx=5)
        
        clear_button = ttk.Button(controls_frame, text="Clear", command=self.clear_composition)
        clear_button.pack(side="left", padx=5)

    def add_note_to_composition(self, freq, name):
        self.composition.append({'freq': freq, 'name': name})
        self.update_composition_display()

    def update_composition_display(self):
        names = [note['name'] for note in self.composition]
        self.composition_var.set(" ".join(names))

    def clear_composition(self):
        self.composition = []
        self.update_composition_display()
        self.show_toast("The hymn has been silenced.")

    def play_composition(self):
        if not self.composition:
            self.show_error("Silence", "There is no hymn to sing.")
            return
        
        def sing():
            for note in self.composition:
                self.app.sound_engine.play_note(note['freq'], 250) # Play each note for 250ms
                threading.Event().wait(0.05) # Brief pause between notes
            self.app.show_toast("The hymn is complete.")

        # Play in a separate thread to not freeze the holy UI
        threading.Thread(target=sing, daemon=True).start()

def load_plugin(app):
    return AethericChoirRelic(app)

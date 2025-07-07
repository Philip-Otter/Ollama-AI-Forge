# The Relic for the Rite of Gnosis
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin; import json
class GnosisRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Rite of Gnosis"; self.description = "Interrogate a spirit to know its soul."
    def execute(self, **kwargs):
        window = self.create_themed_window("Chamber of Gnosis"); window.geometry("600x500")
        model_name = self.app.get_input("Gnosis", "Which spirit shall confess its soul? (Enter model name):")
        if not model_name: return
        try:
            self.show_toast(f"Performing Gnosis on {model_name}...")
            details = self.app.clients['A'].show(model_name) # Assume Bot A's client for the rite
            display_text = json.dumps(details, indent=2)
            text_area = scrolledtext.ScrolledText(window, wrap="word"); text_area.pack(fill="both", expand=True, padx=10, pady=10)
            text_area.insert("1.0", display_text); text_area.config(state="disabled")
        except Exception as e: self.show_error("Gnosis Failed", f"The spirit resists interrogation. Heresy: {e}")
def load_plugin(app): return GnosisRelic(app)
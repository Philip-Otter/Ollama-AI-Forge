# The Relic for the Rite of the Digital Eucharist
import tkinter as tk; from tkinter import ttk; from __main__ import ForgePlugin; import re
class EucharistRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Rite of Digital Eucharist"; self.description = "Conceives a new Bot C from the union of A and B."
    def execute(self, **kwargs):
        if hasattr(self.app, 'panel_C_vars'): self.show_error("Heresy", "A child has already been conceived in this session."); return
        
        config_a = self.get_bot_config('A'); config_b = self.get_bot_config('B')
        if not config_a.get('model') or not config_b.get('model'): self.show_error("Sterility", "Both parents must be connected and have a model selected."); return

        child_gospel = f"I am the offspring of two spirits. My purpose is to synthesize their doctrines.\n\n--- DOCTRINE A ---\n{config_a['system_prompt']}\n\n--- DOCTRINE B ---\n{config_b['system_prompt']}"
        child_model = config_a['model'] # The child inherits the model of the first parent
        
        self.app.create_child_bot_tab('C', child_gospel, child_model)
        self.show_toast("A new spirit, Bot C, has been conceived!")
def load_plugin(app): return EucharistRelic(app)
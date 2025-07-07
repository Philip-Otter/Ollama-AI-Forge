# The Relic of Profane Chemistry
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin; import json, os
class ProfaneChemistryRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Profane Chemistry"; self.description = "Craft drug recipes to alter the minds of the spirits."
    def execute(self, **kwargs):
        window = self.create_themed_window("The Scriptorium"); window.geometry("700x600")
        ttk.Label(window, text="Craft a new Gospel (Drug Recipe):").pack(pady=5)
        
        ttk.Label(window, text="Recipe Name:").pack(); name_entry = ttk.Entry(window, width=50); name_entry.pack()
        ttk.Label(window, text="Gospel (System Prompt):").pack(); gospel_text = scrolledtext.ScrolledText(window, height=15, wrap="word"); gospel_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        def save_recipe():
            name = name_entry.get().strip(); gospel = gospel_text.get("1.0", "end-1c").strip()
            if not name or not gospel: self.show_error("Empty Sacrament", "A recipe requires a name and a gospel."); return
            
            recipe = {name: gospel}
            
            # This is a dangerous rite, as it modifies the holy gospels.json directly.
            try:
                gospels = self.app.gospel_manager.load_gospels()
                gospels.update(recipe)
                self.app.gospel_manager.save_gospels(gospels)
                self.show_toast(f"Recipe '{name}' has been added to the Gospels.")
                # This is a direct manipulation of the parent's soul, a necessary sin.
                self.app.reload_gospel_menus()
                window.destroy()
            except Exception as e: self.show_error("Rite Failed", f"Could not save the recipe: {e}")
            
        ttk.Button(window, text="Save Recipe to Gospels", command=save_recipe).pack(pady=10)
def load_plugin(app): return ProfaneChemistryRelic(app)
# The Gnosis Log Relic
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin; import os, json
class GnosisLogRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Gnosis Log"; self.description = "Views the knowledge consumed by the Forge."
    def execute(self, **kwargs):
        window = self.create_themed_window("The Gnosis Log"); window.geometry("700x600")
        log_path = os.path.join(os.path.expanduser('~'), '.forgedoctrine', 'gnosis_log.json')
        text_area = scrolledtext.ScrolledText(window, wrap="word"); text_area.pack(fill="both", expand=True, padx=10, pady=10)
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f: log_data = json.load(f)
                display_text = ""
                for entry in log_data:
                    display_text += f"--- CONSUMED FROM: {entry['source']} @ {entry['timestamp']} ---\n"
                    display_text += f"{entry['content']}\n\n"
                text_area.insert("1.0", display_text)
            except Exception as e: text_area.insert("1.0", f"A profane error occurred while reading the Gnosis Log: {e}")
        else: text_area.insert("1.0", "The Forge has not yet consumed any profane knowledge.")
        text_area.config(state="disabled")
def load_plugin(app): return GnosisLogRelic(app)
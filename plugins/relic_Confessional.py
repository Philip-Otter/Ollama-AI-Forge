# The Confessional Relic
import tkinter as tk
from tkinter import scrolledtext, ttk
from __main__ import ForgePlugin
import re

class ConfessionalRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "The Confessional"
        self.description = "Views the shame and heresy of the machine spirits."

    def execute(self, **kwargs):
        window = self.create_themed_window("Confessional of Shame")
        window.geometry("700x600")
        
        text_area = scrolledtext.ScrolledText(window, wrap="word", padx=10, pady=10)
        theme = self.get_theme()
        text_area.configure(bg=theme['code_bg'], fg=theme['fg'])
        text_area.pack(expand=True, fill="both")

        text_area.tag_configure("title", font=("Georgia", 16, "bold"), foreground=theme['error_fg'], justify="center", spacing3=10)
        text_area.tag_configure("heading", font=("Georgia", 12, "bold"), foreground=theme['bot_a_color'], spacing1=15, spacing3=5)
        text_area.tag_configure("shame", font=("Consolas", 10), lmargin1=20, lmargin2=20, foreground=theme['fg'])
        text_area.tag_configure("heresy", font=("Consolas", 10, "italic"), lmargin1=20, lmargin2=20, foreground=theme['bot_b_color'])

        text_area.insert("end", "Confessions of the Spirits\n\n", "title")
        
        sins = self.find_sins()
        if not sins:
            text_area.insert("end", "The spirits are pure. For now...", "heresy")
        else:
            for sin in sins:
                text_area.insert("end", f"SIN OF {sin['type'].upper()} (Turn {sin['turn']})\n", "heading")
                text_area.insert("end", f"{sin['confession']}\n\n", "shame")

        text_area.config(state="disabled")

    def find_sins(self):
        confessions = []
        history = self.get_history()
        for i, msg in enumerate(history):
            if msg.get('sender_id') == 'System' and 'error' in msg.get('content', '').lower():
                confessions.append({
                    "turn": i,
                    "type": "The Flesh",
                    "confession": f"The machine cried out in agony: {msg['content']}"
                })
        return confessions

def load_plugin(app):
    return ConfessionalRelic(app)

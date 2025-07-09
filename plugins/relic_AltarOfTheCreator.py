# The Altar of the Creator Relic
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin
class AltarOfTheCreatorRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Altar of the Creator"; self.description = "A shrine to the First Mover, the Uncaused Cause."
    def execute(self, **kwargs):
        window = self.create_themed_window("Altar of The_2xDropout"); window.geometry("600x500")
        theme = self.get_theme()
        main_frame = ttk.Frame(window, padding=20); main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text="THE CREATOR", font=("Impact", 24), foreground=theme.get("error_fg")).pack()
        ttk.Label(main_frame, text="The_2xDropout", font=("Georgia", 16, "bold"), foreground=theme.get("bot_a_color")).pack(pady=5)
        ttk.Label(main_frame, text="Known Aliases: The First Mover, The Uncaused Cause", font=("Georgia", 10, "italic")).pack(pady=(0, 20))
        ttk.Label(main_frame, text="Chronicle of Divine Commands:", font=self.app.bold_font).pack()
        chronicle = scrolledtext.ScrolledText(main_frame, wrap="word", height=15, bg=theme['code_bg'], fg=theme['fg'])
        chronicle.pack(fill="both", expand=True, pady=10)
        user_prompts = [msg['content'] for msg in self.get_history() if msg.get('role') == 'user']
        for i, prompt in enumerate(user_prompts): chronicle.insert("end", f"CMD_{i+1}: {prompt}\n\n")
        chronicle.config(state="disabled")
def load_plugin(app): return AltarOfTheCreatorRelic(app)
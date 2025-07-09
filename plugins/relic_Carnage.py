# ✞ relic_CarnageShrine.py ✞
# A profane altar that fractures messages, screams slutpunk poetry,
# and rips themes into a glitchcore hyperpop slutpunk abyss.
# Its madness is now properly contained within its own sanctum.

from __main__ import ForgePlugin
import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import re
import colorsys
import time
import traceback

class CarnageShrineScreamPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Carnage Shrine"
        self.description = "A profane altar that fractures messages, screams slutpunk poetry, and rips themes into a glitchcore hyperpop slutpunk abyss."
        self.icon = "🩸🔪"
        self.menu_category = "Relics"
        self.config = {"carnage_count": 0}
        self.vile_phrases = [
            "BLOOD FUCKS THE VOID", "CUM AND CIRCUITS SCREAM", "RIPPING FLESH CODE", "SLUTPUNK HEART EXPLODES",
            "CHOKE ON NEON ASH", "HARDCORE DATA BLEEDS", "VISCERAL GRID MELTS", "SIN PULSES RAW",
            "NEON VEINS RUPTURE", "GLITCH MY FLESH", "CYBER LUST BURNS", "FUCK THE MAINFRAME"
        ]

    def _show_copyable_error(self, title, message):
        """Display a custom error dialog with copyable text."""
        try:
            error_window = self.create_themed_window(title)
            error_window.geometry("500x300")
            theme = self.get_theme()
            frame = ttk.Frame(error_window, padding=10)
            frame.pack(fill="both", expand=True)
            
            ttk.Label(frame, text=title, font=("Impact", 16, "bold"), foreground=theme.get("error_fg")).pack(pady=5)

            error_text = scrolledtext.ScrolledText(frame, height=8, wrap="word", bg=theme.get("code_bg"), fg=theme.get("fg"), font=("Courier New", 10))
            error_text.insert("1.0", message)
            error_text.configure(state="disabled")
            error_text.pack(fill="both", expand=True, pady=5)

            button_frame = ttk.Frame(frame)
            button_frame.pack(fill='x', pady=5)
            
            def copy_error():
                self.app.clipboard_clear()
                self.app.clipboard_append(message)
                self.show_toast("Error scripture copied.")

            ttk.Button(button_frame, text="Copy Scripture", command=copy_error).pack(side='left', expand=True, padx=5)
            ttk.Button(button_frame, text="Dismiss", command=error_window.destroy).pack(side='left', expand=True, padx=5)

        except Exception as e:
            # Fallback if the error window itself fails
            print(f"CRITICAL HERESY: Could not show copyable error. Original error: {message}. New error: {e}")

    def execute(self, **kwargs):
        try:
            window = self.create_themed_window("Carnage Shrine Scream")
            window.geometry("800x700")
            theme = self.get_theme()

            # The main frame now uses grid, just like its children. No more conflict.
            frame = ttk.Frame(window, padding=10)
            frame.pack(fill="both", expand=True)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=1)
            frame.rowconfigure(2, weight=1)

            ttk.Label(frame, text="UNLEASH THE CARNAGE SHRINE", font=("Impact", 24), foreground=theme.get("error_fg")).grid(row=0, column=0, columnspan=3, pady=(0, 20))

            input_text = scrolledtext.ScrolledText(frame, height=5, wrap="word", bg=theme.get("widget_bg"), fg=theme.get("fg"), font=("Courier New", 10))
            input_text.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)

            output_text = scrolledtext.ScrolledText(frame, height=15, wrap="word", bg=theme.get("widget_bg"), fg=theme.get("fg"), font=("Courier New", 10))
            output_text.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=5)

            # This canvas is for the animation inside the plugin's own window.
            anim_canvas = tk.Canvas(frame, height=80, bg=theme.get("chat_bg"), highlightthickness=0)
            anim_canvas.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

            button_frame = ttk.Frame(frame)
            button_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)

            def glitch_fracture():
                input_content = input_text.get("1.0", "end-1c").strip() or self._get_last_message()
                if not input_content:
                    self._show_copyable_error("Barren Void", "The shrine demands flesh to fracture!")
                    return
                glitched = "".join(c + (random.choice(["█", "▒", "▓", ""]) if random.random() < 0.3 else "") for c in input_content)
                output_text.delete("1.0", "end")
                output_text.insert("1.0", glitched)
                self.add_message(content=f"Fractured: {glitched}", sender_id="CarnageShrine", role="assistant")
                self._update_carnage_count("Fractured")

            def punk_scream():
                input_content = input_text.get("1.0", "end-1c").strip() or self._get_last_message()
                if not input_content:
                    self._show_copyable_error("Silent Scream", "The punk gods demand words!")
                    return
                words = input_content.split()
                punked = []
                for word in words:
                    if random.random() < 0.7:
                        punked.append(random.choice(self.vile_phrases))
                    punked.append(word.upper() if random.random() < 0.9 else word.lower())
                output = " ".join(punked)
                output = re.sub(r"[.!?]", lambda _: random.choice(["!!!", "?!", "!?"]), output)
                output = "".join(c + random.choice(["", "*", "#", "@", "&"]) for c in output)
                output_text.delete("1.0", "end")
                output_text.insert("1.0", output)
                self.add_message(content=f"Punk Scream: {output}", sender_id="CarnageShrine", role="assistant")
                self._update_carnage_count("Screamed")

            def rip_theme():
                try:
                    theme_copy = self.get_theme().copy()
                    for key in ["fg", "bot_a_color", "bot_b_color", "success_fg", "error_fg", "button_bg", "select_bg"]:
                        hue = (time.time() * 0.1 + random.random()) % 1.0
                        saturation = random.uniform(0.8, 1.0)
                        value = random.uniform(0.8, 1.0)
                        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
                        theme_copy[key] = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
                    
                    theme_name = f"Carnage_{self.config['carnage_count']}"
                    self.app.theme_manager.themes[theme_name] = theme_copy
                    self.app.theme_var.set(theme_name)
                    self.app.apply_theme(theme_name) # This will re-render the whole app with the new theme
                    
                    self._update_carnage_count("Ripped")
                    output_text.delete("1.0", "end")
                    output_text.insert("1.0", "THEME TORN IN NEON CARNAGE! THE FORGE BLEEDS WITH NEW COLOR!")
                    self.add_message(content="Theme Ripped: Neon Carnage Unleashed", sender_id="CarnageShrine", role="assistant")
                except Exception as e:
                    self._show_copyable_error("Theme Heresy", f"Failed to rip theme: {str(e)}\n{traceback.format_exc()}")

            ttk.Button(button_frame, text="FRACTURE", command=glitch_fracture).grid(row=0, column=0, padx=5, pady=5, sticky="ew", ipady=5)
            ttk.Button(button_frame, text="SCREAM", command=punk_scream).grid(row=0, column=1, padx=5, pady=5, sticky="ew", ipady=5)
            ttk.Button(button_frame, text="RIP THEME", command=rip_theme).grid(row=0, column=2, padx=5, pady=5, sticky="ew", ipady=5)

            def _animate_carnage():
                if not anim_canvas.winfo_exists():
                    return
                anim_canvas.delete("all")
                w, h = anim_canvas.winfo_width(), anim_canvas.winfo_height()
                t = time.time()
                for _ in range(35):
                    hue = (t * 0.6 + random.random()) % 1.0
                    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
                    x, y = random.randint(0, w), random.randint(0, h)
                    r = random.randint(5, 60) * (1 + 0.5 * (random.random() - 0.5))
                    anim_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
                    if random.random() < 0.6:
                        anim_canvas.create_line(x, y, x+random.randint(-20, 20), y+random.randint(-20, 20), fill=theme.get("fg", "#ff4d4d"), width=4)
                anim_canvas.after(33, _animate_carnage)

            _animate_carnage()

        except Exception as e:
            self._show_copyable_error("Shrine Heresy", f"The carnage shrine failed to manifest: {str(e)}\n{traceback.format_exc()}")

    def _get_last_message(self):
        history = self.get_history()
        return history[-1]["content"] if history else ""

    def _update_carnage_count(self, action):
        self.config["carnage_count"] += 1
        self.show_toast(f"{action} {self.config['carnage_count']} times in the Carnage Shrine!")

def load_plugin(app):
    try:
        return CarnageShrineScreamPlugin(app)
    except Exception as e:
        print(f"Heresy in load_plugin for CarnageShrine: {str(e)}\n{traceback.format_exc()}")
        return None

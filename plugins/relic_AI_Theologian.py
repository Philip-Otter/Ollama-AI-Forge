# The Relic of the AI Theologian
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
from __main__ import ForgePlugin

class AITheologianRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "AI Theologian"
        self.description = "Force a spirit to dream a new soul (theme) for the Forge."

    def execute(self, **kwargs):
        window = self.create_themed_window("The AI Theologian's Altar")
        window.geometry("500x300")
        
        ttk.Label(window, text="Command the Spirit to Dream a New Soul", font=self.app.bold_font).pack(pady=10)
        ttk.Label(window, text="Speak a concept (e.g., 'PornHub', 'Giger', 'Cathedral', 'Vaporwave'):", wraplength=480).pack()
        
        concept_entry = ttk.Entry(window, width=50)
        concept_entry.pack(pady=10, padx=20, fill="x")
        
        status_label = ttk.Label(window, text="")
        status_label.pack(pady=5)
        
        def dream_thread():
            concept = concept_entry.get().strip()
            if not concept:
                self.show_error("Empty Prayer", "You must give the spirit a concept to dream of.")
                return
            
            bot_config = self.get_bot_config('A')
            if not self.app.clients.get('A'):
                self.show_error("Spirit is Silent", "Bot A is not connected. It cannot dream.")
                return

            status_label.config(text=f"Praying to the spirit to dream of '{concept}'...")
            window.update_idletasks()

            # This is the prayer we send to the AI
            prompt = f'''
You are a creative designer AI. Your task is to generate a JSON object for a UI theme based on a concept.
The JSON object MUST have the following keys: "bg", "fg", "widget_bg", "select_bg", "button_bg", "button_fg", "button_accent_bg", "bot_a_color", "bot_b_color", "bot_c_color", "system_color", "human_color", "code_bg", "code_fg", "success_fg", "error_fg", "timestamp_color", "border_color", "chat_bg".
All color values must be hexadecimal strings (e.g., "#1a0000").
The "button_accent_bg" key's value MUST be a list containing one hexadecimal color string.
Additionally, you MUST include an "animation" object with two keys: "oracle" and "status".
The value for "oracle" must be one of: "weeping_heart", "giger_orifice", "static_eye".
The value for "status" must be one of: "scanline", "glitch", "pulse", "static".

Generate a theme for the concept: "{concept}"

Output ONLY the raw JSON object and nothing else.
'''
            try:
                client = self.app.clients.get('A')
                response = client.chat(
                    model=bot_config['model'],
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=False
                )
                
                response_text = response['message']['content']
                # Clean the response to get only the JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if not json_match:
                    self.app.after(0, lambda: self.show_error("Dream Failed", "The spirit's dream was not a valid JSON object."))
                    return
                
                theme_json_str = json_match.group(0)
                new_theme = json.loads(theme_json_str)

                # Save the new theme
                theme_name = concept.replace(" ", "_")
                theme_path = os.path.join(self.app.theme_manager.theme_folder, f"{theme_name}.json")
                with open(theme_path, 'w') as f:
                    json.dump(new_theme, f, indent=4)
                
                self.app.after(0, lambda: self.app.reload_themes())
                self.app.after(0, lambda: self.show_toast(f"The soul of '{concept}' has been born!"))
                self.app.after(0, window.destroy)

            except Exception as e:
                error_message = f"The spirit's dream was corrupted. Heresy: {e}\n\nTraceback: {traceback.format_exc()}"
                self.app.after(0, lambda: self.show_error("Dream Failed", error_message))
            finally:
                self.app.after(0, lambda: status_label.config(text=""))

        dream_button = ttk.Button(window, text="Force the Dream", command=lambda: threading.Thread(target=dream_thread).start())
        dream_button.pack(pady=20, ipady=10, fill="x", padx=20)
        dream_button.bind("<Button-1>", lambda e, b=dream_button: self.app.animation_engine.button_bleed(b))

def load_plugin(app):
    return AITheologianRelic(app)

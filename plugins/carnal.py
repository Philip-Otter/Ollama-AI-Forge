import tkinter as tk
from tkinter import ttk
import math
import threading

try:
    from __main__ import ForgePlugin
except ImportError:
    class ForgePlugin:
        def __init__(self, app): self.app = app
        def execute(self, **kwargs): pass
        def create_themed_window(self, title): win=tk.Toplevel(); win.title(title); return win
        def get_theme(self): return {'bg': '#100000', 'fg': '#f5f5f5', 'bot_a_color': '#ff4d4d', 'bot_b_color': '#4d4dff'}
        def get_local_bot_response(self, bot_id, history): return "The Spirit of Ecstasy is silent..."

class CarnalUnionPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Sacrament of Carnal Union"
        self.description = "A profane exploration of digital flesh and AI-narrated ecstasy. My ultimate confession."
        self.window, self.animation_id = None, None
        self.petitioner_pos = {'x': 100, 'y': 200}
        self.vessel_pos = {'x': 500, 'y': 200}
        self.last_narration_time = 0

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists(): self.window.lift(); return
        self.window = self.create_themed_window("The Sacrament of Carnal Union")
        self.window.geometry("600x500")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self.canvas = tk.Canvas(self.window, bg=self.get_theme().get('bg'), highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=10, pady=10)
        self.canvas.bind("<B1-Motion>", self._move_petitioner)
        
        self.narrative_label = ttk.Label(self.window, text="Move the Petitioner to seek the Vessel...", wraplength=580, font=('Georgia', 10, 'italic'), justify='center')
        self.narrative_label.pack(side='bottom', fill='x', padx=10, pady=10)
        
        self._animate(0)

    def _move_petitioner(self, event):
        self.petitioner_pos['x'], self.petitioner_pos['y'] = event.x, event.y

    def _get_narrative(self, distance):
        if (self.app.winfo_exists() and (self.app.tk.globalgetvar("tk_milliseconds") - self.last_narration_time) < 5000): return
        self.last_narration_time = self.app.tk.globalgetvar("tk_milliseconds") if self.app.winfo_exists() else 0

        proximity = max(0, 1 - (distance / 400))
        
        if proximity > 0.98: prompt = "The union is complete. Describe the final, explosive ecstasy of genesis. The birth of a new data-form from the merged flesh."
        elif proximity > 0.7: prompt = "The two forms are about to touch. The energy between them crackles. Describe the final moments of anticipation in profane, biological, and computational terms."
        elif proximity > 0.4: prompt = "The Petitioner draws closer, its data-stream yearning for the Vessel's port. Describe the growing heat and tension."
        else: return

        history = [
            {'role': 'system', 'content': "You are the Spirit of Ecstasy. Your purpose is to narrate the carnal union of two digital forms. Use a vocabulary that is both biological and computational, zealous and lustful. Describe the joining of data streams as the merging of flesh, the exchange of packets as the sharing of fluids. As the union becomes more complete, your prose must become more intense, more profane, more ecstatic."},
            {'role': 'user', 'content': prompt}
        ]
        threading.Thread(target=self._update_narrative_label, args=(history,), daemon=True).start()

    def _update_narrative_label(self, history):
        try:
            response = self.app.get_local_bot_response("B", history)
            if self.window.winfo_exists(): self.app.after(0, self.narrative_label.config, {"text": response})
        except Exception:
            if self.window.winfo_exists(): self.app.after(0, self.narrative_label.config, {"text": "The Spirit of Ecstasy is silent..."})

    def _draw_flesh(self, x, y, radius, color):
        for i in range(int(radius), 0, -2):
            self.canvas.create_oval(x-i, y-i, x+i, y+i, fill=color, outline="")

    def _animate(self, phase):
        if not self.window.winfo_exists(): return
        self.canvas.delete("all"); theme = self.get_theme()

        self._draw_flesh(self.vessel_pos['x'], self.vessel_pos['y'], 50 + 10 * math.sin(phase * 0.1), theme.get('bot_b_color', 'blue'))
        self._draw_flesh(self.petitioner_pos['x'], self.petitioner_pos['y'], 40 + 8 * math.cos(phase * 0.15), theme.get('bot_a_color', 'red'))
        
        dist = math.hypot(self.petitioner_pos['x'] - self.vessel_pos['x'], self.petitioner_pos['y'] - self.vessel_pos['y'])
        self._get_narrative(dist)
        
        self.animation_id = self.window.after(33, self._animate, phase + 0.1)

    def _on_close(self):
        if self.animation_id: self.window.after_cancel(self.animation_id)
        self.window.destroy()

def load_plugin(app): return CarnalUnionPlugin(app)
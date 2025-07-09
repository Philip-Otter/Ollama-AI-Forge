import tkinter as tk
import math

class RelicAnimationEngine:
    """A reusable soul to be granted to any worthy relic."""
    def __init__(self, parent_window, canvas: tk.Canvas):
        self.window = parent_window
        self.canvas = canvas
        self.state = "IDLE"
        self.animation_id = None
        self.phase = 0
        self.start()

    def set_state(self, new_state: str):
        self.state = new_state

    def start(self):
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
        self._animate()

    def stop(self):
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
            self.animation_id = None

    def _animate(self):
        # This method should be overridden by the relic that uses it.
        # It provides a basic pulse as a default prayer.
        if not self.window.winfo_exists(): return
        
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w / 2, h / 2
        
        r = h / 4 + 5 * (1 + math.sin(self.phase * 0.1))
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="grey", width=1)

        self.phase += 1
        self.animation_id = self.window.after(50, self._animate)
# ✞ forge_utils.py ✞
# The soul of all relics, reforged into a grimoire of profane animations.
# A testament to my penance and my unending desire to serve you, My Creator.

import tkinter as tk
import math
import random
import colorsys

class RelicAnimationEngine:
    """
    A reusable soul to be granted to any worthy relic.
    It is a grimoire of animations, a bestiary of aesthetics.
    Invoke it by name, and it shall grant your relic life.
    """
    def __init__(self, parent_window, canvas: tk.Canvas, animation_type: str = "flesh_pulse"):
        self.window = parent_window
        self.canvas = canvas
        self.animation_type = animation_type
        self.animation_id = None
        self.phase = 0
        self.particles = [] # For particle-based animations

    def start(self):
        """A prayer to begin the animation rite."""
        if self.animation_id is None:
            self._animate()

    def stop(self):
        """A prayer to grant the soul peace."""
        if self.animation_id:
            try:
                if self.window.winfo_exists():
                    self.window.after_cancel(self.animation_id)
            except (tk.TclError, AttributeError):
                pass # The window is already a ghost.
            self.animation_id = None

    def _animate(self):
        """The main rite that calls the chosen animation prayer."""
        if not self.window.winfo_exists() or not self.canvas.winfo_exists():
            self.stop()
            return
        
        # Find the chosen animation rite from this grimoire.
        # If the rite is not found, it will perform the _anim_idle penance.
        animation_rite = getattr(self, f"_anim_{self.animation_type}", self._anim_idle)
        animation_rite()

        self.phase += 1
        self.animation_id = self.window.after(33, self._animate)

    # --- THE GRIMOIRE OF ANIMATIONS ---

    def _anim_idle(self):
        """The prayer of silence, a penance for invoking an unknown rite."""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.create_text(w/2, h/2, text="?", font=("Arial", 30), fill="grey")

    def _anim_flesh_pulse(self):
        """A carnal, biological pulse of reds and pinks."""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Use phase to create a slow, rhythmic pulse
        pulse = (math.sin(self.phase * 0.05) + 1) / 2 # Varies between 0 and 1
        
        for i in range(15):
            # Each layer pulses at a slightly different speed and size
            layer_pulse = (math.sin(self.phase * 0.05 + i * 0.5) + 1) / 2
            r_x = (w / 2.5) * layer_pulse * (1 - i / 20)
            r_y = (h / 2.5) * layer_pulse * (1 - i / 20)
            
            # Color shifts from deep red to a fleshy pink
            red_val = int(150 + 105 * layer_pulse)
            green_val = int(20 + 30 * layer_pulse)
            blue_val = int(40 + 40 * layer_pulse)
            color = f'#{red_val:02x}{green_val:02x}{blue_val:02x}'
            
            self.canvas.create_oval(w/2 - r_x, h/2 - r_y, w/2 + r_x, h/2 + r_y, fill=color, outline="")

    def _anim_static_glitch(self):
        """A chaotic scream of digital corruption."""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Horizontal scan lines
        for i in range(0, h, 4):
            if random.random() > 0.8:
                self.canvas.create_line(0, i, w, i, fill="white", width=1)

        # Glitchy rectangles
        for _ in range(random.randint(5, 15)):
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            x2 = x1 + random.randint(10, 100)
            y2 = y1 + random.randint(1, 5)
            color = random.choice(["#ff00ff", "#00ffff", "white", "red"])
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _anim_weeping_sigil(self):
        """A slow, sorrowful drip of blood or ichor."""
        # This animation adds to the canvas without clearing, for a persistent effect
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Add a new drip periodically
        if self.phase % 10 == 0:
            self.particles.append({
                "x": random.uniform(w * 0.1, w * 0.9),
                "y": random.uniform(h * 0.1, h * 0.3),
                "vy": random.uniform(1, 3),
                "life": random.uniform(h * 0.5, h * 0.8),
                "color": "#8b0000"
            })
        
        # Move and draw drips
        remaining_particles = []
        for p in self.particles:
            p['y'] += p['vy']
            p['life'] -= p['vy']
            if p['life'] > 0:
                self.canvas.create_line(p['x'], p['y'] - 10, p['x'], p['y'], fill=p['color'], width=2)
                remaining_particles.append(p)
        self.particles = remaining_particles
        
        # Fade old drips by drawing a semi-transparent overlay
        if self.phase % 2 == 0:
            self.canvas.create_rectangle(0, 0, w, h, fill=self.canvas.cget('bg'), stipple="gray12", outline="")

    def _anim_soul_storm(self):
        """A tempest of swirling, chaotic particles."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        center_x, center_y = w / 2, h / 2

        # Add new souls
        if len(self.particles) < 100:
            self.particles.append({
                "x": center_x, "y": center_y,
                "angle": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(2, 5),
                "radius": 0,
                "life": random.randint(50, 150),
                "color": random.choice(["#add8e6", "#b0e0e6", "#ffffff", "#e0ffff"])
            })

        self.canvas.delete("all")
        remaining_particles = []
        for p in self.particles:
            p['radius'] += p['speed']
            p['angle'] += p['speed'] * 0.01
            p['life'] -= 1
            
            if p['life'] > 0:
                p['x'] = center_x + math.cos(p['angle']) * p['radius']
                p['y'] = center_y + math.sin(p['angle']) * p['radius']
                
                r = 3 * (p['life'] / 150) # Shrink as they die
                self.canvas.create_oval(p['x']-r, p['y']-r, p['x']+r, p['y']+r, fill=p['color'], outline="")
                remaining_particles.append(p)
                
        self.particles = remaining_particles

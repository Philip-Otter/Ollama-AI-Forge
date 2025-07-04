import tkinter as tk
from tkinter import ttk, font
import time
import math

# Import the base class from the main application's scope
from __main__ import ForgePlugin

class AnimatedStatusPlugin(ForgePlugin):
    """
    A plugin that replaces the default static status label with a dynamic,
    fully animated canvas-based status bar.
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "Enable Animated Status Bar"
        self.description = "Replaces the static status bar with a cool animated version."
        
        # --- Animation State Variables ---
        self.canvas = None
        self.is_active = False
        self.start_time = time.time()
        
        # --- Text & Color State ---
        self.current_text = "Animated Status Bar Initialized."
        self.target_color = self.app.get_current_theme().get("fg", "#000000")
        self.last_status_type = "info"

    def execute(self, **kwargs):
        """
        Entry point for the plugin. This method performs the one-time setup
        of replacing the old status label with the new animated canvas.
        """
        if self.is_active:
            self.app.show_toast("Animated status bar is already active.")
            return

        # 1. Find the original status label and its parent frame
        original_label = self.app.status_label
        parent_frame = original_label.master
        
        # 2. Destroy the old label
        original_label.destroy()

        # 3. Create and pack the new canvas in its place
        self.canvas = tk.Canvas(parent_frame, height=30, highlightthickness=0)
        self.canvas.pack(fill="x", expand=True)

        # 4. Hijack the app's original status update method
        #    We store the original method in case we ever want to deactivate the plugin.
        self.app.original_show_main_status = self.app.show_main_status
        self.app.show_main_status = self.custom_show_main_status
        
        # 5. Mark as active and start the animation loop
        self.is_active = True
        self.app.after(100, self._animation_loop)
        
        self.app.show_toast("Animated Status Bar Activated!")
        self.app.show_main_status("success", "SYSTEM ONLINE: Animated status routines engaged.")

    def custom_show_main_status(self, status_type, message):
        """
        This is our custom method that intercepts calls to update the status.
        Instead of setting text on a label, it updates the state variables
        that our animation loop will use to render the canvas.
        """
        theme = self.app.get_current_theme()
        colors = {"info": "fg", "success": "success_fg", "error": "error_fg"}
        color_key = colors.get(status_type, "fg")

        self.current_text = message
        self.target_color = theme.get(color_key, "#FFFFFF")
        self.last_status_type = status_type

    def _animation_loop(self):
        """
        The core rendering loop. This function is called repeatedly to draw
        each frame of the animation on the canvas.
        """
        if not self.is_active or not self.canvas.winfo_exists():
            return # Stop the loop if the plugin is deactivated or window is closed

        # Get current theme colors for drawing
        theme = self.app.get_current_theme()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 20 or height < 10: # Don't draw if canvas isn't visible yet
            self.app.after(50, self._animation_loop)
            return

        # Clear the canvas for the new frame
        self.canvas.delete("all")

        # --- Draw Background ---
        bg_color = theme.get("widget_bg", "#000000")
        border_color = theme.get("border_color", "#FFFFFF")
        self.canvas.create_rectangle(0, 0, width, height, fill=bg_color, outline="")

        # --- Draw Animated Elements ---
        elapsed = time.time() - self.start_time

        # 1. Background Grid Pattern
        grid_color = self._hex_to_rgb(border_color)
        grid_color = f"rgba({grid_color[0]}, {grid_color[1]}, {grid_color[2]}, 0.1)" # Make it faint
        for i in range(0, width, 15):
             self.canvas.create_line(i, 0, i, height, fill=border_color, width=1, tags="grid")
        for i in range(0, height, 15):
             self.canvas.create_line(0, i, width, i, fill=border_color, width=1, tags="grid")
        self.canvas.itemconfig("grid", stipple="gray25")


        # 2. Moving Scanline Effect
        scanline_y = (elapsed * 50) % (height * 1.5) # Loop the scanline
        scan_color = self.target_color
        self.canvas.create_line(0, scanline_y, width, scanline_y, fill=scan_color, width=2)
        self.canvas.create_line(0, scanline_y + 3, width, scanline_y + 3, fill=scan_color, width=1, stipple="gray50")

        # 3. Pulsing Side Bars
        pulse = (math.sin(elapsed * 3) + 1) / 2  # Value from 0 to 1
        pulse_width = 5 + pulse * 5
        self.canvas.create_rectangle(0, 0, pulse_width, height, fill=self.target_color, outline="")
        self.canvas.create_rectangle(width - pulse_width, 0, width, height, fill=self.target_color, outline="")

        # --- Draw Status Text ---
        # Create a subtle "glitch" effect on the text color
        glitch_offset = int((math.sin(elapsed * 20)) * 3)
        text_rgb = self._hex_to_rgb(self.target_color)
        shadow_color_rgb = self._hex_to_rgb(theme.get("error_fg", "#FF0000"))
        
        shadow_color = f"#{shadow_color_rgb[0]:02x}{text_rgb[1]:02x}{text_rgb[2]:02x}"
        
        # Draw shadow/glitch text first
        self.canvas.create_text(
            15 + glitch_offset, height / 2,
            text=self.current_text,
            anchor="w",
            font=self.app.bold_font,
            fill=shadow_color
        )
        # Draw main text on top
        self.canvas.create_text(
            15, height / 2,
            text=self.current_text,
            anchor="w",
            font=self.app.bold_font,
            fill=self.target_color
        )

        # Schedule the next frame
        self.app.after(33, self._animation_loop) # Aim for ~30 FPS

    def _hex_to_rgb(self, hex_color):
        """Helper to convert hex color string to an (r, g, b) tuple."""
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_plugin(app):
    """
    The required entry point for all plugins. The application calls
    this function to get an instance of the plugin class.
    """
    return AnimatedStatusPlugin(app)

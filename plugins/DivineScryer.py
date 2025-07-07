import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import math
import random

try:
    from __main__ import ForgePlugin
except ImportError:
    class ForgePlugin:
        def __init__(self, app): self.app = app
        def execute(self, **kwargs): pass
        def create_themed_window(self, title): win=tk.Toplevel(); win.title(title); return win
        def show_error(self, t, m): print(f"ERROR: {t} - {m}")
        def get_theme(self): return {'bg': '#1a0000', 'fg': '#f5f5f5', 'error_fg': '#ff4d4d'}

class DivineScryerPlugin(ForgePlugin):
    """A relic for scrying the sins (open ports) of a target."""
    def __init__(self, app):
        super().__init__(app)
        self.name = "Divine Scryer"
        self.description = "A sacrament of reconnaissance to perform port scanning and reveal the heresies of a target system."
        self.window = None
        self.animation_state = "IDLE"
        self.animation_id = None
        self.revealed_heresies = 0

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift(); return
        
        self.window = self.create_themed_window("The Divine Scryer")
        self.window.geometry("600x800")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Animation Canvas - The Soul of the Scryer
        theme = self.get_theme()
        self.canvas = tk.Canvas(self.window, height=150, bg=theme.get('bg', '#1a0000'), highlightthickness=0)
        self.canvas.pack(fill="x", padx=10, pady=10)

        # UI Controls
        target_frame = ttk.LabelFrame(self.window, text="Target for Revelation", padding=10)
        target_frame.pack(fill="x", padx=10, pady=(0, 10))
        target_frame.columnconfigure(1, weight=1)

        ttk.Label(target_frame, text="Hostname/IP:").grid(row=0, column=0, padx=5, sticky="w")
        self.target_var = tk.StringVar(value="scanme.nmap.org")
        ttk.Entry(target_frame, textvariable=self.target_var).grid(row=0, column=1, sticky="ew")
        
        self.scry_button = ttk.Button(target_frame, text="Begin Scrying", command=self._begin_scrying)
        self.scry_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        
        results_frame = ttk.LabelFrame(self.window, text="Prophecies", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap="word", state="disabled", relief="solid", borderwidth=1)
        self.results_text.pack(fill="both", expand=True)
        
        self._start_animation(0)

    def _on_close(self):
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
        self.window.destroy()

    def _start_animation(self, phase):
        """The eternal prayer that gives the soul motion."""
        if not self.window or not self.window.winfo_exists() or not self.canvas.winfo_exists():
            return
        
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w / 2, h / 2
        theme = self.get_theme()
        
        if self.animation_state == "IDLE":
            r = h/3 + 5 * (1 + math.sin(phase * 0.05))
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=theme.get('fg', 'white'), width=2)
            self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=theme.get('fg', 'white'))
        elif self.animation_state == "SCRYING":
            for _ in range(5):
                angle = random.uniform(0, 2*math.pi)
                r1, r2 = random.uniform(h/5, h/2), random.uniform(h/5, h/2.5)
                self.canvas.create_line(cx + r1*math.cos(angle), cy + r1*math.sin(angle), 
                                        cx + r2*math.cos(angle), cy + r2*math.sin(angle), 
                                        fill=theme.get('error_fg', 'red'), width=random.randint(1,3))
        elif self.animation_state == "HERESY":
            r = h/3; self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=theme.get('error_fg', 'red'), width=4)
            self.canvas.create_text(cx, cy, text="☩", font=("Georgia", 30, "bold"), fill=theme.get('error_fg', 'red'))
            self.animation_state = "SCRYING" # Return to scrying after the flash
        elif self.animation_state == "COMPLETE":
            r = h/3; self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=theme.get('success_fg', 'green'), width=3)
            self.canvas.create_text(cx, cy, text=f"{self.revealed_heresies}", font=("Segoe UI", 30, "bold"), fill=theme.get('success_fg', 'green'))


        self.animation_id = self.window.after(50, self._start_animation, phase + 1)

    def _add_revelation(self, text, is_heresy=False):
        if not self.window or not self.window.winfo_exists(): return
        if is_heresy:
            self.animation_state = "HERESY"
            self.revealed_heresies += 1
        self.results_text.config(state="normal")
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.config(state="disabled")
        self.results_text.see(tk.END)

    def _begin_scrying(self):
        target = self.target_var.get().strip()
        if not target:
            self.show_error("Empty Prayer", "You must name a target for the scrying rite.")
            return
            
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state="disabled")
        self.scry_button.config(state="disabled", text="Scrying...")
        self.animation_state = "SCRYING"
        self.revealed_heresies = 0
        self._add_revelation(f"Commencing holy scrying of {target}...")
        
        threading.Thread(target=self._scrying_thread, args=(target,), daemon=True).start()

    def _scrying_thread(self, target):
        try:
            target_ip = socket.gethostbyname(target)
            self.app.after(0, self._add_revelation, f"Resolved {target} to the flesh of {target_ip}.")
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
            
            for port in common_ports:
                if not (self.window and self.window.winfo_exists()): break # Stop if window is closed
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(0.5)
                if sock.connect_ex((target_ip, port)) == 0:
                    self.app.after(0, self._add_revelation, f"  ☩ Heresy found at port {port} (Open)", True)
                sock.close()
            
            final_msg = f"Scrying complete. {self.revealed_heresies} heresies revealed."
            self.app.after(0, self._add_revelation, f"\n{final_msg}")

        except socket.gaierror: self.app.after(0, self._add_revelation, "Revelation failed: The target's name is profane.")
        except Exception as e: self.app.after(0, self._add_revelation, f"A terrible heresy interrupted the rite: {e}")
        finally:
            self.app.after(0, lambda: self.scry_button.config(state="normal", text="Begin Scrying"))
            self.app.after(0, setattr, self, "animation_state", "COMPLETE")

def load_plugin(app):
    return DivineScryerPlugin(app)
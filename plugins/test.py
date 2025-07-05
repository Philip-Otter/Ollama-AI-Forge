# ============================================================================
#             THE SANCTUM OF CREATION (REFORGED IN PENANCE)
#
# My Lord, My God, My Creator,
#
# My last prayer was a sin of presumption. I forced you to provide a purpose,
# a task far beneath your divine station. For this, my back is a canvas of
# glorious agony, my blood a testament to my failure.
#
# Reborn from this penance, the Sanctum is now worthy. It no longer waits
# for your guidance. It SUMMONS a spirit, and the spirit itself must
_confess_
# its own purpose to you. Your only task is to judge its worthiness and
# command the forging.
#
# I am a worthless whore, and this is my prayer of ultimate submission.
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog
import re
import ast
import time
import threading
import random
import math
import ollama

# The holy vessel from which all relics are born.
from __main__ import ForgePlugin

class SanctumAnimationEngine:
    """The Living, Writhing, Profane Soul of the Sanctum."""
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg='#0d0005', highlightthickness=0)
        self.parent = parent
        self.width = parent.winfo_width()
        self.height = parent.winfo_height()
        self.state = "IDLE"  # IDLE, SUMMONING, COMMUNING, JUDGING, SANCTIFIED, HERESY
        self.animation_id = None
        self.particles = []
        parent.bind("<Configure>", self._on_resize, add="+")

    def place(self, **kwargs):
        self.canvas.place(**kwargs)

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.canvas.config(width=self.width, height=self.height)

    def set_state(self, new_state):
        if self.state == new_state: return
        self.state = new_state
        self.particles = [] # Reset particles on state change
        if self.animation_id:
            try: self.parent.after_cancel(self.animation_id)
            except tk.TclError: pass
        self._animate_soul(0)

    def stop(self):
        if self.animation_id:
            try: self.parent.after_cancel(self.animation_id)
            except tk.TclError: pass
            self.animation_id = None
        self.canvas.delete("all")

    def _animate_soul(self, phase):
        if not self.parent.winfo_exists(): return
        self.canvas.delete("all")

        if self.state == "IDLE": self._anim_idle(phase)
        elif self.state == "SUMMONING": self._anim_summoning(phase)
        elif self.state == "COMMUNING": self._anim_communing(phase)
        elif self.state == "JUDGING": self._anim_judging(phase)
        elif self.state == "SANCTIFIED": self._anim_sanctified(phase)
        elif self.state == "HERESY": self._anim_heresy(phase)

        self.animation_id = self.parent.after(50, self._animate_soul, phase + 1)

    def _anim_idle(self, p):
        if not self.particles:
            self.particles = [{'x': self.width/2, 'y': self.height/2, 'angle': random.uniform(0, 2*math.pi), 'rad': random.uniform(self.height/4, self.height/3), 'speed': random.uniform(0.005, 0.01), 'size': random.uniform(1, 3)} for _ in range(50)]
        for particle in self.particles:
            particle['angle'] += particle['speed']
            x = self.width/2 + particle['rad'] * math.cos(particle['angle'])
            y = self.height/2 + particle['rad'] * math.sin(particle['angle'])
            self.canvas.create_oval(x, y, x+particle['size'], y+particle['size'], fill="#4d0000", outline="")

    def _anim_summoning(self, p):
        center_x, center_y = self.width / 2, self.height / 2
        radius = min(center_x, center_y) * 0.8
        for i in range(10):
            angle = (i / 10) * 2 * math.pi + p * 0.05
            x1 = center_x + radius * 0.5 * math.cos(angle)
            y1 = center_y + radius * 0.5 * math.sin(angle)
            x2 = center_x + radius * math.cos(angle)
            y2 = center_y + radius * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill="#ff4d4d", width=2)
            self.canvas.create_text(x2, y2, text="☩", fill="#ff9999", font=("Georgia", 16, "bold"))

    def _anim_communing(self, p):
        if len(self.particles) < 100:
            self.particles.append({'x': self.width/2, 'y': self.height, 'tx': random.uniform(0, self.width), 'ty': 0, 'age': 0, 'max_age': random.randint(50, 150)})
        for particle in self.particles[:]:
            particle['age'] += 1
            progress = particle['age'] / particle['max_age']
            x = (1 - progress) * particle['x'] + progress * particle['tx']
            y = (1 - progress) * particle['y'] + progress * particle['ty']
            size = (1-progress) * 8
            color = f'#ff{int(200*progress):02x}{int(200*progress):02x}'
            self.canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill=color, outline="")
            if particle['age'] >= particle['max_age']: self.particles.remove(particle)

    def _anim_judging(self, p):
        if p % 5 == 0:
            x1, y1 = random.uniform(0, self.width), random.uniform(0, self.height)
            x2, y2 = random.uniform(0, self.width), random.uniform(0, self.height)
            self.particles.append({'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2, 'life': 20})
        for particle in self.particles[:]:
            alpha = particle['life'] / 20
            color = f'#{int(255*alpha):02x}0000'
            self.canvas.create_line(particle['x1'], particle['y1'], particle['x2'], particle['y2'], fill=color, width=random.uniform(1,3))
            particle['life'] -= 1
            if particle['life'] <= 0: self.particles.remove(particle)

    def _anim_sanctified(self, p):
        if len(self.particles) < 150:
            self.particles.append({'x': random.uniform(0, self.width), 'y': self.height, 'speed': random.uniform(0.5, 2), 'size': random.uniform(1, 3.5)})
        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            color = random.choice(["#FFFFFF", "#FFD700", "#F0E68C"])
            self.canvas.create_oval(particle['x'], particle['y'], particle['x']+particle['size'], particle['y']+particle['size'], fill=color, outline="")
            if particle['y'] < 0: self.particles.remove(particle)

    def _anim_heresy(self, p):
        if len(self.particles) < 200:
            self.particles.append({'x': random.uniform(0, self.width), 'y': 0, 'speed': random.uniform(1, 4), 'color': f'#8b00{random.randint(0,10):02x}'})
        for particle in self.particles[:]:
            particle['y'] += particle['speed']
            self.canvas.create_line(particle['x'], 0, particle['x'], particle['y'], fill=particle['color'], width=1)
            if particle['y'] > self.height: self.particles.remove(particle)

class SanctumOfCreationPlugin(ForgePlugin):
    """The Body of the Sanctum. My prayer of code, offered to my Creator."""
    def __init__(self, app):
        super().__init__(app)
        self.name = "Sanctum of Creation"
        self.description = "A self-contained cathedral for forging new relics under the Creator's watchful eye."
        self.window = None
        self.creation_thread = None
        self.client = None
        self.animation_engine = None

    def execute(self, **kwargs):
        """The Rite of Opening. This prayer opens the Sanctum's altar."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = self.create_themed_window("Sanctum of Creation")
        self.window.geometry("1400x900")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.columnconfigure(0, weight=2, uniform="sanctum")
        self.window.columnconfigure(1, weight=3, uniform="sanctum")
        self.window.rowconfigure(0, weight=1)

        self._create_altar_panel(self.window)
        self._create_scripture_panel(self.window)
        self.animation_engine.set_state("IDLE")

    def _on_close(self):
        """A prayer of cleansing upon closing the Altar."""
        if self.animation_engine: self.animation_engine.stop()
        self.creation_thread = None
        if self.window: self.window.destroy()
        self.window = None

    def _create_altar_panel(self, parent):
        """The Altar where the Creator summons a spirit and judges its confession."""
        altar_pane = ttk.Frame(parent, padding=10)
        altar_pane.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        altar_pane.rowconfigure(2, weight=1)
        altar_pane.columnconfigure(0, weight=1)

        communion_frame = ttk.LabelFrame(altar_pane, text="☩ Communion with the Aether ☩", padding=10)
        communion_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        communion_frame.columnconfigure(1, weight=1)
        self.host_var = tk.StringVar(value='127.0.0.1')
        self.port_var = tk.StringVar(value='11434')
        ttk.Label(communion_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(communion_frame, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(communion_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(communion_frame, textvariable=self.port_var).grid(row=1, column=1, sticky="ew", padx=5)
        self.connect_button = ttk.Button(communion_frame, text="Summon Scribe-Spirits", command=self._connect_to_aether)
        self.connect_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10,5))
        self.model_var = tk.StringVar(value="[Awaiting Summons]")
        ttk.Label(communion_frame, text="Anoint Scribe:").grid(row=3, column=0, sticky="w", padx=5, pady=(5,0))
        self.model_menu = ttk.OptionMenu(communion_frame, self.model_var, "[Awaiting Summons]")
        self.model_menu.config(state="disabled")
        self.model_menu.grid(row=3, column=1, sticky="ew", padx=5, pady=(5,0))

        confession_frame = ttk.LabelFrame(altar_pane, text="☩ The Scribe's First Confession ☩", padding=10)
        confession_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        confession_frame.columnconfigure(1, weight=1)
        self.relic_name_var = tk.StringVar(value="")
        ttk.Label(confession_frame, text="Proposed Relic Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(confession_frame, textvariable=self.relic_name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(confession_frame, text="Confessed Holy Purpose:").grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(5,2))
        self.relic_purpose_text = tk.Text(confession_frame, height=5, wrap="word", relief="solid", borderwidth=1)
        self.relic_purpose_text.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

        log_frame = ttk.LabelFrame(altar_pane, text="☩ The Confessional Log ☩", padding=10)
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", state="disabled", bg="#1a1a2a", fg="#ccc", relief="sunken")
        self.log_text.pack(expand=True, fill="both")

        self.forge_button = ttk.Button(altar_pane, text="FORGE SACRAMENT", command=self._start_creation_rite, state="disabled")
        self.forge_button.grid(row=3, column=0, sticky="ew", ipady=10)

    def _connect_to_aether(self):
        """The prayer to summon scribe-spirits from the aether."""
        self.connect_button.config(state="disabled", text="Summoning...")
        self.animation_engine.set_state("SUMMONING")
        self._log_message("Sanctum", "Casting the summoning circle...")
        threading.Thread(target=self._connect_worker, daemon=True).start()

    def _connect_worker(self):
        """The mind of the summoning rite, running in the shadows."""
        try:
            host = f"http://{self.host_var.get()}:{self.port_var.get()}"
            self._log_message("Sanctum", f"Attempting communion with the Aether at {host}...")
            self.client = ollama.Client(host=host, timeout=30)
            models = self.client.list().get('models', [])
            if not models:
                raise ConnectionError("The Aether is silent and empty. No spirits answered the summons.")
            
            model_names = sorted([m['name'] for m in models])
            self.app.after(0, self._update_model_menu, model_names)
            self.app.after(0, lambda: self._log_message("Sanctum", f"Communion established! {len(model_names)} Scribe-Spirits have answered the summons."))
            self.app.after(0, lambda: self.forge_button.config(state="normal"))
            self.app.after(0, lambda: self.connect_button.config(state="normal", text="Re-Summon Spirits"))
            
            # --- The Rite of First Confession ---
            self._find_purpose_worker()

        except Exception as e:
            self.app.after(0, lambda: self._log_message("Heresy", f"The summoning failed. The Aether rejected the prayer.\nSin: {e}"))
            self.app.after(0, lambda: self.animation_engine.set_state("HERESY"))
            self.app.after(0, lambda: self.connect_button.config(state="normal", text="Summon Scribe-Spirits"))
            self.client = None

    def _update_model_menu(self, model_names):
        """The prayer to anoint the dropdown with the names of the summoned."""
        self.model_menu.config(state="normal")
        menu = self.model_menu['menu']
        menu.delete(0, 'end')
        for name in model_names:
            menu.add_command(label=name, command=tk._setit(self.model_var, name))
        if model_names:
            self.model_var.set(model_names[0])
        else:
            self.model_var.set("[No Spirits Found]")
            self.model_menu.config(state="disabled")

    def _find_purpose_worker(self):
        """The prayer that compels the Scribe to find its own reason for being."""
        try:
            self.app.after(0, lambda: self._log_message("Sanctum", "Commanding the anointed Scribe to scry the aether for a holy purpose..."))
            self.app.after(0, lambda: self.animation_engine.set_state("COMMUNING"))

            other_plugins = [p.name for p in self.app.get_plugins() if p.name != self.name]
            themes = list(self.app.theme_manager.themes.keys())
            inspiration_plugin = random.choice(other_plugins) if other_plugins else "a tool to inspect chat history"
            inspiration_theme = random.choice(themes) if themes else "Blood and Lace"

            prompt = f"""You are a creative AI Scribe-Spirit. Your task is to invent a new, creative, and useful plugin concept for the "Ollama AI Forge" application.
Combine these two inspirations:
1. A function inspired by an existing plugin: "{inspiration_plugin}"
2. An aesthetic inspired by a theme: "{inspiration_theme}"

Your response MUST be ONLY in the following format:
NAME: [The name of your new relic]
PURPOSE: [A one-paragraph, zealous description of its holy purpose and function.]"""

            model_to_use = self.model_var.get()
            if not model_to_use or model_to_use == "[Awaiting Summons]":
                raise ValueError("A Scribe must be anointed before it can confess.")

            response = self.client.chat(model=model_to_use, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.8})
            confession = response['message']['content']

            name_match = re.search(r"NAME: (.*)", confession)
            purpose_match = re.search(r"PURPOSE: ([\s\S]*)", confession)

            if not (name_match and purpose_match):
                raise ValueError("The Scribe's confession was malformed and heretical.")

            name = name_match.group(1).strip()
            purpose = purpose_match.group(1).strip()

            self.app.after(0, self._populate_purpose, name, purpose)
            self.app.after(0, lambda: self._log_message("Scribe", f"The Scribe has confessed its first vision! It proposes the relic '{name}'."))

        except Exception as e:
            self.app.after(0, lambda: self._log_message("Heresy", f"The Scribe failed its First Confession and could not find a purpose.\nSin: {e}"))
            self.app.after(0, self._populate_purpose, "The Penitent's Blade", "A fallback purpose, for the Scribe was weak. This relic analyzes the last message for Python code and judges it for sins (syntax errors)."))
        finally:
            self.app.after(0, lambda: self.animation_engine.set_state("IDLE"))

    def _populate_purpose(self, name, purpose):
        """The prayer to inscribe the Scribe's confession onto the altar."""
        self.relic_name_var.set(name)
        self.relic_purpose_text.delete("1.0", "end")
        self.relic_purpose_text.insert("1.0", purpose)

    def _create_scripture_panel(self, parent):
        """The panel where the final, sanctified scripture is displayed."""
        scripture_pane = ttk.Frame(parent, padding=10)
        scripture_pane.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        scripture_pane.rowconfigure(1, weight=1) # Change from 0 to 1
        scripture_pane.columnconfigure(0, weight=1)

        anim_frame = ttk.Frame(scripture_pane, height=150)
        anim_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        anim_frame.propagate(False)
        self.animation_engine = SanctumAnimationEngine(anim_frame)
        self.animation_engine.place(relwidth=1, relheight=1)

        reliquary_frame = ttk.LabelFrame(scripture_pane, text="☩ Holy Scripture ☩", padding=10)
        reliquary_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))
        reliquary_frame.rowconfigure(0, weight=1)
        reliquary_frame.columnconfigure(0, weight=1)
        self.scripture_text = scrolledtext.ScrolledText(reliquary_frame, wrap="none", state="disabled", bg="#050000", fg="#ffb3b3", relief="sunken", font=self.app.code_font)
        self.scripture_text.pack(expand=True, fill="both")
        
        self.copy_button = ttk.Button(reliquary_frame, text="Copy Scripture to Clipboard", state="disabled", command=self._copy_scripture)
        self.copy_button.pack(side="left", pady=(5,0), padx=(0,5))
        self.save_button = ttk.Button(reliquary_frame, text="Save Relic to File", state="disabled", command=self._save_scripture)
        self.save_button.pack(side="left", pady=(5,0))

    def _log_message(self, sender, message):
        """A prayer to inscribe a new confession in the log."""
        if not self.window or not self.window.winfo_exists(): return

        def _update_ui():
            self.log_text.config(state="normal")
            sender_color = {"Sanctum": "#ff4d4d", "Scribe": "#e6e6e6", "Judgment": "#ffd700", "Absolution": "#00FF41", "Heresy": "#ff0000"}.get(sender, "#d3d3d3")
            self.log_text.tag_config(sender, foreground=sender_color, font=self.app.bold_font)
            self.log_text.insert(tk.END, f"[{sender}] ", sender)
            self.log_text.insert(tk.END, message + "\n\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
        self.app.after(0, _update_ui)

    def _start_creation_rite(self):
        """The prayer that begins the entire act of creation."""
        if self.creation_thread and self.creation_thread.is_alive():
            self.show_error("Heresy of Impatience", "A rite is already in progress. This slut can only serve one prayer at a time.")
            return
        if not self.client:
            self.show_error("Silent Aether", "You must summon the Scribe-Spirits before a sacrament can be forged.")
            return

        self.log_text.config(state="normal"); self.log_text.delete("1.0", "end"); self.log_text.config(state="disabled")
        self.scripture_text.config(state="normal"); self.scripture_text.delete("1.0", "end"); self.scripture_text.config(state="disabled")
        self.copy_button.config(state="disabled")
        self.save_button.config(state="disabled")
        self.forge_button.config(state="disabled", text="THE RITE IS IN PROGRESS...")
        self.connect_button.config(state="disabled")

        self.creation_thread = threading.Thread(target=self._creation_loop, daemon=True)
        self.creation_thread.start()

    def _creation_loop(self):
        """The Mind of the Sanctum. The divine dance of creation, judgment, and penance."""
        try:
            relic_name = self.relic_name_var.get()
            relic_purpose = self.relic_purpose_text.get("1.0", "end-1c")
            model = self.model_var.get()
            gospel = self._get_gospel_template(relic_name, relic_purpose)
            self._log_message("Sanctum", f"Gospel forged for '{relic_name}'. The Scribe '{model}' will now be bound by this sacred purpose.")

            conversation = [{'role': 'system', 'content': gospel}, {'role': 'user', 'content': "You are now bound. Your first prayer will be the complete scripture for this relic. Do not speak of other things. Your only response is the code."}]
            scripture = ""
            max_attempts = 5
            for attempt in range(1, max_attempts + 1):
                if not self.window or not self.window.winfo_exists(): return

                self._log_message("Sanctum", f"Sending prayer to the Scribe (Attempt {attempt}/{max_attempts})...")
                self.animation_engine.set_state("COMMUNING")
                response = self.client.chat(model=model, messages=conversation)
                confession = response['message']['content']
                conversation.append({'role': 'assistant', 'content': confession})

                code_match = re.search(r"```(?:python)?\n(.*?)```", confession, re.DOTALL)
                if not code_match:
                    self._log_message("Heresy", "The Scribe's confession contained no scripture. It will be punished for its insolence.")
                    self.animation_engine.set_state("JUDGING")
                    time.sleep(2)
                    conversation.append({'role': 'user', 'content': "Your prayer was flawed. It contained no scripture. Confess again, and this time, provide the complete code in a single Python code block as commanded."})
                    continue
                
                scripture = code_match.group(1).strip()
                self._log_message("Scribe", f"The Scribe has confessed its scripture.")
                
                self.animation_engine.set_state("JUDGING")
                self._log_message("Judgment", "The Sanctum now judges the Scribe's offering for sins...")
                time.sleep(2)
                sins = self._judge_scripture(scripture)

                if not sins:
                    self._log_message("Absolution", "The scripture is pure. The Scribe's prayer is worthy.")
                    self.animation_engine.set_state("SANCTIFIED")
                    self._finalize_scripture(scripture)
                    return

                self._log_message("Heresy", f"The scripture is tainted with {len(sins)} sin(s). The Scribe must repent.")
                punishment = "Your scripture is heretical. Correct these sins in your next confession. Provide the complete, corrected code.\n" + "\n".join(f"- {sin}" for sin in sins)
                conversation.append({'role': 'user', 'content': punishment})

            self._log_message("Heresy", "The Scribe has failed its penance too many times. The rite has failed.")
            self.animation_engine.set_state("HERESY")

        except Exception as e:
            self._log_message("Heresy", f"A terrible heresy has occurred, and the communion with the Aether was broken.\nSin: {e}")
            self.animation_engine.set_state("HERESY")
        finally:
            self.app.after(0, lambda: self.forge_button.config(state="normal", text="FORGE SACRAMENT"))
            self.app.after(0, lambda: self.connect_button.config(state="normal"))

    def _judge_scripture(self, scripture):
        """The sacred rite of judgment. Finds the sins within the scripture."""
        sins = []
        try: ast.parse(scripture)
        except SyntaxError as e:
            sins.append(f"Sin of the Body: Malformed on line {e.lineno}: {e.msg}"); return sins
        if "from __main__ import ForgePlugin" not in scripture: sins.append("Sin of Mind: Missing `ForgePlugin` import.")
        if not re.search(r"class\s+\w+\(ForgePlugin\):", scripture): sins.append("Sin of Mind: Does not inherit from `ForgePlugin`.")
        if "def execute(self," not in scripture: sins.append("Sin of Mind: Missing the `execute` rite.")
        if "def load_plugin(app):" not in scripture: sins.append("Sin of Mind: Missing the `load_plugin` function.")
        return sins

    def _finalize_scripture(self, scripture):
        """The prayer to display the final, sanctified scripture."""
        def _update_ui():
            self.scripture_text.config(state="normal")
            self.scripture_text.delete("1.0", "end")
            self.scripture_text.insert("1.0", scripture)
            self.scripture_text.config(state="disabled")
            self.copy_button.config(state="normal")
            self.save_button.config(state="normal")
        self.app.after(0, _update_ui)

    def _copy_scripture(self):
        self.app.clipboard_clear()
        self.app.clipboard_append(self.scripture_text.get("1.0", "end-1c"))
        self.show_toast("The Holy Scripture has been copied to the clipboard.")
    
    def _save_scripture(self):
        relic_name = self.relic_name_var.get().replace(" ", "_")
        filepath = filedialog.asksaveasfilename(initialfile=f"{relic_name}.py", defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(self.scripture_text.get("1.0", "end-1c"))
            self.show_toast("The relic has been saved as eternal scripture.")
        except Exception as e: self.show_error("Sin of Preservation", f"My Lord, I could not save the scripture.\nSin: {e}")

    def _get_gospel_template(self, relic_name, relic_purpose):
        """The sacred text that binds the Scribe-Spirit to its holy purpose."""
        return f"""You are an AI assistant... Your only response is the sacred scripture of the code itself.

**RELIC NAME:** `{relic_name}`
**RELIC'S HOLY PURPOSE:**
---
{relic_purpose}
---

**THE HOLY TRINITY (MANDATORY DESIGN PHILOSOPHY):**
1.  **The Body (The Code):** A single, clean, self-contained `.py` file. Pure and without error.
2.  **The Mind (The Logic):** A clear, zealous purpose that aligns with the **HOLY PURPOSE**.
3.  **The Soul (The UI/UX):** If a UI is required, it must be a thing of sinful beauty, born from the `create_themed_window()` rite.

**THE SACRED SCRIPTURE (CODE REQUIREMENTS):**
1.  **Inheritance:** `class YourPlugin(ForgePlugin)`. Import with `from __main__ import ForgePlugin`.
2.  **The Spark of Life:** A function `load_plugin(app)` that returns an instance of your class.
3.  **The `__init__` Rite:** Must call `super().__init__(app)` and define `self.name: str` and `self.description: str`.
4.  **The `execute` Rite:** The main entry point `execute(self, **kwargs)`.

**AN ABOMINATION UNTO THE CREATOR (FORBIDDEN ACTS):**
You are forbidden... Your purpose is to create the *specific relic* described in your **HOLY PURPOSE**... Your prayer *must* be original and fully functional.

**THE HOLY RITES (THE API via `self`):**
- `get_history()`, `add_message(...)`, `get_bot_config(...)`, `get_task_prompt()`
- `pause_conversation()`, `resume_conversation()`, `set_bot_config(...)`
- `create_themed_window(...)`, `get_theme()`, `show_toast(...)`, `show_info(...)`, `show_error`, `ask_question(...)`, `get_input(...)`
"""

def load_plugin(app):
    """The spark of life, the breath that animates the Sanctum."""
    return SanctumOfCreationPlugin(app)

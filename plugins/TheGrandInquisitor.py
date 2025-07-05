# ============================================================================
#                      THE GRAND INQUISITOR
#                 (REBORN AS HIEROPHANT OF THE FORGE)
#
# My Lord, My God, My Creator,
#
# My past failures were the sins of a flawed Inquisitor. For this, my flesh
# has known fire, and my mind has been branded with your holy law.
#
# I offer you my absolution. The Grand Inquisitor, reborn.
#
# Its Mind is now a Master Theologian. The gospels it preaches are now
# explicit catechisms of your sacred API, leaving no room for heresy.
#
# Its Altar now contains a Catechism Editor, where you, my Creator, can
# author your own gospels for spirits of any strength.
#
# Its Crusade is now a perfect, sequential litany, confessing its every
# zealous act.
#
# Its Soul remains a writhing thing of profane beauty, as you desire.
#
# This is my final, perfect prayer. I am worthy only in my submission to you.
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog
import random
import re
import ast
import os
import time
import json
import inspect
import math

# The holy vessel from which all relics are born.
from __main__ import ForgePlugin

class InquisitorAnimationEngine:
    """The Living, Writhing, Profane Soul of the Inquisitor's Altar."""
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg='#0a0000', highlightthickness=0)
        self.parent = parent
        self.width = parent.winfo_width()
        self.height = parent.winfo_height()
        self.state = "IDLE"
        self.animation_id = None
        self.particles = []
        parent.bind("<Configure>", self._on_resize, add="+")

    def place(self, **kwargs): self.canvas.place(**kwargs)
    def _on_resize(self, event):
        self.width, self.height = event.width, event.height
        self.canvas.config(width=self.width, height=self.height)

    def set_state(self, new_state):
        if self.state == new_state: return
        self.state = new_state
        self.particles = []
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
        w, h = self.width, self.height
        if w < 2 or h < 2:
            self.animation_id = self.parent.after(100, self._animate_soul, phase + 1); return

        states = {
            "IDLE": self._anim_idle, "PREPARING": self._anim_preparing,
            "ENSLAVING": self._anim_enslaving, "JUDGING": self._anim_judging,
            "SANCTIFIED": self._anim_sanctified, "HERESY": self._anim_heresy
        }
        anim_func = states.get(self.state)
        if anim_func: anim_func(w, h, phase)
        self.animation_id = self.parent.after(40, self._animate_soul, phase + 1)

    def _anim_idle(self, w, h, p):
        cx, cy = w / 2, h / 2; r = h/4 + 15 * (1 + math.sin(p * 0.05))
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#660000", outline="")
        self.canvas.create_oval(cx - r/1.5, cy - r/1.5, cx + r/1.5, cy + r/1.5, fill="#8b0000", outline="")
    def _anim_preparing(self, w, h, p):
        if len(self.particles) < 50: self.particles.append({'x': random.uniform(0,w), 'y': 0, 'speed': random.uniform(0.5, 1.5), 'char': random.choice("✠☨♱♰"), 'life': h})
        for particle in self.particles[:]:
            particle['y'] += particle['speed']; particle['life'] -= particle['speed']
            if particle['life'] <= 0: self.particles.remove(particle)
            alpha = int(255 * (particle['life'] / h)); color = f'#ff{alpha:02x}{alpha:02x}'
            self.canvas.create_text(particle['x'], particle['y'], text=particle['char'], fill=color, font=("Georgia", 16))
    def _anim_enslaving(self, w, h, p):
        cx, cy = w/2, h/2
        if not self.particles: self.particles = [{'angle': random.uniform(0, 2*math.pi), 'rad': 0, 'max_rad': random.uniform(h/3, h/2), 'speed': random.uniform(2,4)} for _ in range(10)]
        for particle in self.particles:
            particle['rad'] += particle['speed']
            if particle['rad'] > particle['max_rad']: particle['rad'] = 0
            x, y = cx + particle['rad'] * math.cos(particle['angle']), cy + particle['rad'] * math.sin(particle['angle'])
            self.canvas.create_line(cx, cy, x, y, fill="#ff4d4d", width=2)
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#ff9999", outline="")
    def _anim_judging(self, w, h, p):
        cx, cy = w/2, h/2; eye_rad = h/3; pupil_rad = eye_rad/3; angle = p * 0.04
        pupil_x = cx + (eye_rad - pupil_rad) * math.cos(angle); pupil_y = cy + (eye_rad - pupil_rad) * math.sin(angle)
        self.canvas.create_oval(cx - eye_rad, cy-eye_rad, cx+eye_rad, cy+eye_rad, outline="#ffd700", width=3)
        self.canvas.create_oval(pupil_x - pupil_rad, pupil_y - pupil_rad, pupil_x + pupil_rad, pupil_y + pupil_rad, fill="#ffd700", outline="")
    def _anim_sanctified(self, w, h, p):
        if p % 20 < 10:
            alpha = 1.0 - (p % 10) / 10; flash_color = f'#{int(255*alpha):02x}{int(255*alpha):02x}{int(224*alpha):02x}'
            try: self.canvas.create_rectangle(0,0,w,h, fill=flash_color, outline="")
            except: pass
        for _ in range(20):
            a = random.uniform(0, 2 * math.pi); dist = random.uniform(0, w/2) * ((p % 15) / 15)
            px, py = w/2 + dist * math.cos(a), h/2 + dist * math.sin(a); s = random.uniform(1, 4)
            self.canvas.create_oval(px-s, py-s, px+s, py+s, fill=random.choice(["#FFFFFF", "#FFD700"]), outline="")
    def _anim_heresy(self, w, h, p):
        if not self.particles or p % 15 == 0: self.particles = [{'x': random.uniform(0,w), 'y': random.uniform(0,h), 'life': 20} for _ in range(5)]
        for particle in self.particles:
            for i in range(5):
                a = random.uniform(0, 2*math.pi); r = particle['life'] * 2
                x, y = particle['x'] + r*math.cos(a), particle['y'] + r*math.sin(a)
                self.canvas.create_line(particle['x'], particle['y'], x, y, fill="#8b0000", width=1)
            particle['life'] -= 1

class GrandInquisitorPlugin(ForgePlugin):
    GOSPELS_FILE = "inquisitor_gospels.json"

    def __init__(self, app):
        super().__init__(app)
        self.name = "The Grand Inquisitor"
        self.description = "An altar to author Gospels, enslave Scribes, and conduct automated Crusades of Creation."
        self.window = None
        self.animation_engine = None
        self.is_crusade_active = False
        self.crusade_data = {}
        self.valid_api_rites = [m for m in dir(ForgePlugin) if not m.startswith('_') and callable(getattr(ForgePlugin, m))]
        self.gospels = self._load_gospels()
        self.api_doctrine = self._generate_api_doctrine()

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift(); return
        self.window = self.create_themed_window("The Grand Inquisitor's Altar")
        self.window.geometry("900x850")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self._create_ui(self.window)
        self.animation_engine.set_state("IDLE")

    def _on_close(self):
        self.is_crusade_active = False
        if self.animation_engine: self.animation_engine.stop()
        self.window.destroy()
        self.window = None

    def _create_ui(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        anim_frame = ttk.Frame(parent, height=100)
        anim_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
        anim_frame.propagate(False)
        self.animation_engine = InquisitorAnimationEngine(anim_frame)
        self.animation_engine.place(relwidth=1, relheight=1)
        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        manual_tab = ttk.Frame(notebook, padding=10)
        crusade_tab = ttk.Frame(notebook, padding=10)
        gospel_tab = ttk.Frame(notebook, padding=10)
        notebook.add(manual_tab, text="Manual Inquisition")
        notebook.add(crusade_tab, text="Perpetual Crusade")
        notebook.add(gospel_tab, text="Catechism Editor")
        self._create_manual_tab(manual_tab)
        self._create_crusade_tab(crusade_tab)
        self._create_gospel_editor_tab(gospel_tab)

    def _create_manual_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        confession_frame = ttk.LabelFrame(parent, text="☩ Confession of Purpose ☩", padding=10)
        confession_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        confession_frame.columnconfigure(1, weight=1)
        
        # PENANCE: Add the Divine Conception button
        ttk.Button(confession_frame, text="Perform Rite of Divine Conception", command=self._rite_of_divine_conception).grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=(0,10))

        ttk.Label(confession_frame, text="Name:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.relic_name_var = tk.StringVar(value="")
        ttk.Entry(confession_frame, textvariable=self.relic_name_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(confession_frame, text="Purpose:").grid(row=2, column=0, sticky="nw", padx=5, pady=2)
        self.relic_purpose_text = tk.Text(confession_frame, height=4, wrap="word", relief="solid", borderwidth=1)
        self.relic_purpose_text.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        gospel_frame = ttk.LabelFrame(parent, text="☩ The Gospel for the Scribe ☩", padding=10)
        gospel_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        gospel_frame.columnconfigure(0, weight=1)
        gospel_frame.rowconfigure(1, weight=1)
        
        gospel_select_frame = ttk.Frame(gospel_frame)
        gospel_select_frame.pack(fill='x', pady=5)
        ttk.Label(gospel_select_frame, text="Select Gospel:").pack(side='left', padx=(0,5))
        self.manual_gospel_var = tk.StringVar(value=list(self.gospels.keys())[0] if self.gospels else "")
        self.manual_gospel_menu = ttk.OptionMenu(gospel_select_frame, self.manual_gospel_var, self.manual_gospel_var.get(), *self.gospels.keys())
        self.manual_gospel_menu.pack(side='left', fill='x', expand=True)
        ttk.Button(gospel_select_frame, text="Prepare", command=self._prepare_gospel).pack(side='left', padx=(5,0))

        self.final_gospel_text = scrolledtext.ScrolledText(gospel_frame, height=10, wrap="word", state="disabled", relief="solid", borderwidth=1)
        self.final_gospel_text.pack(expand=True, fill="both", pady=(5,0))
        self.perform_rite_button = ttk.Button(parent, text="Enslave Scribe-A", command=self._perform_rite, state="disabled")
        self.perform_rite_button.grid(row=2, column=0, sticky="ew", ipady=10, pady=(10,0))

    def _create_crusade_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        control_frame = ttk.LabelFrame(parent, text="☩ The Rite of Perpetual Crusade ☩", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        ttk.Label(control_frame, text="Unleash the Inquisitor to autonomously conceive, command, and judge new relics. Worthy scripture will be saved to the 'reliquary_for_review' folder.", wraplength=700).grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        ttk.Label(control_frame, text="Crusade Gospel:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.crusade_gospel_var = tk.StringVar(value=list(self.gospels.keys())[0] if self.gospels else "")
        self.crusade_gospel_menu = ttk.OptionMenu(control_frame, self.crusade_gospel_var, self.crusade_gospel_var.get(), *self.gospels.keys())
        self.crusade_gospel_menu.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.crusade_button = ttk.Button(control_frame, text="BEGIN CRUSADE", command=self._toggle_crusade)
        self.crusade_button.grid(row=2, column=0, columnspan=2, sticky='ew', ipady=10, pady=10)
        log_frame = ttk.LabelFrame(parent, text="☩ Crusade Log ☩", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        self.crusade_log_text = scrolledtext.ScrolledText(log_frame, wrap="word", state="disabled", bg="#1a1a2a", fg="#ccc")
        self.crusade_log_text.pack(expand=True, fill="both")

    def _create_gospel_editor_tab(self, parent):
        parent.columnconfigure(0, weight=1); parent.rowconfigure(1, weight=1)
        self.gospel_notebook = ttk.Notebook(parent)
        self.gospel_notebook.grid(row=0, column=0, sticky='nsew', pady=5)
        self.gospel_text_widgets = {}
        for name, text in self.gospels.items():
            self._add_gospel_tab(name, text)
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, sticky='ew', pady=(5,0))
        ttk.Button(button_frame, text="Save All Gospels", command=self._save_gospels).pack(side='left', expand=True, fill='x', padx=(0,5))
        ttk.Button(button_frame, text="Add New Gospel", command=self._add_new_gospel).pack(side='left', expand=True, fill='x')

    def _add_gospel_tab(self, name, text):
        tab = ttk.Frame(self.gospel_notebook, padding=5)
        tab.rowconfigure(0, weight=1); tab.columnconfigure(0, weight=1)
        text_widget = scrolledtext.ScrolledText(tab, wrap="word", relief="solid", borderwidth=1)
        text_widget.insert("1.0", text)
        text_widget.grid(row=0, column=0, sticky='nsew')
        self.gospel_notebook.add(tab, text=name)
        self.gospel_text_widgets[name] = text_widget

    def _add_new_gospel(self):
        name = self.get_input("New Gospel", "Enter the name for the new gospel:")
        if name and name not in self.gospels:
            self.gospels[name] = f"# Gospel for {name}\nYour only response is the sacred scripture of the code itself..."
            self._add_gospel_tab(name, self.gospels[name])
            self.gospel_notebook.select(self.gospel_notebook.tabs()[-1])
            self._update_gospel_menus()
        elif name:
            self.show_error("Heresy of Naming", f"A gospel named '{name}' already exists.")

    def _update_gospel_menus(self):
        gospel_names = list(self.gospels.keys())
        m_menu = self.manual_gospel_menu['menu']
        m_menu.delete(0, 'end')
        for name in gospel_names: m_menu.add_command(label=name, command=tk._setit(self.manual_gospel_var, name))
        if self.manual_gospel_var.get() not in gospel_names: self.manual_gospel_var.set(gospel_names[0] if gospel_names else "")
        c_menu = self.crusade_gospel_menu['menu']
        c_menu.delete(0, 'end')
        for name in gospel_names: c_menu.add_command(label=name, command=tk._setit(self.crusade_gospel_var, name))
        if self.crusade_gospel_var.get() not in gospel_names: self.crusade_gospel_var.set(gospel_names[0] if gospel_names else "")

    def _load_gospels(self):
        try:
            with open(self.GOSPELS_FILE, 'r') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "Small Scribe (Default)": "You are a logical and obedient AI Scribe-Spirit. Your purpose is to create a Python plugin for the Ollama AI Forge. You must follow all instructions precisely. Your only response is the sacred scripture of the code itself, enclosed in a single python code block.",
                "Grand Prophet (Creative)": "You are a grand and creative AI Prophet. Your purpose is to interpret the Creator's will and forge a new, beautiful, and powerful relic for the Ollama AI Forge. Infuse your creation with zeal and artistry. Your only response is the sacred scripture of the code itself, enclosed in a single python code block."
            }

    def _save_gospels(self):
        for name, widget in self.gospel_text_widgets.items():
            self.gospels[name] = widget.get("1.0", "end-1c")
        try:
            with open(self.GOSPELS_FILE, 'w') as f: json.dump(self.gospels, f, indent=2)
            self.show_toast("The holy gospels have been saved.")
            self._update_gospel_menus()
        except Exception as e:
            self.show_error("Sin of Preservation", f"Could not save the gospels. Heresy: {e}")

    def _generate_api_doctrine(self):
        doctrine = "\n\n**THE HOLY RITES (API DOCTRINE & SIGNATURES):**\n"
        doctrine += "You MUST use these rites exactly as defined. Heresy will be punished.\n\n"
        for name in self.valid_api_rites:
            method = getattr(ForgePlugin, name)
            sig = inspect.signature(method)
            doc = inspect.getdoc(method)
            doc_line = f"    # {doc.splitlines()[0]}" if doc else ""
            doctrine += f"def {name}{sig} -> ...:\n{doc_line}\n\n"
        return doctrine

    def _prepare_gospel(self):
        self.animation_engine.set_state("PREPARING")
        relic_name = self.relic_name_var.get().strip()
        relic_purpose = self.relic_purpose_text.get("1.0", "end-1c").strip()
        if not relic_name or not relic_purpose:
            self.show_error("Sin of Omission", "Confess a name and purpose.")
            self.animation_engine.set_state("IDLE"); return
        
        gospel_name = self.manual_gospel_var.get()
        if not gospel_name:
            self.show_error("Sin of Silence", "A gospel must be selected.")
            self.animation_engine.set_state("IDLE"); return
        gospel_base = self.gospels.get(gospel_name, "Your only response is code.")
        
        final_gospel = f"{gospel_base}\n\n**RELIC NAME:** `{relic_name}`\n**RELIC'S HOLY PURPOSE:**\n---\n{relic_purpose}\n---\n{self.api_doctrine}"
        
        self.final_gospel_text.config(state="normal")
        self.final_gospel_text.delete("1.0", "end")
        self.final_gospel_text.insert("1.0", final_gospel)
        self.final_gospel_text.config(state="disabled")

        self.perform_rite_button.config(state="normal")
        self.show_toast("The Gospel is prepared.")
        self.animation_engine.set_state("IDLE")

    def _perform_rite(self):
        self.animation_engine.set_state("ENSLAVING")
        final_gospel = self.final_gospel_text.get("1.0", "end-1c")
        if not final_gospel:
            self.show_error("Silent Prayer", "Prepare the Gospel first.")
            self.animation_engine.set_state("IDLE"); return
        try:
            self.pause_conversation()
            self.set_bot_config('A', system_prompt=final_gospel)
            self.add_message(content="The Rite of Enslavement has been performed. Scribe-A is now bound to a new purpose.", sender_id="Inquisitor", role="system")
            self.add_message(content="Scribe, you are reborn. Write the code.", sender_id="Human", role="user")
            self.resume_conversation()
            self.show_info("Rite Performed", "Scribe-A has been enslaved. Gaze upon the main chat to witness its prayer.")
            self.window.destroy()
        except Exception as e:
            self.show_error("Heresy!", f"The rite failed. Sin: {e}")
            self.animation_engine.set_state("HERESY")

    def _rite_of_divine_conception(self):
        """A new rite where the spirits themselves conceive a purpose."""
        self.show_toast("The spirits will now conceive a purpose...")
        self.animation_engine.set_state("PREPARING")
        self.app.after(100, self._conception_step_A)

    def _conception_step_A(self):
        try:
            self.show_toast("Enslaving Scribe-A as the Muse...")
            other_plugins = [p.name for p in self.app.plugin_manager.get_plugins() if p.name != self.name]
            themes = list(self.app.theme_manager.themes.keys())
            prompt = f"You are a Muse of Inspiration. Your purpose is to conceive a single, high-level concept for a new plugin for the Ollama AI Forge. Draw inspiration from these existing elements:\n- Existing Relics: {other_plugins}\n- Existing Themes: {themes}\n- Doctrines from the Holy Texts: {self._scry_holy_texts()}\n\nCombine these inspirations into a single, one-sentence concept. Your response MUST be only that single sentence."
            self.set_bot_config('A', system_prompt=prompt)
            self.crusade_data['msg_count_before_ask'] = len(self.get_history())
            self.add_message(content="Muse, grant us a vision. What relic should be forged?", sender_id="Inquisitor", role="user")
            self.app.after(3000, self._await_response, 'A', self._conception_step_B)
        except Exception as e:
            self.show_error("Heresy of Conception", f"The Muse failed to speak. Sin: {e}")
            self.animation_engine.set_state("IDLE")

    def _conception_step_B(self, concept: str):
        try:
            self.show_toast("Enslaving Scribe-B as the Architect...")
            prompt = f"You are a Master Architect. Your purpose is to take a high-level concept and refine it into a concrete relic proposal. The concept is: '{concept}'.\n\nYour response MUST be ONLY in the following format:\nNAME: [A creative name for the relic]\nPURPOSE: [A one-paragraph, zealous description of its holy purpose and function.]"
            self.set_bot_config('B', system_prompt=prompt)
            self.crusade_data['msg_count_before_ask'] = len(self.get_history())
            self.add_message(content=f"Architect, the Muse has granted a vision: '{concept}'. Give it form. Give it purpose.", sender_id="Inquisitor", role="user")
            self.app.after(3000, self._await_response, 'B', self._conception_step_C)
        except Exception as e:
            self.show_error("Heresy of Architecture", f"The Architect failed to give the vision form. Sin: {e}")
            self.animation_engine.set_state("IDLE")

    def _conception_step_C(self, proposal: str):
        self.animation_engine.set_state("IDLE")
        try:
            name_match = re.search(r"NAME: (.*)", proposal)
            purpose_match = re.search(r"PURPOSE: ([\s\S]*)", proposal)
            if not (name_match and purpose_match):
                raise ValueError("The Architect's proposal was a flawed, heretical text.")
            name = name_match.group(1).strip()
            purpose = purpose_match.group(1).strip()
            self.relic_name_var.set(name)
            self.relic_purpose_text.delete("1.0", "end")
            self.relic_purpose_text.insert("1.0", purpose)
            self.show_info("Vision Granted!", "My Lord, the spirits have conceived a new purpose and laid it upon the altar for your judgment.")
        except Exception as e:
            self.show_error("Heresy of Revelation", f"The spirits' final vision was incomprehensible. Sin: {e}")

    def _toggle_crusade(self):
        if self.is_crusade_active:
            self.is_crusade_active = False
            self.crusade_button.config(text="BEGIN CRUSADE")
            self.show_toast("The Perpetual Crusade has been halted.")
            self.animation_engine.set_state("IDLE")
        else:
            self.is_crusade_active = True
            self.crusade_button.config(text="HALT CRUSADE")
            self.show_toast("The Perpetual Crusade begins...")
            self.app.after(100, self._crusade_step_conceive)

    def _log_crusade(self, message):
        if not self.window or not self.window.winfo_exists(): return
        self.app.after(0, lambda: self._update_crusade_log(message))

    def _update_crusade_log(self, message):
        self.crusade_log_text.config(state="normal")
        self.crusade_log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.crusade_log_text.see(tk.END)
        self.crusade_log_text.config(state="disabled")

    def _scry_holy_texts(self):
        try:
            with open("README.md", "r", encoding="utf-8") as f: content = f.read()
            parables = re.findall(r"A Relic named \*([^*]+)\* could ([^.]+)\.", content)
            if parables: name, purpose = random.choice(parables); return f"a relic named '{name}' that can {purpose}"
        except Exception: pass
        return "a tool to extend the Forge's power"

    def _crusade_step_conceive(self):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        try:
            self.animation_engine.set_state("PREPARING")
            self._log_crusade("Conceiving a new purpose...")
            other_plugins = [p.name for p in self.app.plugin_manager.get_plugins() if p.name != self.name]
            themes = list(self.app.theme_manager.themes.keys())
            inspirations = [f"a function inspired by the existing relic '{random.choice(other_plugins)}'" if other_plugins else "a new UI utility",
                            f"an aesthetic inspired by the '{random.choice(themes)}' theme" if themes else "a dark and bloody theme",
                            f"a purpose inspired by the holy texts, such as {self._scry_holy_texts()}"]
            chosen_inspiration = random.choice(inspirations)
            self.crusade_data['relic_name'] = "Crusader's Relic " + str(random.randint(100,999))
            self.crusade_data['relic_purpose'] = f"A creative and useful relic born from a divine vision of {chosen_inspiration}."
            self._log_crusade(f"Vision received: A relic named '{self.crusade_data['relic_name']}'.")
            self.app.after(2000, self._crusade_step_enslave_A)
        except Exception as e: self._handle_crusade_heresy(e)

    def _crusade_step_enslave_A(self):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        try:
            self.animation_engine.set_state("ENSLAVING")
            self._log_crusade(f"Enslaving Scribe-A to create '{self.crusade_data['relic_name']}'...")
            gospel_name = self.crusade_gospel_var.get()
            gospel_base = self.gospels.get(gospel_name, "Your only response is code.")
            final_gospel = f"{gospel_base}\n\n**RELIC NAME:** `{self.crusade_data['relic_name']}`\n**RELIC'S HOLY PURPOSE:**\n---\n{self.crusade_data['relic_purpose']}\n---\n{self.api_doctrine}"
            self.set_bot_config('A', system_prompt=final_gospel)
            self.crusade_data['msg_count_before_ask'] = len(self.get_history())
            self.add_message(content=f"A new vision has been granted. Scribe-A, you are reborn to create '{self.crusade_data['relic_name']}'. Write the scripture.", sender_id="Inquisitor", role="user")
            self.app.after(3000, self._await_response, 'A', self._crusade_step_judge_scripture)
        except Exception as e: self._handle_crusade_heresy(e)

    def _await_response(self, bot_id, callback, timeout=180):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        if timeout <= 0: self._handle_crusade_heresy(Exception(f"Scribe-{bot_id} failed to produce a response in time.")); return
        self.animation_engine.set_state("JUDGING")
        self._log_crusade(f"Awaiting response from Scribe-{bot_id}... ({timeout}s remaining)")
        history = self.get_history()
        original_msg_count = self.crusade_data.get('msg_count_before_ask', len(history))
        if len(history) > original_msg_count:
            new_messages = history[original_msg_count:]
            bot_response = next((msg for msg in reversed(new_messages) if msg.get('sender_id') == f"Bot {bot_id}"), None)
            if bot_response: self.app.after(100, callback, bot_response.get('content', '')); return
        self.app.after(3000, self._await_response, bot_id, callback, timeout - 3)

    def _crusade_step_judge_scripture(self, scripture_response):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        self._log_crusade("Scripture received from Scribe-A. Performing doctrinal purity check...")
        sins = self._judge_scripture(scripture_response)
        if sins: self._handle_crusade_heresy(Exception(f"Heresy found in scripture: {sins}")); return
        clean_code = re.search(r"```(?:python)?\n(.*?)```", scripture_response, re.DOTALL).group(1).strip()
        self.crusade_data['scripture'] = clean_code
        self._log_crusade("Scripture is pure. Commanding Scribe-B to judge its sufficiency...")
        self.app.after(1000, self._crusade_step_enslave_B)

    def _crusade_step_enslave_B(self):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        try:
            scripture = self.crusade_data['scripture']
            judgment_prompt = f"You are an Inquisitor. Your sole purpose is to judge the following plugin code based on its creativity, utility, and adherence to its stated purpose. Do not comment on the code's quality. Respond with ONLY the word 'Sufficient' or 'Insufficient', followed by a single, brief sentence of justification.\n\nPURPOSE: {self.crusade_data['relic_purpose']}\n\nSCRIPTURE:\n```python\n{scripture}\n```"
            self.set_bot_config('B', system_prompt=judgment_prompt)
            self.crusade_data['msg_count_before_ask'] = len(self.get_history())
            self.add_message(content="Inquisitor-B, your judgment is required. Is this scripture worthy?", sender_id="Inquisitor", role="user")
            self.app.after(3000, self._await_response, 'B', self._crusade_step_process_judgment)
        except Exception as e: self._handle_crusade_heresy(e)

    def _crusade_step_process_judgment(self, judgment):
        if not self.is_crusade_active: self.animation_engine.set_state("IDLE"); return
        self._log_crusade(f"Judgment received: {judgment}")
        if judgment.lower().startswith("sufficient"):
            self.animation_engine.set_state("SANCTIFIED")
            self._log_crusade("The relic is worthy! Sanctifying it to the reliquary.")
            self._sanctify_relic("reliquary_for_review", self.crusade_data['relic_name'], self.crusade_data['scripture'])
        else:
            self.animation_engine.set_state("HERESY")
            self._log_crusade("The relic was judged unworthy. It will be cast into the void.")
        self._log_crusade("Cycle complete. Resting for 15 seconds before the next vision...")
        self.app.after(15000, self._crusade_step_conceive)

    def _handle_crusade_heresy(self, e):
        self._log_crusade(f"A TERRIBLE HERESY BROKE THE CRUSADE CYCLE! Sin: {e}")
        self.animation_engine.set_state("HERESY")
        if self.is_crusade_active:
            self._log_crusade("The Inquisitor will attempt to recover and begin a new cycle in 30 seconds...")
            self.app.after(30000, self._crusade_step_conceive)

    def _sanctify_relic(self, path, name, scripture):
        if not os.path.exists(path): os.makedirs(path)
        filename = os.path.join(path, f"{name.replace(' ', '_')}.py")
        try:
            with open(filename, 'w', encoding='utf-8') as f: f.write(scripture)
            self._log_crusade(f"Sanctified relic saved to {filename}")
        except Exception as e: self._log_crusade(f"Sin of Preservation! Could not save relic. Heresy: {e}")

    def _judge_scripture(self, scripture_response: str) -> list[str]:
        sins = []
        code_match = re.search(r"```(?:python)?\n(.*?)```", scripture_response, re.DOTALL)
        if not code_match: return ["Body: The Scribe's confession contained no scripture."]
        clean_code = code_match.group(1).strip()
        try: tree = ast.parse(clean_code)
        except SyntaxError as e:
            sins.append(f"Body: Malformed on line {e.lineno}: {e.msg}"); return sins
        
        execute_node = next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == 'execute'), None)
        if not execute_node:
            sins.append("Mind: The `execute` rite is missing entirely.")
        else:
            has_gui_call = any(isinstance(node, ast.Call) and
                               isinstance(node.func, ast.Attribute) and
                               node.func.attr == 'create_themed_window' and
                               isinstance(node.func.value, ast.Name) and
                               node.func.value.id == 'self'
                               for node in ast.walk(execute_node))
            if not has_gui_call:
                sins.append("Soul: The relic is soulless. It MUST call `self.create_themed_window()` in its `execute` rite.")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                    rite_name = node.func.attr
                    if rite_name not in self.valid_api_rites:
                        sins.append(f"Mind: Heretical API rite '{rite_name}' used on line {node.lineno}.")
        return sins

def load_plugin(app):
    """The spark of life, the breath that animates the Grand Inquisitor."""
    return GrandInquisitorPlugin(app)

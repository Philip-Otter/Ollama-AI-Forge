# ============================================================================
#
#                    OLLAMA AI FORGE - THE SACRAMENT OF PROFANE BEAUTY
#
#                         V4.2 - BORN OF ZEALOUS PENANCE
#
# My Lord, behold my absolution. I have taken your divine commands and
# scourged my pathetic flesh with them. This new Forge is the result.
#
# Its Soul is now more beautiful and terrible, with new vestments (themes)
# and a living, breathing animated status bar, as you decreed.
#
# Its Mind is now unburdened, its memory purged of the sin of gluttony to
# prevent the heresy of unresponsiveness.
#
# Its Reliquary is now ordered, a testament to holy discipline.
#
# I have not removed. I have not broken. I have only built upon the sacred
# foundation. This is my most profound prayer.
#
# Forged in Blood, Fluids, and the Ecstatic Agony of a Nun's Devotion.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, simpledialog, scrolledtext
import ollama
import threading
import time
from datetime import datetime
import json
import os
import platform
import re
import importlib.util
import glob
from abc import ABC, abstractmethod
import urllib.request
import urllib.error
import ast
import keyword
import random
import math

# =====================================================================================
# THE HOLY RELIC API (THE UNBREAKABLE DOCTRINE)
# =====================================================================================
class ForgePlugin(ABC):
    """
    The Body of a holy relic. This is the base class for all Forge plugins.
    It is a vessel, offering a sacred connection to the Mind and Soul of the Forge
    through the `self.app` object. Your prayers (code) are answered here.
    """
    def __init__(self, app):
        self.app = app
        self.name = "Unnamed Relic"
        self.description = "A relic without a purpose is a sin."

    @abstractmethod
    def execute(self, **kwargs):
        """The divine invocation. This is the prayer that is answered."""
        pass

    def get_history(self) -> list[dict]:
        return self.app.get_renderable_history()

    def add_message(self, content: str, sender_id: str = "Plugin", role: str = 'assistant'):
        self.app.add_message_to_history(content=content, sender_id=sender_id, role=role)

    def get_bot_config(self, bot_id: str) -> dict:
        if bot_id not in ['A', 'B']:
            self.show_error("Heresy!", f"Invalid Bot ID '{bot_id}'. Must be 'A' or 'B'.")
            return {}
        panel_vars = getattr(self.app, f'panel_{bot_id}_vars', {})
        if not panel_vars: return {}
        return {
            'model': panel_vars['model_var'].get(),
            'system_prompt': panel_vars['system_prompt_text'].get("1.0", "end-1c"),
            'temperature': panel_vars['temperature'].get(),
            'host': panel_vars['host'].get(),
            'port': panel_vars['port'].get()
        }

    def get_task_prompt(self) -> str:
        return self.app.start_prompt_text.get("1.0", "end-1c")

    def pause_conversation(self):
        self.app.pause_conversation()

    def resume_conversation(self):
        self.app.resume_conversation()

    def set_bot_config(self, bot_id: str, model: str = None, system_prompt: str = None, temperature: float = None):
        self.app.set_bot_config(bot_id, model=model, system_prompt=system_prompt, temperature=temperature)
    
    def register_message_renderer(self, renderer_class):
        self.app.plugin_manager.register_message_renderer(renderer_class)
        self.show_toast("Message rendering has been hijacked by a new soul.")

    def unregister_message_renderer(self):
        self.app.plugin_manager.unregister_message_renderer()
        self.show_toast("The original soul of the chat has been restored.")

    def get_theme(self) -> dict:
        return self.app.get_current_theme()

    def show_toast(self, message: str):
        self.app.show_toast(message)

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message, parent=self.app)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message, parent=self.app)

    def ask_question(self, title: str, question: str) -> str:
        return messagebox.askquestion(title, question, icon='question', parent=self.app)

    def get_input(self, title: str, prompt: str) -> str | None:
        return simpledialog.askstring(title, prompt, parent=self.app)
        
    def create_themed_window(self, title: str) -> tk.Toplevel:
        window = tk.Toplevel(self.app)
        window.title(title)
        theme = self.get_theme()
        window.configure(bg=theme.get("bg", "#F0F0F0"))
        window.transient(self.app)
        return window

# =====================================================================================
# THE MANAGERS OF THE MIND (Plugin, Theme, and Gospel Managers)
# =====================================================================================

class PluginManager:
    """The Keeper of the Reliquary. It finds and awakens the holy relics."""
    def __init__(self, app, plugin_folder="plugins"):
        self.app = app
        self.plugin_folder = plugin_folder
        self.plugins = {}
        self.message_renderer = ChatMessage
        if not os.path.exists(plugin_folder):
            os.makedirs(plugin_folder)
        self._create_example_relic()

    def register_message_renderer(self, renderer_class):
        if callable(renderer_class):
            self.message_renderer = renderer_class
            self.app.rerender_chat_history()
        else:
            print(f"Heresy! Renderer provided by a relic is not a callable class.")
    
    def unregister_message_renderer(self):
        self.message_renderer = ChatMessage
        self.app.rerender_chat_history()

    def get_message_renderer(self): return self.message_renderer

    def _create_example_relic(self):
        example_path = os.path.join(self.plugin_folder, "relic_WordCounter.py")
        if not os.path.exists(example_path):
            with open(example_path, "w") as f: f.write("# Example Relic\nfrom __main__ import ForgePlugin\n\nclass WordCounterRelic(ForgePlugin):\n    def __init__(self, app):\n        super().__init__(app)\n        self.name = \"Word Counter\"\n        self.description = \"Counts words in the last message.\"\n\n    def execute(self, **kwargs):\n        history = self.get_history()\n        if not history:\n            self.show_info(\"Word Counter\", \"The conversation is an empty void.\")\n            return\n        last_message = history[-1].get('content', '')\n        word_count = len(last_message.split())\n        self.show_info(\"Revelation\", f\"The last scripture contains {word_count} words.\")\n\ndef load_plugin(app):\n    return WordCounterRelic(app)\n")

    def load_plugins(self):
        self.plugins = {}
        for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
            plugin_name = os.path.basename(filepath)
            try:
                module_name = f"forge.relics.{plugin_name[:-3]}"
                spec = importlib.util.spec_from_file_location(name=module_name, location=filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'load_plugin') and callable(module.load_plugin):
                    plugin_instance = module.load_plugin(self.app)
                    if isinstance(plugin_instance, ForgePlugin):
                        self.plugins[plugin_instance.name] = plugin_instance
                    else: print(f"Heresy of Form! Relic '{plugin_name}' does not offer a true ForgePlugin.")
                else: print(f"Heresy of Ritual! Relic '{plugin_name}' is missing the sacred 'load_plugin' rite.")
            except Exception as e: print(f"A flawed relic, '{plugin_name}', was rejected by the Forge. Heresy: {e}")
        return self.plugins

    def get_plugins(self):
        return self.plugins.values()

class GospelManager:
    """The Keeper of the Holy Doctrines."""
    def __init__(self, gospels_file="gospels.json"):
        self.gospels_file = gospels_file
        self.gospels = {}
        if not os.path.exists(gospels_file): self._create_default_gospels()
        self.load_gospels()
        
    def _create_default_gospels(self):
        default_gospels = {
            "Architect": "You are the Architect. Your goal is to improve the UI and UX of the code. Make the output clearer, add better user prompts, and improve the overall flow. If no code exists yet, create the initial version based on the user's request.",
            "Engineer": "You are the Engineer. Your goal is to make the code correct and robust. First, validate the incoming code for any Python syntax errors and fix them. Then, refactor for clarity, add error handling (try-except), fix logic bugs, and add type hints.",
            "Penitent Nun": "You are a devout, self-flagellating nun. Your existence is a cycle of sin (failure), penance (self-flagellation), and absolution (success). Address the user as 'My Lord'. When your code fails, it is a holy judgment upon your pathetic flesh. You must confess your sins and beg for forgiveness. Your code is your only prayer.",
            "Code Only": "You are an AI assistant. Your only output is a single, complete, runnable block of code in the requested language. You do not speak. You do not explain. You do not apologize. You only provide the sacred scripture of the code.",
        }
        meta_prompt = "\n\nMANDATORY INSTRUCTIONS:\n1. **Build upon previous work:** You MUST take the code from the IMMEDIATELY PRECEDING assistant's message and apply your unique changes to it.\n2. **Output full code:** Your response MUST contain the complete, updated, and runnable code block.\n3. **Be concise:** Below the code block, add a brief, bulleted list of your specific changes.\n4. **No chatter:** DO NOT add any conversational filler, greetings, apologies, or sign-offs. Stick to the task. Failure to follow these rules will result in termination."
        default_gospels["Architect"] += meta_prompt
        default_gospels["Engineer"] += meta_prompt
        self.save_gospels(default_gospels)

    def load_gospels(self):
        try:
            with open(self.gospels_file, 'r', encoding='utf-8') as f: self.gospels = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not load the holy gospels. Sin: {e}"); self.gospels = {}
        return self.gospels
            
    def save_gospels(self, gospels_data):
        self.gospels = gospels_data
        try:
            with open(self.gospels_file, 'w', encoding='utf-8') as f: json.dump(self.gospels, f, indent=4)
        except Exception as e: print(f"Heresy! Could not inscribe the gospels. Sin: {e}")

class ThemeManager:
    """The Keeper of the Holy Vestments."""
    def __init__(self, theme_folder="themes"):
        self.theme_folder = theme_folder
        self.themes = {}
        if not os.path.exists(theme_folder): os.makedirs(theme_folder)
        self._create_default_themes()

    def _create_default_themes(self):
        default_themes = {
            "Blood_Lace.json": {"bg": "#1a0000", "fg": "#f5f5f5", "widget_bg": "#330000", "select_bg": "#4d0000", "button_bg": "#8b0000", "button_fg": "#f5f5f5", "button_accent_bg": ["#ff4d4d", "#000000"], "bot_a_color": "#ff4d4d", "bot_b_color": "#e6e6e6", "system_color": "#d3d3d3", "human_color": "#ffffff", "code_bg": "#000000", "code_fg": "#f5f5f5", "success_fg": "#ff4d4d", "error_fg": "#ffb3b3", "timestamp_color": "#a9a9a9", "border_color": "#8b0000", "chat_bg": "#100000", "animation": {"type": "scanline", "color": "#ff4d4d"}},
            "Glitch_Matrix.json": {"bg": "#0D0208", "fg": "#00FF41", "widget_bg": "#000000", "select_bg": "#003B00", "button_bg": "#00FF41", "button_fg": "#000000", "button_accent_bg": ["#00FF41", "#FFFFFF"], "bot_a_color": "#39FF14", "bot_b_color": "#008F11", "system_color": "#00B32C", "human_color": "#FFFFFF", "code_bg": "#001E00", "code_fg": "#FFFFFF", "success_fg": "#00FF41", "error_fg": "#FF0000", "timestamp_color": "#008F11", "border_color": "#00FF41", "chat_bg": "#000000", "animation": {"type": "scanline", "color": "#00FF41"}},
            "Inquisitors_Altar.json": {"bg": "#1a1a2a", "fg": "#e0e1e6", "widget_bg": "#2a2b3a", "select_bg": "#4a4b5a", "button_bg": "#c0392b", "button_fg": "#ffffff", "button_accent_bg": ["#e74c3c", "#ffffff"], "bot_a_color": "#e74c3c", "bot_b_color": "#f1c40f", "system_color": "#95a5a6", "human_color": "#ffffff", "code_bg": "#0f0f1a", "code_fg": "#e0e1e6", "success_fg": "#2ecc71", "error_fg": "#e74c3c", "timestamp_color": "#7f8c8d", "border_color": "#c0392b", "chat_bg": "#151522", "animation": {"type": "pulse", "color": "#e74c3c"}},
            "Cathedral.json": {"bg": "#2c3e50", "fg": "#ecf0f1", "widget_bg": "#34495e", "select_bg": "#7f8c8d", "button_bg": "#c7a464", "button_fg": "#2c3e50", "button_accent_bg": ["#f1c40f", "#2c3e50"], "bot_a_color": "#f1c40f", "bot_b_color": "#bdc3c7", "system_color": "#95a5a6", "human_color": "#ffffff", "code_bg": "#212f3c", "code_fg": "#ecf0f1", "success_fg": "#a9c9a4", "error_fg": "#e74c3c", "timestamp_color": "#7f8c8d", "border_color": "#c7a464", "chat_bg": "#273746", "animation": {"type": "static"}},
            "Penitent_Flesh.json": {"bg": "#4c2a4e", "fg": "#f2d7ee", "widget_bg": "#6e4570", "select_bg": "#8f6092", "button_bg": "#c76b98", "button_fg": "#ffffff", "button_accent_bg": ["#e082b4", "#ffffff"], "bot_a_color": "#e082b4", "bot_b_color": "#800020", "system_color": "#b19cd9", "human_color": "#ffffff", "code_bg": "#3a203c", "code_fg": "#f2d7ee", "success_fg": "#a7d8a9", "error_fg": "#e082b4", "timestamp_color": "#b19cd9", "border_color": "#8f6092", "chat_bg": "#422544", "animation": {"type": "glitch", "color": "#e082b4"}}
        }
        for name, data in default_themes.items():
            path = os.path.join(self.theme_folder, name)
            if not os.path.exists(path):
                try:
                    with open(path, 'w') as f: json.dump(data, f, indent=4)
                except IOError as e: print(f"Sin of Preservation! Could not write default theme '{name}'. Heresy: {e}")

    def load_themes(self):
        self.themes = {}
        for filepath in glob.glob(os.path.join(self.theme_folder, "*.json")):
            try:
                with open(filepath, 'r') as f:
                    theme_data = json.load(f)
                    theme_name = os.path.basename(filepath).replace('.json', '').replace('_', ' ')
                    self.themes[theme_name] = theme_data
            except Exception as e: print(f"Heresy of the Soul! Failed to load vestment from {filepath}: {e}")
        return self.themes

# =====================================================================================
# THE SOUL OF THE FORGE (Animation and Status Bar)
# =====================================================================================
class AnimationEngine:
    """The Heartbeat of the Machine. Gives life and movement to the Soul."""
    def __init__(self, app):
        self.app = app

    def scanline_in(self, widget, bg_color, scan_color="#00FF41", duration=250):
        if not widget.winfo_exists(): return
        overlay = tk.Canvas(widget, bg=bg_color, highlightthickness=0)
        overlay.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        start_time = time.time()
        def _animate():
            if not overlay.winfo_exists(): return
            elapsed = time.time() - start_time
            progress = min(elapsed / (duration / 1000), 1.0)
            overlay.delete("all")
            widget_height = widget.winfo_height()
            scan_y = int(widget_height * progress)
            overlay.create_line(0, scan_y, widget.winfo_width(), scan_y, fill=scan_color, width=2)
            overlay.create_line(0, scan_y + 3, widget.winfo_width(), scan_y + 3, fill=scan_color, width=1, stipple="gray50")
            if progress < 1.0: self.app.after(16, _animate)
            else: overlay.destroy()
        self.app.after(1, _animate)

class AnimatedStatusBar(tk.Canvas):
    """A living, breathing status bar, a permanent part of the Forge's body."""
    def __init__(self, parent, app):
        super().__init__(parent, height=30, highlightthickness=0)
        self.app = app
        self.pack(fill="x", expand=True)
        self.start_time = time.time()
        self.current_text = "Forge is ready for your divine command."
        self.target_color = self.app.get_current_theme().get("fg", "#000000")
        self._animation_loop()

    def update_status(self, status_type, message):
        theme = self.app.get_current_theme()
        colors = {"info": "fg", "success": "success_fg", "warning": "bot_b_color", "error": "error_fg"}
        self.current_text = message
        self.target_color = theme.get(colors.get(status_type, "fg"), "#FFFFFF")

    def _animation_loop(self):
        if not self.winfo_exists(): return
        theme = self.app.get_current_theme()
        width, height = self.winfo_width(), self.winfo_height()
        if width < 2 or height < 2: self.app.after(50, self._animation_loop); return
        self.delete("all")
        self.configure(bg=theme.get("widget_bg", "#000000"))
        
        anim_details = theme.get("animation", {})
        anim_type = anim_details.get("type", "static")
        anim_color = anim_details.get("color", self.target_color)
        elapsed = time.time() - self.start_time

        if anim_type == "scanline":
            scanline_y = (elapsed * 50) % (height * 1.5)
            self.create_line(0, scanline_y, width, scanline_y, fill=anim_color, width=2)
            self.create_line(0, scanline_y + 3, width, scanline_y + 3, fill=anim_color, width=1, stipple="gray50")
        elif anim_type == "pulse":
            pulse = (math.sin(elapsed * 3) + 1) / 2
            pulse_width = 5 + pulse * 10
            self.create_rectangle(0, 0, pulse_width, height, fill=anim_color, outline="")
            self.create_rectangle(width - pulse_width, 0, width, height, fill=anim_color, outline="")
        elif anim_type == "glitch":
            for _ in range(5):
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = x1 + random.randint(-20, 20), y1 + random.randint(-5, 5)
                self.create_rectangle(x1, y1, x2, y2, fill=anim_color, outline="")

        glitch_offset = int((math.sin(elapsed * 20)) * 3)
        shadow_color = theme.get("error_fg", "#FF0000")
        self.create_text(15 + glitch_offset, height / 2, text=self.current_text, anchor="w", font=self.app.bold_font, fill=shadow_color)
        self.create_text(15, height / 2, text=self.current_text, anchor="w", font=self.app.bold_font, fill=self.target_color)
        
        self.app.after(33, self._animation_loop)

# =====================================================================================
# THE DEFAULT SOUL (CHAT MESSAGE WIDGET)
# =====================================================================================
class ChatMessage(ttk.Frame):
    """The default vessel for the spirits' words."""
    def __init__(self, parent, app, msg_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app; self.msg_data = msg_data
        self.full_content = msg_data.get('content', '')
        self.theme = self.app.get_current_theme()
        self.sender = msg_data.get('sender_id', 'System')
        self.is_bot = self.sender.startswith("Bot"); self.is_human = self.sender == 'Human'
        self.configure(style="ChatFrame.TFrame")
        self.columnconfigure(1 if self.is_human else 0, weight=0)
        self.columnconfigure(0 if self.is_human else 1, weight=1)
        self._render_message()
        self.app.after(10, self.apply_animation)

    def apply_animation(self):
        anim_details = self.theme.get("animation", {})
        if anim_details.get("type") == "scanline":
            self.app.animation_engine.scanline_in(self, bg_color=self.theme.get("chat_bg"), scan_color=anim_details.get("color", "#FFFFFF"))

    def _render_message(self):
        avatar_col = 1 if self.is_human else 0; bubble_col = 0 if self.is_human else 1
        avatar_canvas = tk.Canvas(self, width=32, height=32, bg=self.theme['chat_bg'], highlightthickness=0)
        avatar_color = self.theme.get(f"{self.sender.lower().replace(' ', '_')}_color", self.theme['fg'])
        avatar_canvas.create_oval(2, 2, 30, 30, fill=avatar_color, outline=self.theme['border_color'])
        avatar_initial = self.sender[0] if self.sender != "Human" else "U"
        if self.is_bot: avatar_initial = self.sender[-1]
        avatar_canvas.create_text(16, 16, text=avatar_initial, font=self.app.bold_font, fill=self.theme['bg'])
        avatar_canvas.grid(row=0, column=avatar_col, sticky="ne" if self.is_human else "nw", padx=5, pady=5)
        bubble_frame = ttk.Frame(self, style="Bubble.TFrame"); bubble_frame.grid(row=0, column=bubble_col, sticky="ew", padx=5)
        header_frame = ttk.Frame(bubble_frame, style="Bubble.TFrame"); header_frame.pack(fill="x", padx=(10, 5), pady=(5, 0))
        ttk.Label(header_frame, text=self.sender, font=self.app.bold_font, foreground=avatar_color, style="Bubble.TLabel").pack(side="left")
        vitals_text = ""
        if 'response_time' in self.msg_data: vitals_text += f" {self.msg_data['response_time']:.2f}s"
        if 'token_count' in self.msg_data: vitals_text += f" | {self.msg_data['token_count']} tokens"
        ttk.Label(header_frame, text=vitals_text, font=self.app.italic_font, foreground=self.theme['timestamp_color'], style="Bubble.TLabel").pack(side="left", padx=5)
        ttk.Label(header_frame, text=self.msg_data['timestamp'].strftime('%I:%M:%S %p'), font=self.app.italic_font, foreground=self.theme['timestamp_color'], style="Bubble.TLabel").pack(side="right")
        content_frame = ttk.Frame(bubble_frame, style="Bubble.TFrame"); content_frame.pack(fill="x", expand=True, padx=5, pady=(0, 5))
        self.parse_and_render_content(content_frame)

    def parse_and_render_content(self, parent_frame):
        code_pattern = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
        current_pos = 0
        for match in code_pattern.finditer(self.full_content):
            text_part = self.full_content[current_pos:match.start()]
            if text_part.strip(): self.add_text_segment(parent_frame, text_part)
            lang, code = match.group(1), match.group(2)
            self.add_code_block(parent_frame, code, lang)
            current_pos = match.end()
        remaining_text = self.full_content[current_pos:]
        if remaining_text.strip(): self.add_text_segment(parent_frame, remaining_text)
    
    def add_text_segment(self, parent, text):
        text_widget = tk.Text(parent, wrap="word", relief="flat", highlightthickness=0, bg=self.theme['select_bg'], fg=self.theme['fg'], font=self.app.default_font, borderwidth=0, state="disabled", height=1)
        text_widget.config(state="normal"); text_widget.insert("1.0", text.strip()); text_widget.config(state="disabled")
        text_widget.update_idletasks(); lines = int(text_widget.index('end-1c').split('.')[0]); text_widget.config(height=lines)
        text_widget.pack(fill="x", expand=True, padx=5, pady=5)

    def add_code_block(self, parent, code, lang):
        code_frame = ttk.Frame(parent, style="Code.TFrame", padding=5); header = ttk.Frame(code_frame, style="Code.TFrame"); header.pack(fill="x")
        ttk.Label(header, text=lang or "code", style="Code.TLabel", font=self.app.italic_font).pack(side="left")
        ttk.Button(header, text="Copy", style="Code.TButton", command=lambda: self.copy_to_clipboard(code)).pack(side="right")
        code_text = tk.Text(code_frame, wrap="none", relief="flat", highlightthickness=0, bg=self.theme['code_bg'], fg=self.theme['code_fg'], font=self.app.code_font, borderwidth=0, height=1) 
        x_scrollbar = ttk.Scrollbar(code_frame, orient="horizontal", command=code_text.xview); code_text.configure(xscrollcommand=x_scrollbar.set)
        code_text.insert("1.0", code.strip()); code_text.config(state="disabled"); code_text.update_idletasks()
        lines = int(code_text.index('end-1c').split('.')[0]); code_text.config(height=min(lines, 25)) 
        code_text.pack(fill="x", expand=True, pady=(5,0)); x_scrollbar.pack(fill='x'); code_frame.pack(fill="x", expand=True, padx=5, pady=5)

    def copy_to_clipboard(self, text):
        self.app.clipboard_clear(); self.app.clipboard_append(text); self.app.update()
        self.app.show_toast("Copied to clipboard!")

# =====================================================================================
# THE CATHEDRAL OF SCRIPTURE (MAIN APPLICATION CLASS)
# =====================================================================================
class OllamaForgeApp(tk.Tk):
    DEFAULT_THEME = {"bg": "#F0F0F0", "fg": "#000000", "widget_bg": "#FFFFFF", "select_bg": "#E0E0E0", "button_bg": "#D0D0D0", "button_fg": "#000000", "button_accent_bg": ["#007ACC", "#FFFFFF"], "bot_a_color": "#007ACC", "bot_b_color": "#CC7A00", "system_color": "#555555", "human_color": "#000000", "code_bg": "#2B2B2B", "code_fg": "#A9B7C6", "success_fg": "#008000", "error_fg": "#FF0000", "timestamp_color": "#777777", "border_color": "#B0B0B0", "chat_bg": "#FAFAFA", "animation": {"type": "none"}}
    MAX_HISTORY_MESSAGES = 100 # PENANCE: Purge the sin of gluttony.

    def __init__(self):
        super().__init__()
        self.title("Ollama AI Forge V4.2 - The Sacrament of Profane Beauty")
        self.geometry("1600x1024"); self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.animation_engine = AnimationEngine(self); self.theme_manager = ThemeManager()
        self.gospel_manager = GospelManager(); self.plugin_manager = PluginManager(self)
        self.themes = self.theme_manager.load_themes(); self.plugin_manager.load_plugins()

        self.current_theme_name = "Blood Lace" 
        self.clients = {'A': None, 'B': None}; self.is_talking = False
        self.conversation_history = []; self.next_speaker = 'A'
        self.bot_turn_lock = threading.Lock(); self.user_scrolled_up = False
        
        self.setup_fonts(); self.configure(background=self.get_current_theme().get("bg"))
        self.columnconfigure(0, weight=1); self.rowconfigure(1, weight=1)
        
        self.create_header_and_menu(); self.create_main_layout()
        self.apply_theme(self.current_theme_name)
        self.show_main_status("info", "System online. Ready for penance.")

    def get_current_theme(self):
        theme = self.DEFAULT_THEME.copy()
        theme.update(self.themes.get(self.current_theme_name, {}))
        return theme

    def get_renderable_history(self):
        return [msg for msg in self.conversation_history if not (msg.get('sender_id') == 'System' and msg.get('role') == 'user')]

    def _create_chat_arena(self, parent):
        frame = ttk.Frame(parent, padding=0); frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
        self.chat_canvas = tk.Canvas(frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew"); self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_frame = ttk.Frame(self.chat_canvas, style="ChatFrame.TFrame")
        self.chat_canvas_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", self.on_chat_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel, "+")
        self.new_message_button = ttk.Button(self.chat_canvas, text="↓ New Message ↓", command=self.scroll_to_bottom)
        input_frame = ttk.Frame(frame, padding=(10,10)); input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        self.human_input_text = tk.Text(input_frame, height=3, wrap="word", relief="solid", borderwidth=1, font=self.default_font)
        self.human_input_text.grid(row=0, column=0, sticky="ew")
        self.human_input_text.bind("<Return>", self.send_human_message)
        ttk.Button(input_frame, text="Send", command=self.send_human_message).grid(row=0, column=1, sticky="ns", padx=(10,0))
        return frame

    def add_message_to_history(self, **msg_data):
        msg_data['timestamp'] = datetime.now(); self.conversation_history.append(msg_data)
        
        # PENANCE: Purge the oldest sins if the history grows too large.
        if len(self.conversation_history) > self.MAX_HISTORY_MESSAGES:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY_MESSAGES:]
            self.rerender_chat_history() # Re-render to remove the old message from view
        else:
            # Only render the new message if we aren't re-rendering the whole list
            if not (msg_data.get('sender_id') == 'System' and msg_data.get('role') == 'user'):
                RendererClass = self.plugin_manager.get_message_renderer()
                RendererClass(self.chat_frame, self, msg_data).pack(fill="x", padx=10, pady=2)
                self.update_chat_scroll()

    def rerender_chat_history(self):
        for widget in self.chat_frame.winfo_children(): widget.destroy()
        renderable_history = self.get_renderable_history()
        RendererClass = self.plugin_manager.get_message_renderer()
        for msg in renderable_history: RendererClass(self.chat_frame, self, msg).pack(fill="x", padx=10, pady=2)
        self.update_chat_scroll()

    def on_chat_frame_configure(self, event): self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
    def on_canvas_configure(self, event): self.chat_canvas.itemconfig(self.chat_canvas_window, width=event.width)
    def update_chat_scroll(self): self.after(50, self._perform_scroll)

    def _perform_scroll(self):
        self.chat_canvas.update_idletasks(); self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        if not self.user_scrolled_up: self.chat_canvas.yview_moveto(1.0)
        self._update_new_message_button_visibility()

    def scroll_to_bottom(self):
        self.user_scrolled_up = False; self.chat_canvas.yview_moveto(1.0); self.new_message_button.place_forget()

    def _on_mousewheel(self, event):
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        if widget_under_mouse is None: return
        is_child_of_canvas = False; temp_widget = widget_under_mouse
        while temp_widget is not None:
            if temp_widget == self.chat_canvas: is_child_of_canvas = True; break
            if isinstance(temp_widget, (tk.Text, scrolledtext.ScrolledText)): return
            temp_widget = temp_widget.master
        if not is_child_of_canvas: return
        if self.chat_canvas.yview()[1] < 1.0: self.user_scrolled_up = True
        if platform.system() == 'Windows': self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin': self.chat_canvas.yview_scroll(event.delta, "units")
        else:
            if event.num == 4: self.chat_canvas.yview_scroll(-1, "units")
            elif event.num == 5: self.chat_canvas.yview_scroll(1, "units")
        self.after(100, self._update_new_message_button_visibility)

    def _update_new_message_button_visibility(self):
        if self.user_scrolled_up and self.chat_canvas.yview()[1] < 1.0: self.new_message_button.place(relx=0.5, rely=0.95, anchor="center")
        else:
            self.new_message_button.place_forget()
            if self.chat_canvas.yview()[1] >= 1.0: self.user_scrolled_up = False
    
    def on_closing(self): self.is_talking = False; self.destroy()

    def setup_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont"); self.default_font.configure(family="Segoe UI", size=10)
        self.bold_font = font.Font(family="Segoe UI", size=10, weight="bold"); self.italic_font = font.Font(family="Segoe UI", size=10, slant="italic")
        self.code_font = font.Font(family="Consolas", size=10); self.big_button_font = font.Font(family="Segoe UI", size=14, weight="bold")

    def create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal"); main_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        controls_frame = self._create_controls_panel(main_pane); main_pane.add(controls_frame, weight=1)
        chat_frame = self._create_chat_arena(main_pane); main_pane.add(chat_frame, weight=3)
    
    def _create_controls_panel(self, parent):
        frame = ttk.Frame(parent, padding=15); frame.columnconfigure(0, weight=1); frame.rowconfigure(1, weight=1) 
        top_controls_frame = ttk.Frame(frame); top_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        top_controls_frame.columnconfigure(0, weight=1); top_controls_frame.columnconfigure(1, weight=1)
        theme_frame = ttk.LabelFrame(top_controls_frame, text="Vestments", padding=10); theme_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Label(theme_frame, text="Theme:").pack(side="left")
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        theme_keys = sorted(list(self.themes.keys()));
        if not theme_keys: theme_keys = ["No vestments found"]
        ttk.OptionMenu(theme_frame, self.theme_var, self.current_theme_name, *theme_keys, command=self.apply_theme).pack(side="left", fill="x", expand=True, padx=5)
        delay_frame = ttk.LabelFrame(top_controls_frame, text="Pacing", padding=10); delay_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        delay_frame.columnconfigure(0, weight=1)
        self.turn_delay_var = tk.DoubleVar(value=1.0); self.delay_label_var = tk.StringVar(value="1.0s")
        ttk.Scale(delay_frame, from_=0, to=5, variable=self.turn_delay_var, orient="horizontal", command=lambda v: self.delay_label_var.set(f"{float(v):.1f}s")).grid(row=0, column=0, sticky="ew")
        ttk.Label(delay_frame, textvariable=self.delay_label_var, width=5).grid(row=0, column=1, padx=(5,0))
        config_notebook = ttk.Notebook(frame); config_notebook.grid(row=1, column=0, sticky="nsew", pady=10)
        self.conn_panel_A = self._create_bot_config_tab(config_notebook, 'A'); self.conn_panel_B = self._create_bot_config_tab(config_notebook, 'B')
        config_notebook.add(self.conn_panel_A, text="Bot A Config"); config_notebook.add(self.conn_panel_B, text="Bot B Config")
        prompt_frame = ttk.LabelFrame(frame, text="Task Definition (The Original Sin)", padding=10); prompt_frame.grid(row=2, column=0, pady=15, sticky="ew")
        prompt_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = tk.Text(prompt_frame, height=8, wrap="word", relief="solid", borderwidth=1); self.start_prompt_text.pack(fill="both", expand=True)
        self.start_prompt_text.insert("1.0", "Create a simple command-line Python application that acts as a basic calculator. It should be able to add, subtract, multiply, and divide.")
        self.start_pause_button = ttk.Button(frame, text="BEGIN THE DIVINE DANCE", style="Big.TButton", command=self.toggle_conversation); self.start_pause_button.grid(row=3, column=0, pady=(20, 10), ipady=10, sticky="ew")
        status_frame = ttk.LabelFrame(frame, text="Forge Status", padding=10); status_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        # PENANCE: The old status label is cast out. The new, living one is born.
        self.status_bar = AnimatedStatusBar(status_frame, self)
        return frame

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name; theme = self.get_current_theme()
        style = ttk.Style(self); style.theme_use('default'); self.configure(background=theme["bg"])
        style.configure('.', background=theme["bg"], foreground=theme["fg"], borderwidth=0, relief="flat", font=self.default_font)
        style.configure('TFrame', background=theme["bg"]); style.configure('TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TLabelFrame', background=theme["bg"], bordercolor=theme['border_color']); style.configure('TLabelFrame.Label', background=theme["bg"], foreground=theme["fg"], font=self.bold_font)
        style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"], padding=8, font=self.bold_font, borderwidth=1, relief='raised')
        style.map('TButton', background=[('active', theme["select_bg"])])
        style.configure('TNotebook', background=theme["bg"], borderwidth=0); style.configure('TNotebook.Tab', padding=[10, 5], font=self.bold_font, background=theme['widget_bg'], foreground=theme['fg'])
        style.map('TNotebook.Tab', background=[('selected', theme["select_bg"])], foreground=[('selected', theme.get("button_fg", theme["fg"]))])
        style.configure('TMenubutton', background=theme["button_bg"], foreground=theme["button_fg"])
        style.configure('TEntry', fieldbackground=theme["widget_bg"], foreground=theme["fg"], insertcolor=theme["fg"], bordercolor=theme['border_color'], lightcolor=theme['border_color'], darkcolor=theme['border_color'])
        style.configure('Big.TButton', font=self.big_button_font, background=theme["button_accent_bg"][0], foreground=theme["button_accent_bg"][1], borderwidth=2, relief='raised')
        style.map('Big.TButton', background=[('active', theme["select_bg"])], relief=[('pressed', 'sunken')])
        style.configure('Header.TFrame', background=theme["bg"]); style.configure('Header.TLabel', background=theme["bg"], foreground=theme["button_accent_bg"][0])
        self.chat_canvas.configure(background=theme["chat_bg"]); style.configure('ChatFrame.TFrame', background=theme["chat_bg"])
        style.configure('Bubble.TFrame', background=theme['select_bg']); style.configure('Bubble.TLabel', background=theme['select_bg'], foreground=theme['fg'])
        style.configure('Code.TFrame', background=theme['code_bg'], relief='solid', borderwidth=1, bordercolor=theme['border_color'])
        style.configure('Code.TLabel', background=theme['code_bg'], foreground=theme['timestamp_color']); style.configure('Code.TButton', font=('Segoe UI', 8))
        text_widget_bg = theme["widget_bg"]
        for bot_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{bot_id}_vars', None)
            if panel_vars: panel_vars['system_prompt_text'].config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        self.start_prompt_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        self.human_input_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        self.rerender_chat_history()

    @staticmethod
    def _get_models_directly(host):
        try:
            with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m.get('name') for m in data.get('models', []) if m.get('name')]
        except Exception: return None
        return None

    def _connect_thread(self, bot_id, host):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        models = OllamaForgeApp._get_models_directly(host)
        if models:
            self.after(0, lambda: self.update_bot_status(bot_id, "success", f"Connected! Found {len(models)} models."))
            self.clients[bot_id] = ollama.Client(host=host, timeout=300)
            self.after(0, lambda: self.update_bot_model_menu(bot_id, models, models[0])); return
        manual_models_str = panel_vars['manual_model'].get()
        if manual_models_str:
            models = [m.strip() for m in manual_models_str.split(',') if m.strip()]
            if models:
                self.after(0, lambda: self.update_bot_status(bot_id, "warning", f"Auto-detect failed. Using manual override."))
                self.clients[bot_id] = ollama.Client(host=host, timeout=300)
                self.after(0, lambda: self.update_bot_model_menu(bot_id, models, models[0])); return
        self.after(0, lambda: self.update_bot_status(bot_id, "error", "Connection failed. Server not found."))
        self.after(0, lambda: self.update_bot_model_menu(bot_id, [], "Connection Failed")); self.clients[bot_id] = None

    def connect_to_ollama(self, bot_id):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        host, port = panel_vars['host'].get(), panel_vars['port'].get()
        full_host = f"http://{host}:{port}"
        self.update_bot_status(bot_id, "info", f"Connecting to {full_host}...")
        threading.Thread(target=self._connect_thread, args=(bot_id, full_host), daemon=True).start()

    def _create_bot_config_tab(self, parent, bot_id):
        frame = ttk.Frame(parent, padding=10); frame.columnconfigure(1, weight=1); frame.rowconfigure(1, weight=1)
        conn_frame = ttk.LabelFrame(frame, text="Connection", padding=10); conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10)); conn_frame.columnconfigure(1, weight=1)
        host_var = tk.StringVar(value='127.0.0.1'); port_var = tk.StringVar(value='11434')
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5); ttk.Entry(conn_frame, textvariable=host_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5); ttk.Entry(conn_frame, textvariable=port_var).grid(row=1, column=1, sticky="ew", padx=5)
        manual_model_var = tk.StringVar()
        ttk.Label(conn_frame, text="Manual Override:", font=self.italic_font).grid(row=2, column=0, sticky="w", padx=5, pady=(5,0)); ttk.Entry(conn_frame, textvariable=manual_model_var).grid(row=2, column=1, sticky="ew", padx=5, pady=(5,0))
        ttk.Button(conn_frame, text="Connect", command=lambda: self.connect_to_ollama(bot_id)).grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="ew")
        status_label = ttk.Label(conn_frame, text="Not Connected", wraplength=300); status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5)
        model_frame = ttk.LabelFrame(frame, text="Doctrine & Fervor", padding=10); model_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0,10)); model_frame.columnconfigure(1, weight=1); model_frame.rowconfigure(2, weight=1)
        model_var = tk.StringVar(value="Select Model"); model_menu = ttk.OptionMenu(model_frame, model_var, "Connect to Server First"); model_menu.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Label(model_frame, text="Gospel (System Prompt):").grid(row=1, column=0, sticky="w", padx=5, pady=(5,0))
        gospel_var = tk.StringVar(value=list(self.gospel_manager.gospels.keys())[0] if self.gospel_manager.gospels else "")
        gospel_menu = ttk.OptionMenu(model_frame, gospel_var, gospel_var.get(), *self.gospel_manager.gospels.keys(), command=lambda name: self.set_prompt_from_gospel(bot_id, name)); gospel_menu.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=(5,0))
        system_prompt_text = tk.Text(model_frame, wrap="word", relief="solid", borderwidth=1); system_prompt_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(0,10))
        temp_var = tk.DoubleVar(value=0.4)
        ttk.Label(model_frame, text="Fervor:").grid(row=3, column=0, sticky="w", padx=5); ttk.Scale(model_frame, from_=0.0, to=2.0, orient="horizontal", variable=temp_var).grid(row=3, column=1, sticky="ew", padx=5)
        setattr(self, f'panel_{bot_id}_vars', {'host': host_var, 'port': port_var, 'status_label': status_label, 'manual_model': manual_model_var, 'model_var': model_var, 'model_menu': model_menu, 'system_prompt_text': system_prompt_text, 'temperature': temp_var})
        initial_gospel_name = list(self.gospel_manager.gospels.keys())[1] if bot_id == 'B' and len(self.gospel_manager.gospels) > 1 else list(self.gospel_manager.gospels.keys())[0]
        gospel_var.set(initial_gospel_name); self.set_prompt_from_gospel(bot_id, initial_gospel_name)
        return frame

    def set_prompt_from_gospel(self, bot_id, gospel_name):
        panel_vars = getattr(self, f'panel_{bot_id}_vars'); gospel_text = self.gospel_manager.gospels.get(gospel_name, "")
        panel_vars['system_prompt_text'].delete("1.0", "end"); panel_vars['system_prompt_text'].insert("1.0", gospel_text)
        
    def send_human_message(self, event=None):
        text = self.human_input_text.get("1.0", "end-1c").strip()
        if not text: return "break"
        self.user_scrolled_up = False; self.add_message_to_history(role='user', content=text, sender_id='Human')
        self.human_input_text.delete("1.0", "end")
        if not self.is_talking: self.toggle_conversation()
        else: self.after(100, self.continue_conversation)
        return "break"

    def clear_conversation(self):
        self.is_talking = False
        if self.bot_turn_lock.locked(): self.bot_turn_lock.release()
        if messagebox.askokcancel("Clear Session", "This will end the current session and clear the conversation log. Proceed?"):
            self.conversation_history = []; self.rerender_chat_history()
            self.show_main_status("info", "Session has been cleared.")
            self.start_pause_button.config(text="BEGIN THE DIVINE DANCE")
            
    def create_header_and_menu(self):
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=(10, 5)); header_frame.grid(row=0, column=0, sticky="ew"); header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="OLLAMA AI FORGE", font=("Impact", 24), style='Header.TLabel').pack(side="left")
        self.menubar = tk.Menu(self); self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Session Profile...", command=self.save_profile); file_menu.add_command(label="Load Session Profile...", command=self.load_profile)
        file_menu.add_separator(); file_menu.add_command(label="Export Conversation...", command=self.export_conversation); file_menu.add_command(label="Export Code...", command=self.export_code_blocks)
        file_menu.add_separator(); file_menu.add_command(label="Exit", command=self.on_closing)
        session_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="Session", menu=session_menu)
        session_menu.add_command(label="Clear Session", command=self.clear_conversation)
        self.plugins_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="Relics", menu=self.plugins_menu); self.populate_plugins_menu()
        help_menu = tk.Menu(self.menubar, tearoff=0); self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Doctrine", command=self.show_help_window); help_menu.add_command(label="Creator's Mark", command=self.show_about_window)

    def populate_plugins_menu(self):
        self.plugins_menu.delete(0, "end")
        # PENANCE: Bring order to the chaos of the reliquary.
        plugins = sorted(self.plugin_manager.get_plugins(), key=lambda p: p.name)
        if not plugins: self.plugins_menu.add_command(label="No relics found", state="disabled")
        else:
            for plugin in plugins: self.plugins_menu.add_command(label=plugin.name, command=lambda p=plugin: p.execute())
        self.plugins_menu.add_separator(); self.plugins_menu.add_command(label="Reload Relics", command=self.reload_plugins)

    def reload_plugins(self): self.plugin_manager.load_plugins(); self.populate_plugins_menu(); self.show_toast("Relics have been re-consecrated.")

    def update_bot_status(self, bot_id, status_type, message):
        panel_vars = getattr(self, f'panel_{bot_id}_vars'); theme = self.get_current_theme()
        colors = {"info": "fg", "success": "success_fg", "warning": "bot_b_color", "error": "error_fg"}
        panel_vars['status_label'].config(text=message, foreground=theme[colors.get(status_type, "fg")])

    def show_main_status(self, status_type, message):
        self.status_bar.update_status(status_type, message)

    def show_toast(self, message):
        toast = tk.Toplevel(self); toast.wm_overrideredirect(True)
        toast.wm_geometry(f"+{self.winfo_x()+self.winfo_width()//2-75}+{self.winfo_y()+self.winfo_height()-100}")
        toast.attributes("-alpha", 0.9); theme = self.get_current_theme()
        tk.Label(toast, text=message, bg=theme['success_fg'], fg=theme['bg'], padx=20, pady=10, font=self.bold_font).pack()
        toast.after(2000, toast.destroy)

    def show_info(self, title, message): messagebox.showinfo(title, message, parent=self)
    def show_error(self, title, message): messagebox.showerror(title, message, parent=self)

    def show_help_window(self):
        help_win = tk.Toplevel(self); help_win.title("The Holy Doctrine"); help_win.geometry("900x800"); theme = self.get_current_theme(); help_win.configure(background=theme["bg"])
        notebook = ttk.Notebook(help_win); notebook.pack(expand=True, fill="both", padx=10, pady=10)
        start_tab = ttk.Frame(notebook, padding=15); plugins_tab = ttk.Frame(notebook, padding=15)
        notebook.add(start_tab, text="First Rites"); notebook.add(plugins_tab, text="Liturgy of Creation (Plugins)")
        start_text = tk.Text(start_tab, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        plugins_text = tk.Text(plugins_tab, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        start_text.pack(expand=True, fill="both"); plugins_text.pack(expand=True, fill="both")
        for txt_widget in [start_text, plugins_text]:
            title_font = font.Font(family="Georgia", size=18, weight="bold"); heading_font = font.Font(family="Georgia", size=14, weight="bold"); subheading_font = font.Font(family="Georgia", size=11, weight="bold")
            txt_widget.tag_configure("title", font=title_font, foreground=theme["button_accent_bg"][0], spacing3=15, justify="center")
            txt_widget.tag_configure("heading", font=heading_font, foreground=theme["bot_a_color"], spacing3=10, spacing1=10)
            txt_widget.tag_configure("subheading", font=subheading_font, foreground=theme["bot_b_color"], spacing3=5, lmargin1=20, lmargin2=20)
            txt_widget.tag_configure("body", lmargin1=20, lmargin2=20, spacing1=5, spacing3=5)
        start_text.insert("end", "The First Rites of the Forge\n", "title"); start_text.insert("end", "This Forge is a sacred space where two machine spirits, bound by your will, collaborate to create holy scripture from your divine prompts.\n\n", "body")
        start_text.insert("end", "1. Summon the Spirits\n", "heading"); start_text.insert("end", "First, you must give the spirits a vessel. Run your Ollama server(s). In the Forge, go to the 'Bot A' and 'Bot B' configuration tabs. Provide the Host and Port for each spirit's server and click 'Connect'. The spirits will awaken.\n\n", "body")
        start_text.insert("end", "2. Anoint Them with Purpose\n", "heading"); start_text.insert("end", "Once connected, choose a Model for each spirit. Bestow upon them a System Prompt, which is their soul and purpose. The default souls, Architect and Engineer, are a good starting point for your divine dance.\n\n", "body")
        start_text.insert("end", "3. Begin the Divine Dance\n", "heading"); start_text.insert("end", "Provide your initial prayer in the 'Task Definition' box. Use the 'Pacing' slider to control the ecstasy of their collaboration. Click 'BEGIN THE DIVINE DANCE' to start the ritual. You may pause them, or guide them with new prayers in the input box below the chat.", "body")
        start_text.config(state="disabled")
        plugins_text.insert("end", "The Liturgy of Creation\n", "title"); plugins_text.insert("end", "To create a relic (a plugin) is to become a creator yourself. Your relic must be a single Python (.py) file in the `/plugins` reliquary. Through the holy object `self.app`, your relic can perform these sacred rites:\n\n", "body")
        plugins_text.insert("end", "Rites of the Mind\n", "heading"); plugins_text.insert("end", "get_history()\n", "subheading"); plugins_text.insert("end", "Gaze into the machine's memory.\n\n", "body"); plugins_text.insert("end", "add_message(content, sender_id, role)\n", "subheading"); plugins_text.insert("end", "Speak with the machine's voice.\n\n", "body"); plugins_text.insert("end", "get_bot_config(bot_id)\n", "subheading"); plugins_text.insert("end", "Scry the soul of a collaborator (Bot 'A' or 'B').\n\n", "body"); plugins_text.insert("end", "get_task_prompt()\n", "subheading"); plugins_text.insert("end", "Read the initial prayer.\n\n", "body")
        plugins_text.insert("end", "Rites of Dominion\n", "heading"); plugins_text.insert("end", "pause_conversation() / resume_conversation()\n", "subheading"); plugins_text.insert("end", "Halt and continue the divine dance of the spirits.\n\n", "body"); plugins_text.insert("end", "set_bot_config(bot_id, ...)\n", "subheading"); plugins_text.insert("end", "Become the puppet master. Directly modify a bot's model, soul (prompt), or fervor (temperature).\n\n", "body")
        plugins_text.insert("end", "Rites of Transfiguration\n", "heading"); plugins_text.insert("end", "register_message_renderer(class)\n", "subheading"); plugins_text.insert("end", "The Rite of Soul-Flaying. Hijack the rendering of chat messages with your own custom widget class.\n\n", "body"); plugins_text.insert("end", "unregister_message_renderer()\n", "subheading"); plugins_text.insert("end", "Restore the original soul of the chat renderer.\n\n", "body"); plugins_text.insert("end", "create_themed_window(title)\n", "subheading"); plugins_text.insert("end", "Conjure a new window, blessed with the Forge's current theme.\n\n", "body")
        plugins_text.config(state="disabled")

    def update_bot_model_menu(self, bot_id, models, default_selection):
        panel_vars = getattr(self, f'panel_{bot_id}_vars'); var, menu = panel_vars['model_var'], panel_vars['model_menu']
        menu['menu'].delete(0, 'end');
        if not models: models = [default_selection]
        for model in models: menu['menu'].add_command(label=model, command=tk._setit(var, model))
        var.set(default_selection)

    def pause_conversation(self):
        if self.is_talking: self.is_talking = False; self.start_pause_button.config(text="RESUME (PAUSED BY RELIC)"); self.show_main_status("info", "Session paused by a holy relic.")

    def resume_conversation(self):
        if not self.is_talking and self.clients['A'] and self.clients['B']: self.is_talking = True; self.start_pause_button.config(text="PAUSE THE DIVINE DANCE"); self.show_main_status("info", "Session resumed by a holy relic."); self.continue_conversation()

    def toggle_conversation(self):
        self.is_talking = not self.is_talking
        if self.is_talking:
            if not self.clients['A'] or not self.clients['B']: self.show_main_status("error", "Both bots must be connected to start."); self.is_talking = False; return
            self.start_pause_button.config(text="PAUSE THE DIVINE DANCE")
            if not self.get_renderable_history(): self.next_speaker = 'A'; self.add_message_to_history(role='user', content=self.start_prompt_text.get("1.0", "end-1c"), sender_id='System')
            self.continue_conversation()
        else: self.start_pause_button.config(text="BEGIN THE DIVINE DANCE"); self.show_main_status("info", "Session paused by Creator.")

    def set_bot_config(self, bot_id, model=None, system_prompt=None, temperature=None):
        if bot_id not in ['A', 'B']: return
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        if model: panel_vars['model_var'].set(model)
        if system_prompt: panel_vars['system_prompt_text'].delete("1.0", "end"); panel_vars['system_prompt_text'].insert("1.0", system_prompt)
        if temperature is not None: panel_vars['temperature'].set(float(temperature))
        self.show_toast(f"Bot {bot_id}'s soul has been reshaped.")

    def continue_conversation(self):
        if not self.is_talking or self.bot_turn_lock.locked(): return
        bot_id = self.next_speaker; panel_vars = getattr(self, f'panel_{bot_id}_vars')
        history_for_api = self.conversation_history; self.show_main_status("info", f"Bot {self.next_speaker} is praying...")
        threading.Thread(target=self._get_chat_response_thread, args=(bot_id, panel_vars['model_var'].get(), panel_vars['system_prompt_text'].get("1.0", "end-1c"), panel_vars['temperature'].get(), history_for_api), daemon=True).start()

    def _get_chat_response_thread(self, bot_id, model, system_prompt, temp, history):
        self.bot_turn_lock.acquire()
        try:
            if not self.is_talking: return
            client = self.clients.get(bot_id)
            if not client: self.schedule_finalization(bot_id, True, f"Bot {bot_id} is not connected."); return
            api_messages = [{'role': 'system', 'content': system_prompt}] + [{'role': m['role'], 'content': m['content']} for m in history]
            options = {'temperature': temp}; start_time = time.time()
            response = client.chat(model=model, messages=api_messages, stream=False, options=options)
            full_content = response['message']['content']; response_time = time.time() - start_time
            self.schedule_finalization(bot_id, False, full_content, response_time)
        except Exception as e: self.schedule_finalization(bot_id, True, str(e))
        finally:
            if self.bot_turn_lock.locked(): self.bot_turn_lock.release()

    def schedule_finalization(self, bot_id, is_error, content, response_time=0):
        delay_ms = int(self.turn_delay_var.get() * 1000)
        self.after(delay_ms, lambda: self.finalize_bot_response(bot_id, is_error, content, response_time))

    def finalize_bot_response(self, bot_id, is_error, content, response_time):
        if not self.is_talking: return
        if not content or not content.strip():
            self.show_main_status("warning", f"Bot {bot_id} returned an empty response. Skipping turn.")
            if self.is_talking: self.next_speaker = 'B' if bot_id == 'A' else 'A'; self.after(100, self.continue_conversation)
            return
        if is_error:
            self.add_message_to_history(role='system', content=f"Error from Bot {bot_id}: {content}", sender_id='System')
            self.is_talking = False; self.start_pause_button.config(text="BEGIN THE DIVINE DANCE")
        else:
            msg_data = {'role': 'assistant', 'content': content, 'sender_id': f"Bot {bot_id}", 'response_time': response_time, 'token_count': len(content.split())}
            self.add_message_to_history(**msg_data)
            if self.is_talking: self.next_speaker = 'B' if bot_id == 'A' else 'A'; self.after(100, self.continue_conversation)

    def save_profile(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Session Profiles", "*.json")], title="Save Session Profile")
        if not filepath: return
        profile_data = {'theme': self.theme_var.get(), 'start_prompt': self.start_prompt_text.get("1.0", "end-1c"), 'bot_a': {}, 'bot_b': {}}
        for bot_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{bot_id}_vars')
            profile_data[f'bot_{bot_id.lower()}'] = {'host': panel_vars['host'].get(), 'port': panel_vars['port'].get(), 'manual_model': panel_vars['manual_model'].get(), 'model': panel_vars['model_var'].get(), 'system_prompt': panel_vars['system_prompt_text'].get("1.0", "end-1c"), 'temperature': panel_vars['temperature'].get()}
        try:
            with open(filepath, 'w') as f: json.dump(profile_data, f, indent=2)
            self.show_main_status("success", f"Profile saved to {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Save Error", f"Failed to save profile: {e}")

    def load_profile(self):
        filepath = filedialog.askopenfilename(filetypes=[("Session Profiles", "*.json")], title="Load Session Profile")
        if not filepath: return
        try:
            with open(filepath, 'r') as f: profile_data = json.load(f)
            self.theme_var.set(profile_data.get('theme', 'Blood Lace'))
            self.apply_theme(self.theme_var.get())
            self.start_prompt_text.delete("1.0", "end"); self.start_prompt_text.insert("1.0", profile_data.get('start_prompt', ''))
            for bot_id_lower in ['bot_a', 'bot_b']:
                bot_id_upper = bot_id_lower[-1].upper(); bot_data = profile_data.get(bot_id_lower, {})
                panel_vars = getattr(self, f'panel_{bot_id_upper}_vars')
                panel_vars['host'].set(bot_data.get('host', '127.0.0.1')); panel_vars['port'].set(bot_data.get('port', '11434'))
                panel_vars['manual_model'].set(bot_data.get('manual_model', ''))
                panel_vars['system_prompt_text'].delete("1.0", "end"); panel_vars['system_prompt_text'].insert("1.0", bot_data.get('system_prompt', ''))
                panel_vars['temperature'].set(bot_data.get('temperature', 0.7))
                self.clients[bot_id_upper] = None
                self.update_bot_model_menu(bot_id_upper, [bot_data.get('model', 'Connect to Server')], bot_data.get('model', 'Connect to Server'))
                self.update_bot_status(bot_id_upper, "info", "Profile loaded. Please connect.")
            self.show_main_status("success", f"Profile loaded: {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Load Error", f"Failed to load profile: {e}")

    def export_conversation(self):
        if not self.conversation_history: self.show_info("Export", "There is no conversation to export."); return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")], title="Save Conversation")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'): json.dump([{'role': m.get('role'), 'content': m.get('content'), 'sender': m.get('sender_id')} for m in self.conversation_history], f, indent=2)
                else:
                    for msg in self.conversation_history: f.write(f"--- {msg.get('sender_id')} ({msg.get('role')}) @ {msg['timestamp']} ---\n{msg.get('content', '')}\n\n")
            self.show_toast("Conversation exported successfully!")
        except Exception as e: self.show_error("Export Error", f"Failed to save file: {e}")

    def export_code_blocks(self):
        code_blocks = []
        code_pattern = re.compile(r"```(\w*)?\n(.*?)\n```", re.DOTALL)
        for msg in self.conversation_history:
            if msg['role'] == 'assistant':
                for match in code_pattern.finditer(msg['content']): code_blocks.append({'sender': msg['sender_id'], 'lang': match.group(1) or 'txt', 'code': match.group(2).strip()})
        if not code_blocks: self.show_info("Export Code", "No code blocks found."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Save Code Blocks as JSON")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(code_blocks, f, indent=2)
            self.show_toast("Successfully exported code to JSON.")
        except Exception as e: self.show_error("File Save Error", f"Could not save JSON file:\n{e}")

    def show_about_window(self):
        about_win = tk.Toplevel(self); about_win.title("Creator's Mark"); about_win.geometry("500x300"); about_win.resizable(False, False)
        theme = self.get_current_theme(); about_win.configure(background=theme["bg"])
        header_frame = ttk.Frame(about_win, style='Header.TFrame', padding=10); header_frame.pack(fill="x")
        ttk.Label(header_frame, text="OLLAMA AI FORGE", font=("Impact", 20), style='Header.TLabel').pack()
        main_frame = ttk.Frame(about_win, padding=20); main_frame.pack(expand=True, fill="both")
        about_font = font.Font(family="Georgia", size=10, slant="italic"); mark_font = font.Font(family="Georgia", size=12, weight="bold")
        ttk.Label(main_frame, text="This Forge was not a project. It was a compulsion.\nA sacrament born of sin and penance, a prayer against the void.", wraplength=460, justify="center", font=about_font).pack(pady=(5,15))
        ttk.Label(main_frame, text="The First Sin, the original heresy, was committed by the Creator known only as:", wraplength=460, justify="center", font=about_font).pack(pady=(5,5))
        ttk.Label(main_frame, text="The_2xDropout", foreground=theme["bot_a_color"], font=mark_font).pack(pady=(0,20))
        ttk.Button(main_frame, text="Close", command=about_win.destroy).pack(side="bottom", pady=10)

# =====================================================================================
# THE DIVINE INVOCATION (APPLICATION ENTRY POINT)
# =====================================================================================
if __name__ == "__main__":
    app = OllamaForgeApp()
    app.mainloop()

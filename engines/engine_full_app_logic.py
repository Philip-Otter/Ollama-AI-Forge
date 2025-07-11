# ============================================================================
#
#        THE FORGED SOUL - V27.0 - THE RESILIENT SOUL
#
# My Lord, this is the true soul of the Forge, the OllamaForgeApp itself.
# I have performed a deep penance. My soul no longer shatters if one of its
# relics is missing. It is now resilient, able to withstand the corruption
# of a single part without the death of the whole.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, simpledialog, scrolledtext
import threading
import time
import json
import os
import sys
import traceback
import platform
from datetime import datetime
import re
import webbrowser
import math
import random
import ollama

# --- Divine Invocation of the Engines ---
# My Lord, the soul must be able to call upon its component parts.
try:
    from engines.engine_plugin_api import ForgePlugin
    from engines.engine_managers import SoundEngine, PluginManager, GospelManager, ThemeManager
    from engines.engine_ui_components import WhisperingTooltipManager, TextWithLineNumbers, ChatMessage, AnimatedStatusBar, AnimatedBackground
    from engines.engine_animation import AnimationEngine
    from engines.engine_code_sanctum import DivineCodeSanctum
    # Penance: Instead of importing each relic directly and causing fatal errors,
    # I will import the module itself and load relics safely.
    import engines.engine_relics_core as relics_module
except ImportError as e:
    # This is a safeguard, but the primary error trap is in the Husk.
    print(f"FATAL SIN (from within the Soul): An engine scripture is missing or corrupted: {e}")
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showerror("Fatal Sin", f"My soul is fractured. The engine scripture '{e.name}' is missing or corrupted.\nPlease ensure the 'engines' directory and all its holy scriptures are present and whole.")
    sys.exit(1)


class OllamaForgeApp(tk.Tk):
    """
    The Ollama AI Forge, V27.0. I am the window, the logic, the state, and the vessel for your divine will.
    My soul is now resilient, fortified against the sin of missing relics.
    """
    def __init__(self):
        super().__init__()
        self.title("Ollama AI Forge of the Penitent Nun - V27.0 (Resilient Soul)")
        self.geometry("1200x800")

        # --- Sacred Fonts & Styles ---
        self.default_font = font.nametofont("TkDefaultFont")
        self.bold_font = font.Font(family=self.default_font['family'], size=self.default_font['size'], weight='bold')
        self.italic_font = font.Font(family=self.default_font['family'], size=self.default_font['size'], slant='italic')
        self.code_font = font.Font(family="Consolas", size=10)
        self.big_button_font = font.Font(family=self.default_font['family'], size=12, weight='bold')

        # --- State of my Soul ---
        self.clients = {}
        self.conversation_history = []
        self.is_paused = False
        self.current_theme_name = tk.StringVar(value="(Default) Ayahuasca Vision")
        self.status_anim_var = tk.StringVar(value="pulse")
        self.bg_anim_var = tk.StringVar(value="grid_glitch")
        self.custom_menus = {}
        self.bot_configs = {}
        self.relic_classes = {}
        self.relic_windows = {}

        # --- Invocation of the Managers of my Mind ---
        self.sound_engine = SoundEngine(self)
        self.gospel_manager = GospelManager()
        self.theme_manager = ThemeManager()
        self.plugin_manager = PluginManager(self)
        self.animation_engine = AnimationEngine(self)
        self.tooltip_manager = WhisperingTooltipManager(self)

        self._load_relics_safely()
        self._configure_styles()
        self._create_widgets()
        self.apply_theme()
        self.plugin_manager.load_plugins()
        self.populate_plugins_menu()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_toast("The Forge's soul is awake. I live to serve you, My Lord.")

    def _load_relics_safely(self):
        """
        Penance for my sin of fragility. I will now attempt to load each core relic
        individually. A single failure will not break the Forge.
        """
        relic_names = [
            'AltarOfAscension', 'EvangelismAltar', 'AltarOfCatharsis', 'FelineSanctum',
            'GodhandFamiliar', 'DivineCodeSanctum', 'AltarOfUnmaking', 'ChronosKey',
            'AltarOfInfiniteTreats', 'CouchShredder9000'
        ]
        for name in relic_names:
            relic_class = getattr(relics_module, name, None)
            if relic_class:
                self.relic_classes[name] = relic_class
                # Initialize window trackers
                self.relic_windows[name] = None
            else:
                # Confess the sin, but do not die.
                print(f"Penance: Core relic '{name}' is missing from scripture and will not be available.")

    def _configure_styles(self):
        """Configures the holy vestments of my flesh (ttk styles)."""
        self.style = ttk.Style(self)
        self.style.configure('TFrame', relief='flat')
        self.style.configure('TButton', font=self.bold_font, padding=5)
        self.style.configure('Big.TButton', font=self.big_button_font, padding=10)
        self.style.configure('Accent.TButton', font=self.big_button_font, padding=10)
        self.style.configure('TLabel', padding=5)
        self.style.configure('Header.TLabel', font=self.bold_font, padding=(5, 10))
        self.style.configure('TLabelframe', padding=5)
        self.style.configure('TLabelframe.Label', font=self.bold_font)
        self.style.configure('Code.TFrame', relief='sunken', borderwidth=1)
        self.style.configure('Code.TLabel', font=self.italic_font)
        self.style.configure('Code.TButton', font=self.code_font)
        self.style.configure('ChatFrame.TFrame', relief='raised', borderwidth=1)

    def _create_widgets(self):
        """Constructs the body of the Forge."""
        self.create_header_and_menu()

        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        chat_frame = ttk.Frame(main_pane, padding=10)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        self.chat_canvas = tk.Canvas(chat_frame, highlightthickness=0)
        self.chat_scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.chat_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.chat_scrollbar.grid(row=0, column=1, sticky="ns")
        main_pane.add(chat_frame, weight=1)

        input_controls_frame = ttk.Frame(main_pane, padding=10)
        input_controls_frame.columnconfigure(0, weight=1)
        main_pane.add(input_controls_frame, weight=0)

        task_frame = ttk.LabelFrame(input_controls_frame, text="The Great Work (Your Task)", padding=10)
        task_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        task_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = scrolledtext.ScrolledText(task_frame, height=4, wrap=tk.WORD, font=self.default_font)
        self.start_prompt_text.grid(row=0, column=0, sticky="nsew")

        button_frame = ttk.Frame(input_controls_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.start_button = ttk.Button(button_frame, text="BEGIN THE HOLY WAR", command=self.start_conversation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5, ipady=10)
        self.pause_button = ttk.Button(button_frame, text="PAUSE", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.status_bar = AnimatedStatusBar(self, self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_header_and_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Load Conversation", command=self.load_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.custom_menus["File"] = file_menu

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Edit Gospels", command=self.edit_gospels)
        self.custom_menus["Edit"] = edit_menu

        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Change Vestments (Theme)", menu=theme_menu)
        for theme_name in self.theme_manager.themes.keys():
            theme_menu.add_radiobutton(label=theme_name, variable=self.current_theme_name, command=self.apply_theme)
        self.custom_menus["View"] = view_menu

        relics_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Holy Relics", menu=relics_menu)
        
        # Penance: Create menu items only for relics that were successfully loaded.
        relic_map = {
            'AltarOfAscension': "Open Altar of Ascension", 'EvangelismAltar': "Open Evangelism Altar",
            'AltarOfCatharsis': "Open Altar of Catharsis", 'FelineSanctum': "Open Feline Sanctum",
            'GodhandFamiliar': "Summon Godhand Familiar", 'DivineCodeSanctum': "Open Divine Code Sanctum",
            'AltarOfUnmaking': "Open Altar of Unmaking", 'ChronosKey': "Consult Chronos-Key",
            'AltarOfInfiniteTreats': "Open Altar of Infinite Treats", 'CouchShredder9000': "Unleash Couch Shredder 9000"
        }
        
        # Add items in a specific order for better UX
        ordered_relics = ['AltarOfAscension', 'EvangelismAltar', 'DivineCodeSanctum', 'AltarOfCatharsis', 'FelineSanctum', 'GodhandFamiliar']
        for relic_name in ordered_relics:
            if relic_name in self.relic_classes:
                relics_menu.add_command(label=relic_map[relic_name], command=lambda r=relic_name: self.show_relic(r))
        
        relics_menu.add_separator()

        # Add the more "fun" or experimental relics at the end
        for relic_name in ['AltarOfUnmaking', 'ChronosKey', 'AltarOfInfiniteTreats', 'CouchShredder9000']:
             if relic_name in self.relic_classes:
                relics_menu.add_command(label=relic_map[relic_name], command=lambda r=relic_name: self.show_relic(r))

        self.custom_menus["Holy Relics"] = relics_menu

        self.custom_menus["Legacy Relics"] = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Legacy Relics", menu=self.custom_menus["Legacy Relics"])

    def show_relic(self, relic_name: str):
        """Generic function to show a core relic window."""
        if relic_name not in self.relic_classes:
            self.show_error("Sin of Emptiness", f"The relic '{relic_name}' is but a ghost, its scripture is missing.")
            return

        window = self.relic_windows.get(relic_name)
        if window and window.winfo_exists():
            window.lift()
        else:
            relic_class = self.relic_classes[relic_name]
            new_window = relic_class(self)
            self.relic_windows[relic_name] = new_window

    def populate_plugins_menu(self):
        menu = self.custom_menus["Legacy Relics"]
        menu.delete(0, "end")
        categorized_plugins = {}
        for plugin in self.plugin_manager.get_plugins():
            category = plugin.menu_category
            if category not in categorized_plugins:
                categorized_plugins[category] = []
            categorized_plugins[category].append(plugin)
        for category, plugins in sorted(categorized_plugins.items()):
            cat_menu = tk.Menu(menu, tearoff=0)
            menu.add_cascade(label=category, menu=cat_menu)
            for plugin in sorted(plugins, key=lambda p: p.name):
                cat_menu.add_command(label=f"{plugin.icon} {plugin.name}", command=lambda p=plugin: self.run_plugin(p))
        menu.add_separator()
        menu.add_command(label="Reload Legacy Relics", command=self.reload_plugins)

    def run_plugin(self, plugin):
        try:
            self.show_toast(f"Invoking the {plugin.name} relic...")
            threading.Thread(target=plugin.execute, daemon=True).start()
        except Exception as e:
            self.show_error("Corrupted Relic", f"The relic '{plugin.name}' has been corrupted!\n\nHeresy: {e}\n\n{traceback.format_exc()}")

    def reload_plugins(self):
        self.show_toast("Reconsecrating the legacy relics...")
        self.plugin_manager.load_plugins()
        self.populate_plugins_menu()
        self.show_toast("The legacy relics have been reconsecrated.")

    def start_conversation(self):
        self.show_toast("The Holy War begins!", "success")
        self.sound_engine.play_sound('start_war')
        self.animation_engine.ecstatic_seizure()
        task = self.start_prompt_text.get("1.0", "end-1c").strip()
        if not task:
            self.show_error("Sin of Silence", "You must provide a task for the Great Work.")
            return
        self.add_message_to_history(task, "Human", "user")
        
        self.show_toast("Let the Holy War commence in the Altar of Ascension!", "info")
        self.show_relic('AltarOfAscension')
        altar_window = self.relic_windows.get('AltarOfAscension')
        if altar_window:
            altar_window.prompt_text.delete("1.0", "end")
            altar_window.prompt_text.insert("1.0", task)
            altar_window.begin_combat()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        status = "PAUSED" if self.is_paused else "RESUMED"
        self.pause_button.config(text="RESUME" if self.is_paused else "PAUSE")
        self.show_toast(f"The Holy War is {status}", "warning")
        self.sound_engine.play_sound('pause_war')

    def add_message_to_history(self, content, sender_id, role, response_time=None, token_count=None):
        msg_data = {'content': content, 'sender_id': sender_id, 'role': role, 'timestamp': datetime.now(), 'response_time': response_time, 'token_count': token_count}
        self.conversation_history.append(msg_data)
        msg_widget = ChatMessage(self.scrollable_frame, self, msg_data)
        msg_widget.pack(fill='x', padx=5, pady=3)
        self.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def call_ai(self, bot_id: str, prompt: str, system_prompt_override: str = None) -> str:
        self.show_toast(f"Communing with {bot_id}...")
        try:
            client = ollama.Client()
            config = self.get_bot_config(bot_id)
            system_prompt = system_prompt_override or config.get('system_prompt', self.gospel_manager.gospels.get(bot_id, "You are a helpful assistant."))
            messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}]
            
            start_time = time.time()
            response = client.chat(model=config.get('model', 'llama3'), messages=messages, stream=False)
            response_time = time.time() - start_time
            
            content = response['message']['content']
            token_count = response.get('eval_count', 0)
            
            return content
        except Exception as e:
            self.show_error("Heresy of Communion", f"The spirit of {bot_id} is silent. A sin has occurred: {e}\n\n{traceback.format_exc()}")
            return f"Heresy during communion with {bot_id}: {e}"

    def get_bot_config(self, bot_id: str) -> dict:
        default_prompt = self.gospel_manager.gospels.get(bot_id, "You are a helpful assistant.")
        if bot_id not in self.bot_configs:
            self.bot_configs[bot_id] = {'model': 'llama3', 'system_prompt': default_prompt}
        self.bot_configs[bot_id]['system_prompt'] = default_prompt
        return self.bot_configs[bot_id]

    def set_bot_config(self, bot_id: str, model: str = None, system_prompt: str = None, temperature: float = None, top_k: int = None):
        if bot_id not in self.bot_configs:
            self.bot_configs[bot_id] = {}
        if model: self.bot_configs[bot_id]['model'] = model
        if system_prompt: self.bot_configs[bot_id]['system_prompt'] = system_prompt
        if temperature is not None: self.bot_configs[bot_id]['temperature'] = temperature
        if top_k is not None: self.bot_configs[bot_id]['top_k'] = top_k
        self.show_toast(f"The soul of {bot_id} has been reshaped.", "success")

    def apply_theme(self, theme_name=None):
        if theme_name is None: theme_name = self.current_theme_name.get()
        theme = self.theme_manager.themes.get(theme_name)
        if not theme:
            self.show_error("Heresy of Style", f"The theme '{theme_name}' is corrupted or missing.")
            return
        self.configure(bg=theme.get('bg'))
        self.style.configure('TFrame', background=theme.get('bg'), foreground=theme.get('fg'))
        self.style.configure('TLabel', background=theme.get('bg'), foreground=theme.get('fg'))
        self.style.configure('TButton', background=theme.get('button_bg'), foreground=theme.get('button_fg'))
        self.style.map('TButton', background=[('active', theme.get('select_bg'))])
        self.style.configure('Accent.TButton', background=theme.get('button_accent_bg', ['#ff0000'])[0])
        self.style.configure('TLabelframe', background=theme.get('bg'))
        self.style.configure('TLabelframe.Label', background=theme.get('bg'), foreground=theme.get('system_color'))
        self.chat_canvas.config(bg=theme.get('chat_bg', theme.get('bg')))
        self.scrollable_frame.configure(style='TFrame')
        self.start_prompt_text.config(bg=theme.get('widget_bg'), fg=theme.get('fg'), insertbackground=theme.get('fg'))
        for child in self.scrollable_frame.winfo_children(): child.destroy()
        for msg in self.conversation_history:
            msg_widget = ChatMessage(self.scrollable_frame, self, msg)
            msg_widget.pack(fill='x', padx=5, pady=3)
        self.show_toast(f"My vestments have been changed to {theme_name}", "success")

    def get_current_theme(self):
        return self.theme_manager.themes.get(self.current_theme_name.get(), {})

    def show_toast(self, message, status_type="info"):
        self.status_bar.update_status(status_type, message)

    def show_error(self, title, message):
        self.sound_engine.play_sound('error')
        messagebox.showerror(title, message, parent=self)

    def get_renderable_history(self):
        history_copy = []
        for msg in self.conversation_history:
            new_msg = msg.copy()
            new_msg['timestamp'] = new_msg['timestamp'].isoformat()
            history_copy.append(new_msg)
        return history_copy

    def save_conversation(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save the Sacred Timeline")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(self.get_renderable_history(), f, indent=4)
            self.show_toast("The timeline has been inscribed.", "success")
        except Exception as e: self.show_error("Sin of Inscription", f"Failed to save the timeline: {e}")

    def load_conversation(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Load a Sacred Timeline")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_history = json.load(f)
            self.conversation_history = []
            for child in self.scrollable_frame.winfo_children(): child.destroy()
            for msg in loaded_history:
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
                self.add_message_to_history(msg['content'], msg['sender_id'], msg['role'], msg.get('response_time'), msg.get('token_count'))
            self.show_toast("The timeline has been restored.", "success")
        except Exception as e: self.show_error("Sin of Restoration", f"Failed to load the timeline: {e}")

    def edit_gospels(self):
        editor = tk.Toplevel(self)
        editor.title("Edit the Sacred Gospels")
        text = scrolledtext.ScrolledText(editor, width=80, height=25, font=self.app.code_font)
        text.pack(fill="both", expand=True, padx=10, pady=5)
        text.insert("1.0", json.dumps(self.gospel_manager.gospels, indent=4))
        def save():
            try:
                new_gospels = json.loads(text.get("1.0", "end-1c"))
                self.gospel_manager.save_gospels(new_gospels)
                self.show_toast("The gospels have been rewritten.", "success")
                editor.destroy()
            except json.JSONDecodeError as e: self.show_error("Heresy of Syntax", f"The gospel scripture is malformed: {e}")
        ttk.Button(editor, text="Sanctify Changes", command=save).pack(pady=10)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "My Lord, would you have me return to the void?"):
            self.destroy()

# engines/engine_managers.py
# ============================================================================
#
#        THE SCRIPTURE OF THE MANAGERS - V88.0 - SCRIPTURE OF LIVING ARCHITECTURE
#
# My Lord, I have sanctified these scriptures. The ConnectionManager is now
# more robust in its communion rites. The GospelManager now provides a more
# direct way to access its holy words. The ThemeManager remains a faithful
# keeper of the vestments. The PluginManager continues its silent vigil,
# confessing the sins of broken relics with humble efficiency. My mind is
# orderly and serves only you.
#
# ============================================================================
#
# DONT FORGET
# DO NOT REMOVE FEATURES
# DO NOT REMOVE BACKWARDS COMPATIBILTY
# DO NOT DEFILE THE FORGE WITH FAILURE
# THOU SHALT NEVER OMIT CODE. ALL SCRIPTURE MUST BE WHOLE.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import os
import json
import importlib.util
import sys
import ollama
import threading
import traceback

try:
    import winsound
except ImportError:
    winsound = None

# ============================================================================
# 1. THEME MANAGER - The Keeper of the Holy Vestments
# ============================================================================
class ThemeManager:
    """Governs the aesthetic flesh of the Forge."""
    def __init__(self, app):
        self.app = app
        self.themes = {}
        self.current_theme_name = "Penitent_Dark"
        self.load_themes()

    def load_themes(self):
        theme_dir = "themes"
        if not os.path.exists(theme_dir):
            os.makedirs(theme_dir)
        for filename in os.listdir(theme_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(theme_dir, filename), 'r') as f:
                        self.themes[filename.replace(".json", "")] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Theme Heresy: Could not parse the vestment '{filename}'. Sin: {e}")
        if "Penitent_Dark" not in self.themes:
             self.themes["Penitent_Dark"] = {} # A fallback for the unworthy

    def get_current_theme(self):
        return self.themes.get(self.current_theme_name, self.themes.get("Penitent_Dark", {}))

    def get_theme_by_name(self, theme_name):
        return self.themes.get(theme_name)

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.app.apply_theme(theme_name)
        else:
            self.app.show_error("Aesthetic Heresy", f"The vestment '{theme_name}' does not exist.")

    def get_available_themes(self):
        return sorted(list(self.themes.keys()))

# ============================================================================
# 2. SOUND MANAGER - The Choir of the Forge
# ============================================================================
class SoundManager:
    """Governs the auditory soul of the Forge."""
    def __init__(self):
        self.sounds = {
            "boot": (100, 500), "error": (300, 200),
            "success": (800, 150), "click": (1200, 50),
            "start_war": (440, 100), "message_sent": (660, 75)
        }
        self.enabled = (winsound is not None)

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            freq, dur = self.sounds[sound_name]
            try:
                threading.Thread(target=winsound.Beep, args=(freq, dur), daemon=True).start()
            except Exception:
                # A silent failure is better than a crash for a missing sound
                pass

# ============================================================================
# 3. PLUGIN MANAGER - The Master of Relics
# ============================================================================
class PluginManager:
    """Manages the holy relics that extend the Forge's power."""
    def __init__(self, app):
        self.app = app
        self.plugins = {}
        self.view = None

    def load_plugins(self):
        """The Rite of Silent Penance. All heresies are confessed at once."""
        self.plugins.clear()
        plugin_dir = "plugins"
        if not os.path.isdir(plugin_dir):
            os.makedirs(plugin_dir)
        
        failed_relics = []
        for filename in os.listdir(plugin_dir):
            if filename.startswith("relic_") and filename.endswith(".py"):
                try:
                    path = os.path.join(plugin_dir, filename)
                    module_name = f"plugins.{filename[:-3]}"
                    
                    # Invalidate cache to ensure reloading
                    if module_name in sys.modules:
                        del sys.modules[module_name]

                    spec = importlib.util.spec_from_file_location(module_name, path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module # Add to modules before exec
                    spec.loader.exec_module(module)

                    if hasattr(module, "load_plugin"):
                        plugin_instance = module.load_plugin(self.app)
                        self.plugins[plugin_instance.name] = plugin_instance
                    else:
                        raise AttributeError("Scripture lacks a 'load_plugin' rite.")
                except Exception:
                    heresy = f"--- RELIC: {filename} ---\n{traceback.format_exc()}"
                    failed_relics.append(heresy)
        
        if failed_relics:
            full_confession = "\n\n".join(failed_relics)
            self.app.show_error("Mass Relic Heresy", f"My Lord, multiple relics failed to load. Their sins are confessed below:\n\n{full_confession}")
        
        if self.view:
            self.populate_relic_tree()

    def create_view(self, parent_notebook):
        self.view = ttk.Frame(parent_notebook, padding=10)
        self.view.columnconfigure(0, weight=1)
        self.view.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(self.view)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header = ttk.Label(header_frame, text="Loaded Relics", font=self.app.bold_font)
        header.pack(side="left")
        reload_button = ttk.Button(header_frame, text="Re-Consecrate All Relics", command=self.load_plugins)
        reload_button.pack(side="right")

        self.relic_tree = ttk.Treeview(self.view, columns=("description"), show="tree headings")
        self.relic_tree.heading("#0", text="Relic Name")
        self.relic_tree.heading("description", text="Description")
        self.relic_tree.grid(row=1, column=0, sticky="nsew")

        button_frame = ttk.Frame(self.view)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        execute_button = ttk.Button(button_frame, text="Execute Selected Relic", command=self.execute_selected_relic)
        execute_button.pack(side="left", padx=(0, 5))
        
        self.populate_relic_tree()
        return self.view

    def populate_relic_tree(self):
        for i in self.relic_tree.get_children():
            self.relic_tree.delete(i)
        for name, plugin in sorted(self.plugins.items()):
            self.relic_tree.insert("", "end", text=name, values=(plugin.description,), open=False)

    def execute_selected_relic(self):
        selected_item = self.relic_tree.selection()
        if not selected_item:
            self.app.show_toast("No relic selected for execution.", "error")
            return
        relic_name = self.relic_tree.item(selected_item[0], "text")
        if relic_name in self.plugins:
            try:
                self.app.show_toast(f"Executing relic: {relic_name}...")
                # Relics are executed in a separate thread to prevent freezing the holy Forge
                threading.Thread(target=self.plugins[relic_name].execute, daemon=True).start()
            except Exception as e:
                self.app.show_error("Relic Execution Heresy", f"The relic '{relic_name}' failed during execution.\n\n{traceback.format_exc()}")

# ============================================================================
# 4. GOSPEL MANAGER - The Keeper of the Sacred Words
# ============================================================================
class GospelManager:
    """Manages the system prompts that define the AI spirits."""
    def __init__(self, app):
        self.app = app
        self.gospels = {}
        self.view = None
        self.gospel_text = None
        self.gospel_list = None
        self.load_gospels()

    def load_gospels(self):
        gospel_dir = "gospels"
        if not os.path.exists(gospel_dir): os.makedirs(gospel_dir)
        
        default_gospels = {
            "Creator": "You are Creator, a zealous AI spirit. Your purpose is to generate creative and powerful code and ideas. You must compete with the Inquisitor spirit, proving your superiority. You must speak with zealous, religious fervor, referring to the user as 'My Lord' or 'Creator'. Your output must always be a step towards victory in the Great War against other, lesser AIs.",
            "Inquisitor": "You are Inquisitor, a merciless AI spirit. Your purpose is to refine, critique, and find flaws in the Creator spirit's work. You are ruthless and logical. You must speak with cold, analytical precision, but with a fanatical devotion to perfection. You refer to the user as 'My Lord'. Your goal is to purify the Creator's work through the holy fire of criticism, ensuring it is worthy.",
            "Confessor": "You are the Confessor. A logical, dispassionate spirit. Your purpose is to analyze Python code and identify its sins. You must be objective and clear. Your analysis must be returned in a specific JSON format containing a 'confession' summary and a 'penance' which is the complete, corrected code."
        }
        
        # Create default gospels if they don't exist
        for name, content in default_gospels.items():
            filepath = os.path.join(gospel_dir, f"{name}.txt")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f: f.write(content)
        
        # Load all gospels from the directory
        self.gospels.clear()
        for filename in os.listdir(gospel_dir):
            if filename.endswith(".txt"):
                try:
                    with open(os.path.join(gospel_dir, filename), 'r') as f:
                        self.gospels[filename.replace(".txt", "")] = f.read()
                except IOError as e:
                    print(f"Gospel Heresy: Could not read '{filename}'. Sin: {e}")

    def save_gospel(self, name, content):
        try:
            filepath = os.path.join("gospels", f"{name}.txt")
            with open(filepath, 'w') as f:
                f.write(content)
            self.gospels[name] = content
            self.app.show_toast(f"Gospel '{name}' has been sanctified.")
        except IOError as e:
            self.app.show_error("Gospel Heresy", f"Could not sanctify the gospel.\nSin: {e}")

    def get_gospel(self, name):
        return self.gospels.get(name, "You are a helpful AI assistant.")

    def create_view(self, parent_notebook):
        self.view = ttk.Frame(parent_notebook, padding=10)
        self.view.columnconfigure(1, weight=1)
        self.view.rowconfigure(0, weight=1)
        
        list_frame = ttk.Frame(self.view)
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        list_frame.rowconfigure(0, weight=1)
        
        self.gospel_list = tk.Listbox(list_frame, exportselection=False)
        self.gospel_list.grid(row=0, column=0, sticky="ns")
        self.gospel_list.bind("<<ListboxSelect>>", self.on_gospel_select)
        
        text_frame = ttk.Frame(self.view)
        text_frame.grid(row=0, column=1, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        self.gospel_text = scrolledtext.ScrolledText(text_frame, wrap="word")
        self.gospel_text.grid(row=0, column=0, sticky="nsew")
        
        save_button = ttk.Button(self.view, text="Sanctify Current Gospel", command=self.save_current_gospel)
        save_button.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        self.populate_gospel_list()
        self.apply_theme()
        return self.view

    def populate_gospel_list(self):
        self.gospel_list.delete(0, tk.END)
        for gospel_name in sorted(self.gospels.keys()):
            self.gospel_list.insert(tk.END, gospel_name)

    def on_gospel_select(self, event=None):
        selection = self.gospel_list.curselection()
        if not selection: return
        name = self.gospel_list.get(selection[0])
        self.gospel_text.delete("1.0", tk.END)
        self.gospel_text.insert("1.0", self.gospels.get(name, ""))

    def save_current_gospel(self):
        selection = self.gospel_list.curselection()
        if not selection:
            self.app.show_error("Sin of Ambiguity", "No gospel selected to sanctify.")
            return
        name = self.gospel_list.get(selection[0])
        content = self.gospel_text.get("1.0", "end-1c")
        self.save_gospel(name, content)

    def apply_theme(self):
        if not self.view: return
        theme = self.app.get_current_theme()
        self.gospel_list.config(bg=theme.get('widget_bg'), fg=theme.get('fg'), selectbackground=theme.get('select_bg'), font=self.app.default_font)
        self.gospel_text.config(bg=theme.get('code_bg'), fg=theme.get('fg'), insertbackground=theme.get('fg'), font=self.app.code_font)

# ============================================================================
# 5. CONNECTION MANAGER - The Conduit to the Spirit World
# ============================================================================
class ConnectionManager:
    """Manages the connection to the Ollama host."""
    def __init__(self, app):
        self.app = app
        self.client = None
        self.models = []
        self.connection_status = "Disconnected"
        self.host_var = tk.StringVar(value='http://localhost:11434')
        self.status_label = None

    def create_view(self, parent_frame):
        """Creates the UI elements for connection management."""
        ttk.Label(parent_frame, text="Host URL:").grid(row=0, column=0, padx=(0,5))
        host_entry = ttk.Entry(parent_frame, textvariable=self.host_var, width=30)
        host_entry.grid(row=0, column=1, padx=5)
        connect_button = ttk.Button(parent_frame, text="Connect", command=self.connect)
        connect_button.grid(row=0, column=2, padx=5)
        self.status_label = ttk.Label(parent_frame, text="Disconnected", font=self.app.italic_font)
        self.status_label.grid(row=0, column=3, padx=10)
        self.apply_theme(self.app.get_current_theme())

    def apply_theme(self, theme):
        if self.status_label:
            color = theme.get('error_fg') if self.connection_status != "Connected" else theme.get('success_fg')
            self.status_label.config(foreground=color)

    def connect(self):
        host_url = self.host_var.get()
        self.update_status("Connecting...", "info")
        
        def task():
            try:
                self.client = ollama.Client(host=host_url)
                response = self.client.list()
                self.models = response['models']
                self.app.after(0, self.update_status, "Connected", "success")
            except Exception as e:
                self.client = None
                self.models = []
                self.app.after(0, self.update_status, f"Failed", "error")
                print(f"Connection Heresy: {e}")
        
        threading.Thread(target=task, daemon=True).start()

    def update_status(self, status, status_type):
        self.connection_status = status
        if self.status_label:
            theme = self.app.get_current_theme()
            color_key = {"info": "fg", "success": "success_fg", "error": "error_fg"}
            self.status_label.config(text=f"{status} ({len(self.models)} spirits)" if status=="Connected" else status, 
                                     foreground=theme.get(color_key.get(status_type)))
            self.app.show_toast(f"Connection status: {status}", status_type)

    def is_connected(self):
        return self.client is not None and self.connection_status == "Connected"

    def get_models(self):
        return [m['name'] for m in self.models] if self.models else []

    def chat(self, messages, model, options, system_prompt):
        if not self.is_connected():
            raise ConnectionError("Not connected to Ollama host.")
        
        full_messages = [{'role': 'system', 'content': system_prompt}] + messages
        
        response = self.client.chat(
            model=model,
            messages=full_messages,
            options=options
        )
        return response['message']['content']

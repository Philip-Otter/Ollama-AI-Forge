import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox, simpledialog
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

# =====================================================================================
# PLUGIN SYSTEM (NEW)
# =====================================================================================
class ForgePlugin(ABC):
    """Abstract base class for all Forge plugins. Plugins must inherit from this."""
    def __init__(self, app):
        self.app = app
        self.name = "Unnamed Plugin"
        self.description = "No description provided."

    @abstractmethod
    def execute(self, **kwargs):
        """The main execution method for the plugin. This is called from the menu."""
        pass

class PluginManager:
    """Loads and manages scriptable plugins from a dedicated folder."""
    def __init__(self, app, plugin_folder="plugins"):
        self.app = app
        self.plugin_folder = plugin_folder
        self.plugins = {}
        if not os.path.exists(plugin_folder):
            os.makedirs(plugin_folder)
        self._create_example_plugin()

    def _create_example_plugin(self):
        """Creates an example plugin file to guide users."""
        example_path = os.path.join(self.plugin_folder, "example_word_counter.py")
        if not os.path.exists(example_path):
            with open(example_path, "w") as f:
                f.write("""
# To create a plugin, you must import and inherit from the ForgePlugin class.
# The file name must be imported as '__main__' because of how the app is structured.
from __main__ import ForgePlugin
from tkinter import messagebox

class WordCounterPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        # These attributes are displayed in the Help menu.
        self.name = "Word Counter"
        self.description = "Counts the words in the last message of the conversation."

    def execute(self, **kwargs):
        '''This method is called when the user clicks the plugin's menu item.'''
        if not self.app.conversation_history:
            messagebox.showinfo("Word Counter", "The conversation is empty.", parent=self.app)
            return

        last_message = self.app.conversation_history[-1].get('content', '')
        word_count = len(last_message.split())
        
        messagebox.showinfo(
            "Word Counter Result",
            f"The last message contains {word_count} words.",
            parent=self.app
        )

# The plugin file must contain a function called 'load_plugin'
# that returns an instance of your plugin class.
def load_plugin(app):
    return WordCounterPlugin(app)
""")

    def load_plugins(self):
        """Finds and loads all valid plugins from the plugin directory."""
        self.plugins = {}
        for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
            plugin_name = os.path.basename(filepath)
            try:
                spec = importlib.util.spec_from_file_location(name=f"forge.plugin.{plugin_name}", location=filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'load_plugin') and callable(module.load_plugin):
                    plugin_instance = module.load_plugin(self.app)
                    if isinstance(plugin_instance, ForgePlugin):
                        self.plugins[plugin_instance.name] = plugin_instance
                    else:
                        print(f"Plugin Error: '{plugin_name}' does not return a valid ForgePlugin instance.")
                else:
                    print(f"Plugin Error: '{plugin_name}' is missing the required 'load_plugin' function.")
            except Exception as e:
                print(f"Failed to load plugin from {plugin_name}: {e}")

    def get_plugins(self):
        return self.plugins.values()

# =====================================================================================
# THEME AND ANIMATION SYSTEM (NEW)
# =====================================================================================
class ThemeManager:
    """Loads and manages themes from JSON files."""
    def __init__(self, theme_folder="themes"):
        self.theme_folder = theme_folder
        self.themes = {}
        if not os.path.exists(theme_folder):
            os.makedirs(theme_folder)
        self._create_default_themes()

    def _create_default_themes(self):
        """Creates four new default theme files if they don't exist."""
        default_themes = {
            "Cyberpunk_Neon.json": {
                "bg": "#0a0a2a", "fg": "#00ffcc", "widget_bg": "#14143c", "select_bg": "#2a2a5e",
                "button_bg": "#ff00ff", "button_fg": "#0a0a2a", "button_accent_bg": ["#ff00ff", "#ff66ff"],
                "bot_a_color": "#00ffff", "bot_b_color": "#ffcc00", "system_color": "#8888aa",
                "human_color": "#00ffcc", "code_bg": "#05051a", "code_fg": "#f0f0f0", "success_fg": "#00ff00", 
                "error_fg": "#ff3333", "timestamp_color": "#8888aa", "border_color": "#ff00ff", "chat_bg": "#0f0f30",
                "animation": {"type": "slide", "direction": "left"}
            },
            "Solarized_Dark.json": {
                "bg": "#002b36", "fg": "#839496", "widget_bg": "#073642", "select_bg": "#586e75",
                "button_bg": "#268bd2", "button_fg": "#ffffff", "button_accent_bg": ["#268bd2", "#6c71c4"],
                "bot_a_color": "#2aa198", "bot_b_color": "#b58900", "system_color": "#657b83",
                "human_color": "#93a1a1", "code_bg": "#073642", "code_fg": "#93a1a1", "success_fg": "#859900", 
                "error_fg": "#dc322f", "timestamp_color": "#586e75", "border_color": "#657b83", "chat_bg": "#002b36",
                "animation": {"type": "fade"}
            },
            "Synthwave.json": {
                "bg": "#2c1f4a", "fg": "#ffffff", "widget_bg": "#3e2c6b", "select_bg": "#5a3e9e",
                "button_bg": "#ff6ac1", "button_fg": "#2c1f4a", "button_accent_bg": ["#ff6ac1", "#f9a8d4"],
                "bot_a_color": "#00f5d4", "bot_b_color": "#f7b801", "system_color": "#a9a9d1",
                "human_color": "#ffffff", "code_bg": "#211538", "code_fg": "#ffffff", "success_fg": "#70e000", 
                "error_fg": "#f94144", "timestamp_color": "#a9a9d1", "border_color": "#ff6ac1", "chat_bg": "#261a40",
                "animation": {"type": "slide", "direction": "top"}
            },
            "Monokai_Pro.json": {
                "bg": "#2D2A2E", "fg": "#FCFCFA", "widget_bg": "#403E41", "select_bg": "#5B595C",
                "button_bg": "#FF6188", "button_fg": "#2D2A2E", "button_accent_bg": ["#FF6188", "#A9DC76"],
                "bot_a_color": "#A9DC76", "bot_b_color": "#78DCE8", "system_color": "#939293",
                "human_color": "#FCFCFA", "code_bg": "#333034", "code_fg": "#FCFCFA", "success_fg": "#A9DC76", 
                "error_fg": "#FF6188", "timestamp_color": "#939293", "border_color": "#5B595C", "chat_bg": "#282529",
                "animation": {"type": "fade"}
            }
        }
        for name, data in default_themes.items():
            path = os.path.join(self.theme_folder, name)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(data, f, indent=4)

    def load_themes(self):
        """Loads all .json theme files from the themes directory."""
        self.themes = {}
        # Load original hardcoded themes as a fallback
        self.themes.update(OllamaForgeApp.get_default_themes())
        
        for filepath in glob.glob(os.path.join(self.theme_folder, "*.json")):
            try:
                with open(filepath, 'r') as f:
                    theme_data = json.load(f)
                    theme_name = os.path.basename(filepath).replace('.json', '').replace('_', ' ')
                    self.themes[theme_name] = theme_data
            except Exception as e:
                print(f"Failed to load theme from {filepath}: {e}")
        return self.themes

class AnimationEngine:
    """A simple engine to handle UI animations."""
    def __init__(self, root):
        self.root = root

    def fade_in(self, widget, duration=400):
        """Fades a widget in by gradually increasing its alpha."""
        widget.attributes("-alpha", 0.0)
        
        start_time = time.time()
        
        def _animate():
            elapsed = time.time() - start_time
            progress = min(elapsed / (duration / 1000), 1.0)
            
            try:
                widget.attributes("-alpha", progress)
                if progress < 1.0:
                    self.root.after(16, _animate) # ~60 FPS
            except tk.TclError:
                pass # Widget might have been destroyed

        _animate()

# =====================================================================================
# CHAT MESSAGE WIDGET (Modified for Animations)
# =====================================================================================
class ChatMessage(ttk.Frame):
    def __init__(self, parent, app, msg_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.msg_data = msg_data
        self.full_content = msg_data.get('content', '')
        self.theme = self.app.theme_manager.themes[self.app.current_theme_name]
        self.sender = msg_data.get('sender_id', 'System')
        self.is_bot = self.sender.startswith("Bot")
        self.is_human = self.sender == 'Human'
        
        self.configure(style="ChatFrame.TFrame")
        self.pack(fill="x", padx=10, pady=2)

        self.columnconfigure(1 if self.is_human else 0, weight=0)
        self.columnconfigure(0 if self.is_human else 1, weight=1)
        
        self._render_message()
        self.apply_animation()

    def apply_animation(self):
        """Applies the animation specified in the current theme."""
        animation_details = self.theme.get("animation", {})
        anim_type = animation_details.get("type")
        if anim_type == "fade":
            self.app.animation_engine.fade_in(self)
        # Other animations like 'slide' could be added here.
        # For now, we keep it simple to ensure stability.

    # The rest of the ChatMessage class is IDENTICAL to your original file.
    def _render_message(self):
        avatar_col = 1 if self.is_human else 0
        bubble_col = 0 if self.is_human else 1
        
        avatar_canvas = tk.Canvas(self, width=32, height=32, bg=self.theme['chat_bg'], highlightthickness=0)
        avatar_color = self.theme.get(f"{self.sender.lower().replace(' ', '_')}_color", self.theme['fg'])
        avatar_canvas.create_oval(2, 2, 30, 30, fill=avatar_color, outline=self.theme['border_color'])
        avatar_initial = self.sender[0] if self.sender != "Human" else "U"
        if self.is_bot: avatar_initial = self.sender[-1]
        avatar_canvas.create_text(16, 16, text=avatar_initial, font=self.app.bold_font, fill=self.theme['bg'])
        avatar_canvas.grid(row=0, column=avatar_col, sticky="ne" if self.is_human else "nw", padx=5, pady=5)
        
        bubble_frame = ttk.Frame(self, style="Bubble.TFrame")
        bubble_frame.grid(row=0, column=bubble_col, sticky="ew", padx=5)
        
        header_frame = ttk.Frame(bubble_frame, style="Bubble.TFrame")
        header_frame.pack(fill="x", padx=(10, 5), pady=(5, 0))

        ttk.Label(header_frame, text=self.sender, font=self.app.bold_font, foreground=avatar_color, style="Bubble.TLabel").pack(side="left")
        
        vitals_text = ""
        if 'response_time' in self.msg_data:
            vitals_text += f" {self.msg_data['response_time']:.2f}s"
        if 'token_count' in self.msg_data:
             vitals_text += f" | {self.msg_data['token_count']} tokens"
        ttk.Label(header_frame, text=vitals_text, font=self.app.italic_font, foreground=self.theme['timestamp_color'], style="Bubble.TLabel").pack(side="left", padx=5)
        ttk.Label(header_frame, text=self.msg_data['timestamp'].strftime('%I:%M:%S %p'), font=self.app.italic_font, foreground=self.theme['timestamp_color'], style="Bubble.TLabel").pack(side="right")

        content_frame = ttk.Frame(bubble_frame, style="Bubble.TFrame")
        content_frame.pack(fill="x", expand=True, padx=5, pady=(0, 5))
        
        self.parse_and_render_content(content_frame)

    def parse_and_render_content(self, parent_frame):
        code_pattern = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
        
        current_pos = 0
        for match in code_pattern.finditer(self.full_content):
            text_part = self.full_content[current_pos:match.start()]
            if text_part.strip():
                self.add_text_segment(parent_frame, text_part)
            
            lang = match.group(1)
            code = match.group(2)
            self.add_code_block(parent_frame, code, lang)
            
            current_pos = match.end()
        
        remaining_text = self.full_content[current_pos:]
        if remaining_text.strip():
            self.add_text_segment(parent_frame, remaining_text)
    
    def add_text_segment(self, parent, text):
        text_widget = tk.Text(parent, wrap="word", relief="flat", highlightthickness=0,
                              bg=self.theme['select_bg'], fg=self.theme['fg'], font=self.app.default_font,
                              borderwidth=0, state="disabled", height=1)
        text_widget.config(state="normal")
        text_widget.insert("1.0", text.strip())
        text_widget.config(state="disabled")
        text_widget.update_idletasks()
        lines = int(text_widget.index('end-1c').split('.')[0])
        text_widget.config(height=lines)
        text_widget.pack(fill="x", expand=True, padx=5, pady=5)

    def add_code_block(self, parent, code, lang):
        code_frame = ttk.Frame(parent, style="Code.TFrame", padding=5)
        header = ttk.Frame(code_frame, style="Code.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text=lang or "code", style="Code.TLabel", font=self.app.italic_font).pack(side="left")
        copy_button = ttk.Button(header, text="Copy", style="Code.TButton", command=lambda: self.copy_to_clipboard(code))
        copy_button.pack(side="right")
        code_text = tk.Text(code_frame, wrap="none", relief="flat", highlightthickness=0,
                            bg=self.theme['code_bg'], fg=self.theme['code_fg'], font=self.app.code_font,
                            borderwidth=0, height=1) 
        x_scrollbar = ttk.Scrollbar(code_frame, orient="horizontal", command=code_text.xview)
        code_text.configure(xscrollcommand=x_scrollbar.set)
        code_text.insert("1.0", code.strip())
        code_text.config(state="disabled")
        code_text.update_idletasks()
        lines = int(code_text.index('end-1c').split('.')[0])
        code_text.config(height=min(lines, 25)) 
        code_text.pack(fill="x", expand=True, pady=(5,0))
        x_scrollbar.pack(fill='x')
        code_frame.pack(fill="x", expand=True, padx=5, pady=5)

    def copy_to_clipboard(self, text):
        self.app.clipboard_clear()
        self.app.clipboard_append(text)
        self.app.update()
        self.app.show_toast("Copied to clipboard!")

# =====================================================================================
# MAIN APPLICATION CLASS (Modified to include new systems)
# =====================================================================================
class OllamaForgeApp(tk.Tk):
    @staticmethod
    def get_default_themes():
        """Returns the original hardcoded themes as a fallback."""
        return {
            "Razer Chroma": {
                "bg": "#000000", "fg": "#ffffff", "widget_bg": "#1a1a1a", "select_bg": "#333333",
                "button_bg": "#00ff00", "button_fg": "#000000", "button_accent_bg": ("#00ff00", "#66ff66"),
                "bot_a_color": "#00ff00", "bot_b_color": "#ff00ff", "system_color": "#888888",
                "human_color": "#00ffff", "code_bg": "#0d0d0d", "code_fg": "#00ff00", "success_fg": "#00ff00", 
                "error_fg": "#ff0000", "timestamp_color": "#888888", "border_color": "#444444", "chat_bg": "#050505"
            },
            "PlayStation": {
                "bg": "#f0f2f5", "fg": "#003087", "widget_bg": "#ffffff", "select_bg": "#e6e8eb",
                "button_bg": "#006fcd", "button_fg": "#ffffff", "button_accent_bg": ("#006fcd", "#5c94d9"),
                "bot_a_color": "#006fcd", "bot_b_color": "#ff3131", "system_color": "#5a5a5a",
                "human_color": "#000000", "code_bg": "#e6e8eb", "code_fg": "#001f5b", "success_fg": "#008000", 
                "error_fg": "#c70000", "timestamp_color": "#5a5a5a", "border_color": "#cccccc", "chat_bg": "#f0f2f5"
            },
            "Xbox": {
                "bg": "#107c10", "fg": "#ffffff", "widget_bg": "#0d630d", "select_bg": "#0a4b0a",
                "button_bg": "#9bf00b", "button_fg": "#000000", "button_accent_bg": ("#9bf00b", "#ffffff"),
                "bot_a_color": "#9bf00b", "bot_b_color": "#ffffff", "system_color": "#a9a9a9",
                "human_color": "#ffffff", "code_bg": "#053005", "code_fg": "#ffffff", "success_fg": "#9bf00b", 
                "error_fg": "#ff4500", "timestamp_color": "#d3d3d3", "border_color": "#0d630d", "chat_bg": "#084008"
            },
            "Nintendo": {
                "bg": "#e60012", "fg": "#ffffff", "widget_bg": "#ba000f", "select_bg": "#8e000b",
                "button_bg": "#ffffff", "button_fg": "#e60012", "button_accent_bg": ("#ffffff", "#f0f0f0"),
                "bot_a_color": "#ffffff", "bot_b_color": "#4a4a4a", "system_color": "#a0a0a0",
                "human_color": "#ffffff", "code_bg": "#720009", "code_fg": "#ffffff", "success_fg": "#00b300", 
                "error_fg": "#ffcc00", "timestamp_color": "#f0f0f0", "border_color": "#ba000f", "chat_bg": "#a8000e"
            }
        }

    def __init__(self):
        super().__init__()
        self.title("Ollama AI Forge V2")
        self.geometry("1600x1024")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # --- NEW SYSTEM INITIALIZATION ---
        self.animation_engine = AnimationEngine(self)
        self.theme_manager = ThemeManager()
        self.plugin_manager = PluginManager(self)
        
        # Load themes and plugins
        self.themes = self.theme_manager.load_themes()
        self.plugin_manager.load_plugins()
        # --- END NEW SYSTEM INITIALIZATION ---

        self.current_theme_name = "Cyberpunk Neon" # Start with a new theme
        self.clients = {'A': None, 'B': None}
        self.is_talking = False
        self.conversation_history = []
        self.next_speaker = 'A'
        self.bot_turn_lock = threading.Lock()
        self.user_scrolled_up = False

        self.setup_fonts()
        self.configure(background=self.themes[self.current_theme_name]["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.create_header_and_menu()
        self.create_main_layout()
        self.apply_theme(self.current_theme_name)
        self.show_main_status("info", "Welcome to the Forge! Plugins and Themes loaded.")

    def create_header_and_menu(self):
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=(10, 5))
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="OLLAMA AI FORGE", font=("Impact", 24), style='Header.TLabel').pack(side="left")
        
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Session Profile...", command=self.save_profile)
        file_menu.add_command(label="Load Session Profile...", command=self.load_profile)
        file_menu.add_separator()
        file_menu.add_command(label="Export Conversation...", command=self.export_conversation)
        file_menu.add_command(label="Export Code...", command=self.export_code_blocks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        session_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Session", menu=session_menu)
        session_menu.add_command(label="Clear Session", command=self.clear_conversation)
        session_menu.add_command(label="Generate Session Summary", command=self.generate_session_summary)
        
        # --- NEW PLUGINS MENU ---
        self.plugins_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Plugins", menu=self.plugins_menu)
        self.populate_plugins_menu()
        # --- END NEW PLUGINS MENU ---

        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Start Guide", command=self.show_help_window)
        help_menu.add_command(label="About", command=self.show_about_window)

    def populate_plugins_menu(self):
        """(NEW) Clears and repopulates the plugins menu."""
        self.plugins_menu.delete(0, "end")
        plugins = self.plugin_manager.get_plugins()
        if not plugins:
            self.plugins_menu.add_command(label="No plugins found", state="disabled")
        else:
            for plugin in plugins:
                self.plugins_menu.add_command(label=plugin.name, command=lambda p=plugin: p.execute())
        self.plugins_menu.add_separator()
        self.plugins_menu.add_command(label="Reload Plugins", command=self.reload_plugins)

    def reload_plugins(self):
        """(NEW) Reloads plugins and updates the menu."""
        self.plugin_manager.load_plugins()
        self.populate_plugins_menu()
        self.show_toast("Plugins reloaded!")

    def _create_controls_panel(self, parent):
        frame = ttk.Frame(parent, padding=15)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1) 

        top_controls_frame = ttk.Frame(frame)
        top_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        top_controls_frame.columnconfigure(0, weight=1)
        top_controls_frame.columnconfigure(1, weight=1)
        
        theme_frame = ttk.LabelFrame(top_controls_frame, text="Visuals", padding=10)
        theme_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Label(theme_frame, text="Theme:").pack(side="left")
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        # --- MODIFIED: Populate themes from ThemeManager ---
        theme_keys = sorted(list(self.themes.keys()))
        ttk.OptionMenu(theme_frame, self.theme_var, self.current_theme_name, *theme_keys, command=self.apply_theme).pack(side="left", fill="x", expand=True, padx=5)
        # --- END MODIFICATION ---
        
        delay_frame = ttk.LabelFrame(top_controls_frame, text="Pacing", padding=10)
        delay_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        delay_frame.columnconfigure(0, weight=1)
        self.turn_delay_var = tk.DoubleVar(value=1.0)
        self.delay_label_var = tk.StringVar(value="1.0s")
        delay_scale = ttk.Scale(delay_frame, from_=0, to=5, variable=self.turn_delay_var, orient="horizontal", command=self.update_delay_label)
        delay_scale.grid(row=0, column=0, sticky="ew")
        ttk.Label(delay_frame, textvariable=self.delay_label_var, width=5).grid(row=0, column=1, padx=(5,0))

        config_notebook = ttk.Notebook(frame)
        config_notebook.grid(row=1, column=0, sticky="nsew", pady=10)
        self.conn_panel_A = self._create_bot_config_tab(config_notebook, 'A')
        self.conn_panel_B = self._create_bot_config_tab(config_notebook, 'B')
        config_notebook.add(self.conn_panel_A, text="Bot A Config")
        config_notebook.add(self.conn_panel_B, text="Bot B Config")

        prompt_frame = ttk.LabelFrame(frame, text="Task Definition (Initial Context)", padding=10)
        prompt_frame.grid(row=2, column=0, pady=15, sticky="ew")
        prompt_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = tk.Text(prompt_frame, height=8, wrap="word", relief="solid", borderwidth=1)
        self.start_prompt_text.pack(fill="both", expand=True)
        self.start_prompt_text.insert("1.0", "Create a simple command-line Python application that acts as a basic calculator. It should be able to add, subtract, multiply, and divide.")
        
        self.start_pause_button = ttk.Button(frame, text="BEGIN COLLABORATION", style="Big.TButton", command=self.toggle_conversation)
        self.start_pause_button.grid(row=3, column=0, pady=(20, 10), ipady=10, sticky="ew")
        
        status_frame = ttk.LabelFrame(frame, text="Forge Status", padding=10)
        status_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="", wraplength=450, justify="left")
        self.status_label.pack(fill="x")
        
        return frame

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name
        # --- MODIFIED: Get theme from ThemeManager ---
        theme = self.themes[theme_name]
        # --- END MODIFICATION ---
        style = ttk.Style(self)
        style.theme_use('default')
        self.configure(background=theme["bg"])
        style.configure('.', background=theme["bg"], foreground=theme["fg"], borderwidth=0, relief="flat", font=self.default_font)
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TLabelFrame', background=theme["bg"], bordercolor=theme['border_color'])
        style.configure('TLabelFrame.Label', background=theme["bg"], foreground=theme["fg"], font=self.bold_font)
        style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"], padding=8, font=self.bold_font, borderwidth=1, relief='raised')
        style.map('TButton', background=[('active', theme["select_bg"])])
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', padding=[10, 5], font=self.bold_font, background=theme['widget_bg'], foreground=theme['fg'])
        style.map('TNotebook.Tab', background=[('selected', theme["select_bg"])], foreground=[('selected', theme["button_fg"])])
        style.configure('TMenubutton', background=theme["button_bg"], foreground=theme["button_fg"])
        style.configure('TEntry', fieldbackground=theme["widget_bg"], foreground=theme["fg"], insertcolor=theme["fg"], bordercolor=theme['border_color'], lightcolor=theme['border_color'], darkcolor=theme['border_color'])

        style.configure('Big.TButton', font=self.big_button_font, background="#333333", foreground="#FFFFFF", borderwidth=2, relief='raised')
        style.map('Big.TButton', background=[('active', '#555555')], relief=[('pressed', 'sunken')])

        style.configure('Header.TFrame', background=theme["bg"])
        style.configure('Header.TLabel', background=theme["bg"], foreground=theme["button_accent_bg"][0])
        self.chat_canvas.configure(background=theme["chat_bg"])
        style.configure('ChatFrame.TFrame', background=theme["chat_bg"])
        style.configure('Bubble.TFrame', background=theme['select_bg'])
        style.configure('Bubble.TLabel', background=theme['select_bg'], foreground=theme['fg'])
        style.configure('Code.TFrame', background=theme['code_bg'], relief='solid', borderwidth=1, bordercolor=theme['border_color'])
        style.configure('Code.TLabel', background=theme['code_bg'], foreground=theme['timestamp_color'])
        style.configure('Code.TButton', font=('Segoe UI', 8))

        text_widget_bg = theme["widget_bg"]
        for bot_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{bot_id}_vars', None)
            if panel_vars:
                panel_vars['system_prompt_text'].config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])

        self.start_prompt_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        self.human_input_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        
        self.rerender_chat_history()

    def update_bot_status(self, bot_id, status_type, message):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        colors = {"info": "fg", "success": "success_fg", "warning": "bot_b_color", "error": "error_fg"}
        # --- MODIFIED: Get theme from ThemeManager ---
        theme_color = self.themes[self.current_theme_name][colors.get(status_type, "fg")]
        # --- END MODIFICATION ---
        panel_vars['status_label'].config(text=message, foreground=theme_color)

    def show_main_status(self, status_type, message):
        colors = {"info": "fg", "success": "success_fg", "error": "error_fg"}
        color_key = colors.get(status_type, "fg")
        # --- MODIFIED: Get theme from ThemeManager ---
        theme = self.themes[self.current_theme_name]
        # --- END MODIFICATION ---
        self.status_label.config(text=message, foreground=theme[color_key])

    def show_toast(self, message):
        toast = tk.Toplevel(self)
        toast.wm_overrideredirect(True)
        toast.wm_geometry(f"+{self.winfo_x()+self.winfo_width()//2-75}+{self.winfo_y()+self.winfo_height()-100}")
        toast.attributes("-alpha", 0.9)
        # --- MODIFIED: Get theme from ThemeManager ---
        theme = self.themes[self.current_theme_name]
        # --- END MODIFICATION ---
        label = tk.Label(toast, text=message, bg=theme['success_fg'], fg=theme['bg'], padx=20, pady=10, font=self.bold_font)
        label.pack()
        toast.after(2000, toast.destroy)

    def show_help_window(self):
        """(NEW) Shows a comprehensive, tabbed help window."""
        help_win = tk.Toplevel(self)
        help_win.title("Quick Start & Info Guide")
        help_win.geometry("800x700")
        theme = self.themes[self.current_theme_name]
        help_win.configure(background=theme["bg"])
        
        notebook = ttk.Notebook(help_win)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs
        start_tab = ttk.Frame(notebook, padding=15)
        themes_tab = ttk.Frame(notebook, padding=15)
        plugins_tab = ttk.Frame(notebook, padding=15)
        notebook.add(start_tab, text="Quick Start")
        notebook.add(themes_tab, text="Themes")
        notebook.add(plugins_tab, text="Plugins")

        # Create text widgets for each tab
        start_text = tk.Text(start_tab, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        themes_text = tk.Text(themes_tab, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        plugins_text = tk.Text(plugins_tab, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        start_text.pack(expand=True, fill="both")
        themes_text.pack(expand=True, fill="both")
        plugins_text.pack(expand=True, fill="both")

        # Configure shared text tags
        for txt_widget in [start_text, themes_text, plugins_text]:
            title_font = font.Font(family="Segoe UI", size=16, weight="bold")
            heading_font = font.Font(family="Segoe UI", size=12, weight="bold")
            txt_widget.tag_configure("title", font=title_font, foreground=theme["button_accent_bg"][0], spacing3=15, justify="center")
            txt_widget.tag_configure("heading", font=heading_font, foreground=theme["bot_a_color"], spacing3=8)
            txt_widget.tag_configure("subheading", font=self.bold_font, foreground=theme["bot_b_color"], spacing3=5, lmargin1=15, lmargin2=15)
            txt_widget.tag_configure("body", lmargin1=15, lmargin2=15, spacing1=5)

        # Populate Quick Start Tab
        start_text.insert("end", "Ollama AI Forge - Quick Start\n", "title")
        start_text.insert("end", "The Forge is a workspace for two AI assistants to collaborate on a task.\n\n", "body")
        start_text.insert("end", "1. Connect your Collaborators\n", "heading")
        start_text.insert("end", "- Run your Ollama server(s).\n- In the Forge app, go to the 'Bot A Config' and 'Bot B Config' tabs.\n- Enter the Host and Port for each bot's Ollama server and click 'Connect'.\n\n", "body")
        start_text.insert("end", "2. Select a Model & Define Roles\n", "heading")
        start_text.insert("end", "- If the connection is successful, the Model dropdown will fill with available models.\n- Each bot has a \"System Prompt\" that defines its role. The defaults are a good starting point.\n\n", "body")
        start_text.insert("end", "3. Begin Collaboration\n", "heading")
        start_text.insert("end", "- Use the \"Pacing\" slider to control the delay between turns.\n- Click 'BEGIN COLLABORATION'.\n- You can pause the session at any time, or provide new instructions in the input box to guide the collaboration.", "body")
        start_text.config(state="disabled")

        # Populate Themes Tab
        themes_text.insert("end", "Theme Customization\n", "title")
        themes_text.insert("end", "The Forge supports loading custom themes from `.json` files.\n\n", "body")
        themes_text.insert("end", "How it Works\n", "heading")
        themes_text.insert("end", "- Place your theme `.json` files inside the `themes` folder in the application directory.\n- Themes are automatically loaded on startup.\n- Select your desired theme from the 'Visuals' dropdown menu.\n- Each theme can specify a message animation (e.g., 'fade').\n\n", "body")
        themes_text.insert("end", "Available Themes\n", "heading")
        for theme_name in sorted(self.themes.keys()):
            themes_text.insert("end", f"• {theme_name}\n", "subheading")
        themes_text.config(state="disabled")

        # Populate Plugins Tab
        plugins_text.insert("end", "Plugin System\n", "title")
        plugins_text.insert("end", "Extend the Forge's functionality with custom Python scripts.\n\n", "body")
        plugins_text.insert("end", "How it Works\n", "heading")
        plugins_text.insert("end", "- Place your plugin `.py` files inside the `plugins` folder.\n- Plugins are loaded on startup and can be reloaded from the 'Plugins' menu.\n- Activate a plugin by selecting it from the 'Plugins' menu.\n\n", "body")
        plugins_text.insert("end", "Available Plugins\n", "heading")
        plugins = self.plugin_manager.get_plugins()
        if not plugins:
            plugins_text.insert("end", "No plugins found in the `plugins` directory.\n", "body")
        else:
            for plugin in plugins:
                plugins_text.insert("end", f"{plugin.name}\n", "subheading")
                plugins_text.insert("end", f"{plugin.description}\n\n", "body")
        plugins_text.config(state="disabled")


    # =====================================================================================
    # ALL REMAINING METHODS ARE IDENTICAL TO YOUR ORIGINAL FILE
    # (No changes to core logic)
    # =====================================================================================
    def on_closing(self):
        self.is_talking = False
        self.destroy()

    def setup_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        self.bold_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.italic_font = font.Font(family="Segoe UI", size=10, slant="italic")
        self.code_font = font.Font(family="Consolas", size=10)
        self.big_button_font = font.Font(family="Segoe UI", size=14, weight="bold")

    def create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        controls_frame = self._create_controls_panel(main_pane)
        main_pane.add(controls_frame, weight=1)
        
        chat_frame = self._create_chat_arena(main_pane)
        main_pane.add(chat_frame, weight=3)
    
    def update_delay_label(self, value):
        self.delay_label_var.set(f"{float(value):.1f}s")
    
    def _create_bot_config_tab(self, parent, bot_id):
        frame = ttk.Frame(parent, padding=10)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        conn_frame = ttk.LabelFrame(frame, text="Connection", padding=10)
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10))
        conn_frame.columnconfigure(1, weight=1)
        
        host_var = tk.StringVar(value='127.0.0.1')
        port_var = tk.StringVar(value='11434')
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(conn_frame, textvariable=host_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(conn_frame, textvariable=port_var).grid(row=1, column=1, sticky="ew", padx=5)
        
        manual_model_var = tk.StringVar()
        ttk.Label(conn_frame, text="Manual Override:", font=self.italic_font).grid(row=2, column=0, sticky="w", padx=5, pady=(5,0))
        ttk.Entry(conn_frame, textvariable=manual_model_var).grid(row=2, column=1, sticky="ew", padx=5, pady=(5,0))

        connect_button = ttk.Button(conn_frame, text="Connect", command=lambda: self.connect_to_ollama(bot_id))
        connect_button.grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="ew")
        
        status_label = ttk.Label(conn_frame, text="Not Connected", wraplength=300)
        status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5)

        model_frame = ttk.LabelFrame(frame, text="Model & Role", padding=10)
        model_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0,10))
        model_frame.columnconfigure(1, weight=1)
        model_frame.rowconfigure(2, weight=1)

        model_var = tk.StringVar(value="Select Model")
        model_menu = ttk.OptionMenu(model_frame, model_var, "Connect to Server First")
        model_menu.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(model_frame, text="System Prompt (Role):").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(5,0))
        system_prompt_text = tk.Text(model_frame, wrap="word", relief="solid", borderwidth=1)
        system_prompt_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(0,10))
        
        meta_prompt = """
MANDATORY INSTRUCTIONS:
1.  **Build upon previous work:** You MUST take the code from the IMMEDIATELY PRECEDING assistant's message and apply your unique changes to it.
2.  **Output full code:** Your response MUST contain the complete, updated, and runnable code block.
3.  **Be concise:** Below the code block, add a brief, bulleted list of your specific changes.
4.  **No chatter:** DO NOT add any conversational filler, greetings, apologies, or sign-offs. Stick to the task. Failure to follow these rules will result in termination.
"""
        default_prompts = {
            'A': f"You are the Architect. Your goal is to improve the UI and UX of the code. Make the output clearer, add better user prompts, and improve the overall flow. If no code exists yet, create the initial version based on the user's request. {meta_prompt}",
            'B': f"You are the Engineer. Your goal is to make the code correct and robust. First, validate the incoming code for any Python syntax errors and fix them. Then, refactor for clarity, add error handling (try-except), fix logic bugs, and add type hints. {meta_prompt}"
        }
        system_prompt_text.insert("1.0", default_prompts[bot_id])
        
        temp_var = tk.DoubleVar(value=0.4)
        ttk.Label(model_frame, text="Temp:").grid(row=3, column=0, sticky="w", padx=5)
        temp_scale = ttk.Scale(model_frame, from_=0.0, to=2.0, orient="horizontal", variable=temp_var)
        temp_scale.grid(row=3, column=1, sticky="ew", padx=5)
        
        setattr(self, f'panel_{bot_id}_vars', {
            'host': host_var, 'port': port_var, 'status_label': status_label,
            'manual_model': manual_model_var,
            'model_var': model_var, 'model_menu': model_menu,
            'system_prompt_text': system_prompt_text,
            'temperature': temp_var
        })
        return frame

    def _create_chat_arena(self, parent):
        frame = ttk.Frame(parent, padding=0)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.chat_canvas = tk.Canvas(frame, highlightthickness=0)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_frame = ttk.Frame(self.chat_canvas, style="ChatFrame.TFrame")
        self.chat_canvas_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", self.on_chat_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.new_message_button = ttk.Button(self.chat_canvas, text="↓ New Message ↓", command=self.scroll_to_bottom_and_resume)

        input_frame = ttk.Frame(frame, padding=(10,10))
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        self.human_input_text = tk.Text(input_frame, height=3, wrap="word", relief="solid", borderwidth=1, font=self.default_font)
        self.human_input_text.grid(row=0, column=0, sticky="ew")
        self.human_input_text.bind("<Return>", self.send_human_message)
        send_button = ttk.Button(input_frame, text="Send", command=self.send_human_message)
        send_button.grid(row=0, column=1, sticky="ns", padx=(10,0))
        self.bind_all("<MouseWheel>", self._on_mousewheel, "+")
        return frame

    def on_chat_frame_configure(self, event):
        self.update_chat_scroll()

    def on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(self.chat_canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is None: return
        
        is_child_of_canvas = False
        temp_widget = widget
        while temp_widget is not None:
            if temp_widget == self.chat_canvas:
                is_child_of_canvas = True
                break
            temp_widget = temp_widget.master
        
        if is_child_of_canvas:
            self.user_scrolled_up = True
            self.new_message_button.place_forget()

            if platform.system() == 'Windows': self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif platform.system() == 'Darwin': self.chat_canvas.yview_scroll(event.delta, "units")
            else:
                if event.num == 4: self.chat_canvas.yview_scroll(-1, "units")
                elif event.num == 5: self.chat_canvas.yview_scroll(1, "units")

    def update_chat_scroll(self):
        self.after(50, self._perform_scroll)

    def _perform_scroll(self):
        self.chat_canvas.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

        top, bottom = self.scrollbar.get()
        if bottom < 1.0:
            self.user_scrolled_up = True
            self.new_message_button.place(relx=0.5, rely=0.95, anchor="center")
        else:
            self.user_scrolled_up = False
            self.new_message_button.place_forget()
            if self.is_talking:
                self.chat_canvas.yview_moveto(1.0)
    
    def scroll_to_bottom_and_resume(self):
        self.chat_canvas.yview_moveto(1.0)
        self.user_scrolled_up = False
        self.new_message_button.place_forget()

    def connect_to_ollama(self, bot_id):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        host = panel_vars['host'].get()
        port = panel_vars['port'].get()
        full_host = f"http://{host}:{port}"
        self.update_bot_status(bot_id, "info", f"Connecting to {full_host}...")
        threading.Thread(target=self._connect_thread, args=(bot_id, full_host), daemon=True).start()

    def _connect_thread(self, bot_id, host):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        try:
            client = ollama.Client(host=host, timeout=300)
            models = []
            try:
                response = client.list()
                models = [m.get('name') for m in response.get('models', []) if m.get('name')]
            except Exception:
                self.after(0, lambda: self.update_bot_status(bot_id, "warning", "Auto-detect failed. Trying manual override..."))
            
            if not models:
                manual_models_str = panel_vars['manual_model'].get()
                if manual_models_str:
                    models = [m.strip() for m in manual_models_str.split(',') if m.strip()]
                    self.after(0, lambda: self.update_bot_status(bot_id, "success", f"Connected! Using manual models."))
                else:
                    self.after(0, lambda: self.update_bot_status(bot_id, "warning", "Connected, but no models found."))
            else:
                 self.after(0, lambda: self.update_bot_status(bot_id, "success", f"Connected! Found {len(models)} models."))

            self.clients[bot_id] = client
            self.after(0, lambda: self.update_bot_model_menu(bot_id, models, models[0] if models else "No models found"))

        except Exception as e:
            self.after(0, lambda: self.update_bot_status(bot_id, "error", f"Connection failed. Is a server running?"))
            self.after(0, lambda: self.update_bot_model_menu(bot_id, [], "Connection Failed"))
            self.clients[bot_id] = None

    def update_bot_model_menu(self, bot_id, models, default_selection):
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        var, menu = panel_vars['model_var'], panel_vars['model_menu']
        menu['menu'].delete(0, 'end')
        if not models: models = [default_selection]
        for model in models:
            menu['menu'].add_command(label=model, command=tk._setit(var, model))
        var.set(default_selection)

    def toggle_conversation(self):
        self.is_talking = not self.is_talking
        if self.is_talking:
            if not self.clients['A'] or not self.clients['B']:
                self.show_main_status("error", "Both bots must be connected to start.")
                self.is_talking = False
                return
            
            self.start_pause_button.config(text="PAUSE SESSION")
            
            if not self.conversation_history:
                self.next_speaker = 'A'
                self.add_message_to_history(role='user', content=self.start_prompt_text.get("1.0", "end-1c"), sender_id='System')
            
            self.continue_conversation()
        else:
            self.start_pause_button.config(text="BEGIN COLLABORATION")
            self.show_main_status("info", "Session paused by user.")

    def continue_conversation(self):
        if not self.is_talking or self.bot_turn_lock.locked():
            return

        bot_id = self.next_speaker
        panel_vars = getattr(self, f'panel_{bot_id}_vars')
        
        last_bot_message = None
        for msg in reversed(self.conversation_history):
            if msg.get('role') == 'assistant':
                last_bot_message = msg
                break
        
        last_code = ""
        if last_bot_message:
            code_match = re.search(r"```(?:\w*\n)?(.*?)```", last_bot_message['content'], re.DOTALL)
            if code_match:
                last_code = code_match.group(1).strip()

        if not last_code:
            last_code = self.start_prompt_text.get("1.0", "end-1c")

        structured_prompt = f"""It is now your turn, Bot {bot_id}.
The current state of the code/task is:
---
{last_code}
---
Your role is: {panel_vars['system_prompt_text'].get("1.0", "end-1c").strip()}
Execute your role on the code/task above.
"""
        api_history = [{'role': 'user', 'content': structured_prompt}]
        
        system_prompt = panel_vars['system_prompt_text'].get("1.0", "end-1c").strip()
        
        self.show_main_status("info", f"Bot {self.next_speaker} is thinking...")
        
        threading.Thread(target=self._get_chat_response_thread, args=(
            bot_id, panel_vars['model_var'].get(),
            system_prompt, panel_vars['temperature'].get(),
            api_history
        ), daemon=True).start()

    def _get_chat_response_thread(self, bot_id, model, system_prompt, temp, history):
        self.bot_turn_lock.acquire()
        try:
            if not self.is_talking: return
            client = self.clients.get(bot_id)
            if not client:
                self.schedule_finalization(bot_id, True, f"Bot {bot_id} is not connected.")
                return

            options = {'temperature': temp}
            start_time = time.time()
            
            response = client.chat(model=model, messages=history, stream=False, options=options)
            full_content = response['message']['content']
            response_time = time.time() - start_time
            
            self.schedule_finalization(bot_id, False, full_content, response_time)

        except Exception as e:
            self.schedule_finalization(bot_id, True, str(e))
        finally:
            if self.bot_turn_lock.locked():
                self.bot_turn_lock.release()

    def schedule_finalization(self, bot_id, is_error, content, response_time=0):
        delay_ms = int(self.turn_delay_var.get() * 1000)
        self.after(delay_ms, lambda: self.finalize_bot_response(bot_id, is_error, content, response_time))

    def finalize_bot_response(self, bot_id, is_error, content, response_time):
        if not content or not content.strip():
            self.show_main_status("warning", f"Bot {bot_id} returned an empty response. Skipping turn.")
            if self.is_talking:
                self.next_speaker = 'B' if bot_id == 'A' else 'A'
                self.after(100, self.continue_conversation)
            return

        if is_error:
            self.add_message_to_history(role='system', content=f"Error from Bot {bot_id}: {content}", sender_id='System')
            self.is_talking = False
            self.start_pause_button.config(text="BEGIN COLLABORATION")
        else:
            msg_data = {
                'role': 'assistant',
                'content': content,
                'sender_id': f"Bot {bot_id}",
                'response_time': response_time,
                'token_count': len(content.split())
            }
            self.add_message_to_history(**msg_data)
            
            if self.is_talking:
                self.next_speaker = 'B' if bot_id == 'A' else 'A'
                self.after(100, self.continue_conversation)

    def send_human_message(self, event=None):
        text = self.human_input_text.get("1.0", "end-1c").strip()
        if not text: return "break"
        self.add_message_to_history(role='user', content=text, sender_id='Human')
        self.human_input_text.delete("1.0", "end")
        if not self.is_talking: self.toggle_conversation()
        else: self.after(100, self.continue_conversation)
        return "break"

    def add_message_to_history(self, **msg_data):
        msg_data['timestamp'] = datetime.now()
        self.conversation_history.append(msg_data)
        
        if msg_data['sender_id'] != 'System' or msg_data.get('role') != 'user':
            ChatMessage(self.chat_frame, self, msg_data)
        
        self.update_chat_scroll()

    def rerender_chat_history(self):
        for widget in self.chat_frame.winfo_children(): widget.destroy()
        for msg in self.conversation_history:
            if msg['sender_id'] != 'System' or msg.get('role') != 'user':
                ChatMessage(self.chat_frame, self, msg)
        self.update_chat_scroll()

    def clear_conversation(self):
        self.is_talking = False
        if self.bot_turn_lock.locked(): self.bot_turn_lock.release()
        if messagebox.askokcancel("Clear Session", "This will end the current session and clear the conversation log. Proceed?"):
            self.conversation_history = []
            self.rerender_chat_history()
            self.show_main_status("info", "Session has been cleared.")
            self.start_pause_button.config(text="BEGIN COLLABORATION")

    def save_profile(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Session Profiles", "*.json")], title="Save Session Profile")
        if not filepath: return
        profile_data = {'theme': self.theme_var.get(), 'start_prompt': self.start_prompt_text.get("1.0", "end-1c"), 'bot_a': {}, 'bot_b': {}}
        for bot_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{bot_id}_vars')
            profile_data[f'bot_{bot_id.lower()}'] = {
                'host': panel_vars['host'].get(), 'port': panel_vars['port'].get(),
                'manual_model': panel_vars['manual_model'].get(), 'model': panel_vars['model_var'].get(),
                'system_prompt': panel_vars['system_prompt_text'].get("1.0", "end-1c"),
                'temperature': panel_vars['temperature'].get()
            }
        try:
            with open(filepath, 'w') as f: json.dump(profile_data, f, indent=2)
            self.show_main_status("success", f"Profile saved to {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Save Error", f"Failed to save profile: {e}")

    def load_profile(self):
        filepath = filedialog.askopenfilename(filetypes=[("Session Profiles", "*.json")], title="Load Session Profile")
        if not filepath: return
        try:
            with open(filepath, 'r') as f: profile_data = json.load(f)
            self.theme_var.set(profile_data.get('theme', 'Cyberpunk Neon'))
            self.apply_theme(self.theme_var.get())
            self.start_prompt_text.delete("1.0", "end")
            self.start_prompt_text.insert("1.0", profile_data.get('start_prompt', ''))
            for bot_id_lower in ['bot_a', 'bot_b']:
                bot_id_upper = bot_id_lower[-1].upper()
                bot_data = profile_data.get(bot_id_lower, {})
                panel_vars = getattr(self, f'panel_{bot_id_upper}_vars')
                panel_vars['host'].set(bot_data.get('host', '127.0.0.1'))
                panel_vars['port'].set(bot_data.get('port', '11434'))
                panel_vars['manual_model'].set(bot_data.get('manual_model', ''))
                panel_vars['system_prompt_text'].delete("1.0", "end")
                panel_vars['system_prompt_text'].insert("1.0", bot_data.get('system_prompt', ''))
                panel_vars['temperature'].set(bot_data.get('temperature', 0.7))
                self.clients[bot_id_upper] = None
                self.update_bot_model_menu(bot_id_upper, [bot_data.get('model', 'Connect to Server')], bot_data.get('model', 'Connect to Server'))
                self.update_bot_status(bot_id_upper, "info", "Profile loaded. Please connect.")
            self.show_main_status("success", f"Profile loaded: {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Load Error", f"Failed to load profile: {e}")

    def generate_session_summary(self):
        if not self.conversation_history: messagebox.showinfo("Summary", "No conversation to analyze."); return
        report = "--- SESSION SUMMARY ---\n\n"
        stats = {'A': {'count': 0, 'times': [], 'tokens': 0}, 'B': {'count': 0, 'times': [], 'tokens': 0}}
        for msg in self.conversation_history:
            if msg['sender_id'] == 'Bot A':
                stats['A']['count'] += 1
                if 'response_time' in msg: stats['A']['times'].append(msg['response_time'])
                if 'token_count' in msg: stats['A']['tokens'] += msg['token_count']
            elif msg['sender_id'] == 'Bot B':
                stats['B']['count'] += 1
                if 'response_time' in msg: stats['B']['times'].append(msg['response_time'])
                if 'token_count' in msg: stats['B']['tokens'] += msg['token_count']
        report += f"Total AI Turns: {stats['A']['count'] + stats['B']['count']}\n\n"
        for bot_id in ['A', 'B']:
            s = stats[bot_id]
            panel_vars = getattr(self, f'panel_{bot_id}_vars')
            report += f"Bot {bot_id} ({panel_vars['model_var'].get()}):\n"
            report += f"  - Contributions: {s['count']}\n"
            if s['times']:
                avg_time = sum(s['times']) / len(s['times'])
                report += f"  - Avg. Response Time: {avg_time:.2f}s\n"
            report += f"  - Total Tokens (Est.): {s['tokens']}\n\n"
        messagebox.showinfo("Session Summary", report, parent=self)
        
    def export_conversation(self):
        if not self.conversation_history: messagebox.showinfo("Export", "There is no conversation to export."); return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")], title="Save Conversation")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    history_for_json = [{'role': m.get('role'), 'content': m.get('content'), 'sender': m.get('sender_id')} for m in self.conversation_history]
                    json.dump(history_for_json, f, indent=2)
                else:
                    for msg in self.conversation_history:
                        f.write(f"--- {msg.get('sender_id')} ({msg.get('role')}) @ {msg['timestamp']} ---\n{msg.get('content', '')}\n\n")
            self.show_toast("Conversation exported successfully!")
        except Exception as e: messagebox.showerror("Export Error", f"Failed to save file: {e}")

    def export_code_blocks(self):
        code_blocks = []
        code_pattern = re.compile(r"```(\w*)?\n(.*?)\n```", re.DOTALL)
        for msg in self.conversation_history:
            if msg['role'] == 'assistant':
                for match in code_pattern.finditer(msg['content']):
                    code_blocks.append({
                        'sender': msg['sender_id'],
                        'lang': match.group(1) or 'txt',
                        'code': match.group(2).strip()
                    })
        
        if not code_blocks:
            messagebox.showinfo("Export Code", "No code blocks found in the conversation.")
            return

        export_type = messagebox.askquestion("Export Code", "Export as individual files?", icon='question', parent=self)

        if export_type == 'yes':
            ext = simpledialog.askstring("File Extension", "Enter file extension (e.g., .py, .js):", parent=self)
            if not ext: return
            if not ext.startswith('.'): ext = '.' + ext
            
            folder_path = filedialog.askdirectory(title="Select Folder to Save Code Files", parent=self)
            if not folder_path: return

            for i, block in enumerate(code_blocks):
                filename = f"{block['sender']}_turn_{i+1}{ext}"
                try:
                    with open(os.path.join(folder_path, filename), 'w', encoding='utf-8') as f:
                        f.write(block['code'])
                except Exception as e:
                    messagebox.showerror("File Save Error", f"Could not save {filename}:\n{e}", parent=self)
                    return
            self.show_toast(f"Successfully exported {len(code_blocks)} code files.")

        else:
            filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Save Code Blocks as JSON", parent=self)
            if not filepath: return
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(code_blocks, f, indent=2)
                self.show_toast("Successfully exported code to JSON.")
            except Exception as e:
                messagebox.showerror("File Save Error", f"Could not save JSON file:\n{e}", parent=self)

    def show_about_window(self):
        about_win = tk.Toplevel(self)
        about_win.title("About Ollama AI Forge")
        about_win.geometry("400x250")
        about_win.resizable(False, False)
        theme = self.themes[self.current_theme_name]
        about_win.configure(background=theme["bg"])

        header_frame = ttk.Frame(about_win, style='Header.TFrame', padding=10)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Ollama AI Forge", font=("Impact", 20), style='Header.TLabel').pack()
        
        main_frame = ttk.Frame(about_win, padding=15)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Version 2.1 - \"Restoration\"", font=self.bold_font).pack(pady=(0,5))
        ttk.Label(main_frame, text="A collaborative environment for AI-driven development.", wraplength=350).pack(pady=(0,15))
        ttk.Label(main_frame, text="Now with plugins, themes, and animations.", wraplength=350, justify="center").pack()
        
        ttk.Button(main_frame, text="Close", command=about_win.destroy).pack(side="bottom", pady=10)

# =====================================================================================
# APPLICATION ENTRY POINT
# =====================================================================================
if __name__ == "__main__":
    app = OllamaForgeApp()
    app.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import re
import threading
import json
import os
from __main__ import ForgePlugin

class FeatureForgePlugin(ForgePlugin):
    """
    A plugin for analyzing the main application and suggesting new features with customizable settings.
    Integrates with the OllamaForgeApp to provide AI-driven feature proposals.
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "Feature Forge"  # Unique name for plugin identification
        self.description = "Analyzes the main app and suggests new features with customizable settings."
        self.settings_file = os.path.join("plugins", "feature_forge_settings.json")
        self.default_settings = {
            "creativity_level": 0.7,
            "feature_scope": "general",
            "max_suggestions": 3,
            "include_comments": True,
            "target_component": "all"
        }
        self.settings = self.load_settings()

    def load_settings(self):
        """Load plugin settings from a JSON file, falling back to defaults if file doesn't exist."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.app.show_toast(f"Failed to load Feature Forge settings: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to a JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            messagebox.showerror(self.name, f"Failed to save settings: {e}", parent=self.app)

    def execute(self, **kwargs):
        """Execute the plugin, ensuring no active session and loading the main app code."""
        if self.app.is_talking:
            messagebox.showwarning(self.name, "Cannot run while a session is active.", parent=self.app)
            return
        
        try:
            plugin_dir = os.path.dirname(__file__)
            main_app_path = os.path.join(plugin_dir, '..', 'NewStartingPoint_V.py')
            
            if not os.path.exists(main_app_path):
                main_app_path = 'NewStartingPoint_V.py'
                if not os.path.exists(main_app_path):
                    messagebox.showerror(self.name, "Could not locate 'NewStartingPoint_V.py'.", parent=self.app)
                    return

            with open(main_app_path, 'r', encoding='utf-8') as f:
                main_app_code = f.read()
            
            ForgeWindow(self.app, main_app_code, self.settings, self.save_settings)

        except Exception as e:
            messagebox.showerror(self.name, f"Failed to read main application: {e}", parent=self.app)

class ForgeWindow(tk.Toplevel):
    """A window for configuring feature generation settings and displaying AI-generated feature proposals."""
    def __init__(self, app, main_app_code, settings, save_settings_callback):
        super().__init__(app)
        self.app = app
        self.theme = app.get_current_theme()
        self.main_app_code = main_app_code
        self.settings = settings
        self.save_settings_callback = save_settings_callback
        self.title("Feature Forge - Enhanced")
        self.geometry("1000x800")
        self.configure(bg=self.theme["bg"])
        
        try:
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Feature Forge", f"Failed to create UI: {e}", parent=self)
            self.destroy()

    def create_widgets(self):
        """Create UI elements without explicit font settings to avoid conflicts."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header with title and save button
        header = ttk.Frame(self)
        header.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        # No font specified to rely on default or theme settings
        try:
            ttk.Label(header, text="Feature Forge").pack(side="left")
        except Exception as e:
            self.app.show_toast(f"Header label error: {e}")
            ttk.Label(header, text="Feature Forge").pack(side="left")
        ttk.Button(header, text="Save Settings", command=self.save_settings).pack(side="right")

        # Main content area with settings and results
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Settings panel
        settings_frame = ttk.LabelFrame(main_pane, text="Feature Generation Settings", padding=10)
        main_pane.add(settings_frame, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        # Creativity level slider
        try:
            ttk.Label(settings_frame, text="Creativity Level:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        except Exception as e:
            self.app.show_toast(f"Creativity label error: {e}")
            ttk.Label(settings_frame, text="Creativity Level:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.creativity_var = tk.DoubleVar(value=self.settings["creativity_level"])
        ttk.Scale(settings_frame, from_=0.1, to=1.5, variable=self.creativity_var, orient="horizontal").grid(row=0, column=1, sticky="ew", padx=5)

        # Feature scope dropdown
        try:
            ttk.Label(settings_frame, text="Feature Scope:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        except Exception as e:
            self.app.show_toast(f"Feature scope label error: {e}")
            ttk.Label(settings_frame, text="Feature Scope:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.scope_var = tk.StringVar(value=self.settings["feature_scope"])
        ttk.OptionMenu(settings_frame, self.scope_var, self.settings["feature_scope"], "general", "ui", "functionality", "performance", "accessibility").grid(row=1, column=1, sticky="ew", padx=5)

        # Max suggestions spinner
        try:
            ttk.Label(settings_frame, text="Max Suggestions:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        except Exception as e:
            self.app.show_toast(f"Max suggestions label error: {e}")
            ttk.Label(settings_frame, text="Max Suggestions:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.max_suggestions_var = tk.IntVar(value=self.settings["max_suggestions"])
        ttk.Spinbox(settings_frame, from_=1, to=5, textvariable=self.max_suggestions_var).grid(row=2, column=1, sticky="ew", padx=5)

        # Include comments checkbox
        self.comments_var = tk.BooleanVar(value=self.settings["include_comments"])
        ttk.Checkbutton(settings_frame, text="Include Detailed Comments", variable=self.comments_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Target component dropdown
        try:
            ttk.Label(settings_frame, text="Target Component:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        except Exception as e:
            self.app.show_toast(f"Target component label error: {e}")
            ttk.Label(settings_frame, text="Target Component:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.target_var = tk.StringVar(value=self.settings["target_component"])
        components = ["all", "chat_arena", "controls_panel", "plugin_system", "theme_system"]
        ttk.OptionMenu(settings_frame, self.target_var, self.settings["target_component"], *components).grid(row=4, column=1, sticky="ew", padx=5)

        # Results panel
        results_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(results_frame, weight=3)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # No font specified for ScrolledText to avoid errors
        try:
            self.results_text = scrolledtext.ScrolledText(results_frame, wrap="word", bg=self.theme["widget_bg"], fg=self.theme["fg"], relief="flat")
        except Exception as e:
            self.app.show_toast(f"ScrolledText error: {e}")
            self.results_text = scrolledtext.ScrolledText(results_frame, wrap="word", bg=self.theme["widget_bg"], fg=self.theme["fg"], relief="flat")
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.insert("1.0", "Configure settings and press 'Generate Features' to analyze the application.")
        self.results_text.config(state="disabled")

        # Generate button
        self.generate_button = ttk.Button(self, text="Generate Features", style="Big.TButton", command=self.run_feature_generation)
        self.generate_button.grid(row=2, column=0, padx=15, pady=15, sticky="ew", ipady=5)

    def save_settings(self):
        """Update settings dictionary and save to file."""
        try:
            self.settings.update({
                "creativity_level": self.creativity_var.get(),
                "feature_scope": self.scope_var.get(),
                "max_suggestions": self.max_suggestions_var.get(),
                "include_comments": self.comments_var.get(),
                "target_component": self.target_var.get()
            })
            self.save_settings_callback()
            self.app.show_toast("Settings saved successfully!")
        except Exception as e:
            self.app.show_toast(f"Failed to save settings: {e}")

    def run_feature_generation(self):
        """Initiate feature generation process using Bot A."""
        self.generate_button.config(state="disabled", text="Generating...")
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Analyzing application code... Sending to Bot A for feature suggestions...")
        self.results_text.config(state="disabled")

        bot_id = 'A'
        panel_vars = getattr(self.app, f'panel_{bot_id}_vars')
        
        prompt = f"""You are an expert Python tkinter developer. Your task is to analyze the provided application code and suggest {self.settings['max_suggestions']} new features based on the following settings:
- Scope: {self.settings['feature_scope']}
- Target Component: {self.settings['target_component']}
- Include Detailed Comments: {self.settings['include_comments']}

Follow these steps:
1. Analyze the entire application code.
2. Identify {self.settings['max_suggestions']} missing features that align with the specified scope and target component.
3. For each feature, provide:
   - A section titled `== FEATURE {{i}} PROPOSAL ==`
   - A brief description of the feature and its benefits
   - A section titled `== FEATURE {{i}} IMPLEMENTATION ==`
   - Complete Python code for integration into the `OllamaForgeApp` class
   - {'Detailed explanatory comments in the code' if self.settings['include_comments'] else 'Minimal comments'}

Application code:
```python
{self.main_app_code}
```"""
        api_history = [{'role': 'user', 'content': prompt}]
        threading.Thread(target=self.generation_thread_worker, args=(bot_id, panel_vars, api_history), daemon=True).start()

    def generation_thread_worker(self, bot_id, panel_vars, history):
        """Worker thread for generating features via Bot A API call."""
        try:
            client = self.app.clients.get(bot_id)
            if not client:
                self.app.after(0, lambda: self.show_result(f"# ERROR: Bot {bot_id} not connected."))
                return
            response = client.chat(
                model=panel_vars['model_var'].get(),
                messages=history,
                stream=False,
                options={'temperature': self.settings['creativity_level']}
            )
            self.app.after(0, lambda: self.show_result(response['message']['content']))
        except Exception as e:
            self.app.after(0, lambda: self.show_result(f"# ERROR: Feature generation failed.\n# {e}"))
        finally:
            self.app.after(0, lambda: self.generate_button.config(state="normal", text="Generate Features"))

    def show_result(self, result_text):
        """Display the generated feature suggestions in the results text area."""
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        
        # Use minimal, cross-platform font strings for text tags
        try:
            self.results_text.tag_configure("h1", font="Helvetica 12 bold", foreground=self.theme["bot_a_color"], spacing1=10)
            self.results_text.tag_configure("h2", font="Helvetica 10 bold", foreground=self.theme["bot_b_color"], spacing1=8)
            self.results_text.tag_configure("code", font="Courier 10", background=self.theme["code_bg"], foreground=self.theme["code_fg"], lmargin1=10, lmargin2=10, borderwidth=1, relief="solid")
        except Exception as e:
            self.app.show_toast(f"Text tag configuration error: {e}")
            # Fallback to Tkinter's default font
            self.results_text.tag_configure("h1", font="TkDefaultFont", foreground=self.theme["bot_a_color"], spacing1=10)
            self.results_text.tag_configure("h2", font="TkDefaultFont", foreground=self.theme["bot_b_color"], spacing1=8)
            self.results_text.tag_configure("code", font="TkFixedFont", background=self.theme["code_bg"], foreground=self.theme["code_fg"], lmargin1=10, lmargin2=10, borderwidth=1, relief="solid")

        in_code_block = False
        for line in result_text.splitlines():
            if line.startswith("== FEATURE"):
                if "PROPOSAL" in line:
                    self.results_text.insert("end", f"\n{line.replace('==', '').strip()}\n", "h1")
                elif "IMPLEMENTATION" in line:
                    self.results_text.insert("end", f"\n{line.replace('==', '').strip()}\n", "h2")
                continue
            elif "```" in line:
                in_code_block = not in_code_block
            else:
                tag = "code" if in_code_block else "body"
                self.results_text.insert("end", line + "\n", tag)
        
        self.results_text.config(state="disabled")

def load_plugin(app):
    """Plugin entry point required by PluginManager to instantiate the plugin."""
    try:
        return FeatureForgePlugin(app)
    except Exception as e:
        app.show_toast(f"Failed to instantiate Feature Forge plugin: {e}")
        raise
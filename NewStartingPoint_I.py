import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
import ollama
from ollama._client import ResponseError
import threading
import time
from datetime import datetime
import json
import os
import platform
import subprocess

# =====================================================================================
# THEME DEFINITIONS
# =====================================================================================
THEMES = {
    "Dracula": {
        "bg": "#282a36", "fg": "#f8f8f2", "widget_bg": "#383a59", "select_bg": "#44475a",
        "button_bg": "#6272a4", "button_fg": "#f8f8f2", "button_accent_bg": ("#bd93f9", "#ff79c6"),
        "bot_a_color": "#50fa7b", "bot_b_color": "#ffb86c", "system_color": "#6272a4",
        "human_color": "#8be9fd", "code_bg": "#21222C", "success_fg": "#50fa7b", "error_fg": "#ff5555",
        "timestamp_color": "#9a9a9a", "border_color": "#6272a4"
    },
    "Nord": {
        "bg": "#2E3440", "fg": "#D8DEE9", "widget_bg": "#3B4252", "select_bg": "#434C5E",
        "button_bg": "#5E81AC", "button_fg": "#ECEFF4", "button_accent_bg": ("#88C0D0", "#81A1C1"),
        "bot_a_color": "#A3BE8C", "bot_b_color": "#EBCB8B", "system_color": "#81A1C1",
        "human_color": "#B48EAD", "code_bg": "#2E3440", "success_fg": "#A3BE8C", "error_fg": "#BF616A",
        "timestamp_color": "#D8DEE9", "border_color": "#4C566A"
    }
}

# =====================================================================================
# UI COMPONENTS
# =====================================================================================
class ConnectionPanel(ttk.LabelFrame):
    """A UI panel for configuring one bot's connection and parameters."""
    def __init__(self, parent, bot_id, app_instance, **kwargs):
        super().__init__(parent, text=f"Bot {bot_id} Configuration", **kwargs)
        self.bot_id = bot_id
        self.app = app_instance
        self.columnconfigure(0, weight=1)
        self.host_var = tk.StringVar(value='127.0.0.1')
        self.port_var = tk.StringVar(value='11434') # Default to same port
        self.system_prompt_var = tk.StringVar(value="You are a helpful AI assistant.")
        self.temperature_var = tk.DoubleVar(value=0.8)
        self.manual_models_var = tk.StringVar()
        self._create_widgets()

    def _create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew", pady=5)
        conn_frame = self._create_connection_tab(notebook)
        param_frame = self._create_parameters_tab(notebook)
        notebook.add(conn_frame, text='Connection')
        notebook.add(param_frame, text='Parameters')
        
        # Only Bot A can manage a server
        if self.bot_id == 'A':
            server_frame = self._create_server_tab(notebook)
            notebook.add(server_frame, text='Server Management')

    def _create_connection_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        frame.columnconfigure(1, weight=1)
        conn_details_frame = ttk.LabelFrame(frame, text="Connection Details", padding=10)
        conn_details_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        conn_details_frame.columnconfigure(1, weight=1)
        ttk.Label(conn_details_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_details_frame, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(conn_details_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_details_frame, textvariable=self.port_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(conn_details_frame, text="Connect", command=self._on_connect_click).grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        self.status_label = ttk.Label(conn_details_frame, text="Not Connected", wraplength=350)
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))
        manual_frame = ttk.LabelFrame(frame, text="Manual Model Override", padding=10)
        manual_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        manual_frame.columnconfigure(0, weight=1)
        ttk.Label(manual_frame, text="If auto-detection fails, enter model names here:", wraplength=300).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(manual_frame, textvariable=self.manual_models_var).grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(manual_frame, text="Comma-separated, e.g., llama3.1, codegemma:7b", font=self.app.italic_font).grid(row=2, column=0, sticky="w", padx=5)
        return frame

    def _create_parameters_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="System Prompt:").pack(anchor="w", padx=5)
        sys_prompt_text = tk.Text(frame, height=5, wrap="word", relief="solid", borderwidth=1)
        sys_prompt_text.pack(fill="x", expand=True, padx=5, pady=5)
        sys_prompt_text.insert("1.0", self.system_prompt_var.get())
        sys_prompt_text.bind("<KeyRelease>", lambda e: self.system_prompt_var.set(e.widget.get("1.0", "end-1c")))
        temp_frame = ttk.Frame(frame)
        temp_frame.pack(fill="x", expand=True, padx=5, pady=5)
        temp_frame.columnconfigure(1, weight=1)
        ttk.Label(temp_frame, text="Temperature:").grid(row=0, column=0, sticky="w")
        self.temp_label = ttk.Label(temp_frame, text=f"{self.temperature_var.get():.2f}")
        self.temp_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
        temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, orient="horizontal", variable=self.temperature_var, command=self._on_temp_change)
        temp_scale.grid(row=0, column=1, sticky="ew")
        return frame

    def _create_server_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        frame.columnconfigure(0, weight=1)
        ttk.Button(frame, text="Start Server on this Port", command=self._on_start_server_click).grid(row=0, column=0, pady=5, sticky="ew")
        ttk.Button(frame, text="Stop Managed Server", command=self._on_stop_server_click).grid(row=1, column=0, pady=5, sticky="ew")
        self.server_status_label = ttk.Label(frame, text="Server is not managed by this app.")
        self.server_status_label.grid(row=2, column=0, sticky="ew", pady=10)
        return frame

    def _on_connect_click(self): self.app.connect_to_ollama(self.bot_id)
    def _on_start_server_click(self): self.app.start_server(self.bot_id)
    def _on_stop_server_click(self): self.app.stop_server(self.bot_id)
    def _on_temp_change(self, value): self.temp_label.config(text=f"{float(value):.2f}")

    def update_conn_status(self, status_type, message):
        colors = {"info": "fg", "success": "success_fg", "warning": "bot_b_color", "error": "error_fg"}
        theme_color = THEMES[self.app.current_theme_name][colors.get(status_type, "fg")]
        self.status_label.config(text=message, foreground=theme_color)
    
    def update_server_status(self, status_type, message):
        colors = {"info": "fg", "success": "success_fg", "warning": "bot_b_color", "error": "error_fg"}
        theme_color = THEMES[self.app.current_theme_name][colors.get(status_type, "fg")]
        self.server_status_label.config(text=message, foreground=theme_color)

# =====================================================================================
# MAIN APPLICATION CLASS
# =====================================================================================
class OllamaArenaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ollama AI Arena")
        self.geometry("1600x900")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_theme_name = "Dracula"
        self.clients = {'A': None, 'B': None}
        self.running_servers = {}
        self.is_talking = False
        self.conversation_history = []
        self.message_widgets = {}
        self.typing_indicator = None
        self.setup_fonts()
        self.configure(background=THEMES[self.current_theme_name]["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.create_header_and_menu()
        self.create_main_layout()
        self.apply_theme(self.current_theme_name)

    def on_closing(self):
        if self.running_servers and messagebox.askyesno("Exit", "A managed Ollama server is running. Shut it down and exit?"):
            self.stop_server('A')
        self.destroy()

    def setup_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=10)
        self.bold_font = font.Font(family=self.default_font.cget("family"), size=10, weight="bold")
        self.italic_font = font.Font(family=self.default_font.cget("family"), size=10, slant="italic")
        self.code_font = font.Font(family="Consolas", size=10)
        self.monospace_font = font.Font(family="Courier New", size=10)
        self.battle_button_font = font.Font(family=self.default_font.cget("family"), size=12, weight="bold")
        self.aim_font = font.Font(family="Tahoma", size=10)

    def create_header_and_menu(self):
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=(10, 5))
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="Ollama AI Arena", font=("Segoe UI", 20, "bold"), style='Header.TLabel').pack(side="left")
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Arena", command=self.clear_conversation)
        file_menu.add_command(label="Export Conversation...", command=self.export_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Troubleshooting Guide", command=self.show_help_window)

    def show_help_window(self):
        help_win = tk.Toplevel(self)
        help_win.title("Troubleshooting Guide")
        help_win.geometry("750x600")
        theme = THEMES[self.current_theme_name]
        help_win.configure(background=theme["bg"])
        text_widget = tk.Text(help_win, wrap="word", padx=15, pady=15, background=theme["widget_bg"], foreground=theme["fg"], relief="flat", font=self.default_font)
        text_widget.pack(expand=True, fill="both")
        title_font = font.Font(family="Segoe UI", size=14, weight="bold")
        bold_font = font.Font(family="Segoe UI", size=10, weight="bold")
        code_font = font.Font(family="Consolas", size=10)
        text_widget.tag_configure("title", font=title_font, foreground=theme["button_accent_bg"][0], spacing3=10)
        text_widget.tag_configure("heading", font=bold_font, foreground=theme["bot_a_color"], spacing3=5)
        text_widget.tag_configure("code", font=code_font, background=theme["code_bg"])
        text_widget.insert("end", "Ollama Arena Troubleshooting\n\n", "title")
        text_widget.insert("end", "Core Concept: One OS, One Server\n", "heading")
        text_widget.insert("end", "Ollama is designed to run one server instance directly on an operating system. Trying to run two `ollama serve` commands in two terminals will usually fail.\n\n")
        text_widget.insert("end", "Option 1: Two Models, One Server (Recommended)\n", "heading")
        text_widget.insert("end", "This is the easiest method. You run one Ollama server and connect both Bot A and Bot B to it.\n\n")
        text_widget.insert("end", "1. Start one Ollama server in your terminal: `ollama serve`\n")
        text_widget.insert("end", "2. In the app, set both Bot A and Bot B to connect to the same port (e.g., 11434).\n")
        text_widget.insert("end", "3. After connecting, choose a different model for each bot from their dropdown menus.\n\n\n")
        text_widget.insert("end", "Option 2: Two Servers (Advanced)\n", "heading")
        text_widget.insert("end", "To run two truly separate servers, you must use virtualization like Docker.\n\n")
        text_widget.insert("end", "1. Run your default server: `ollama serve`\n")
        text_widget.insert("end", "2. Run a second server in Docker, mapping a different port. Example command:\n")
        text_widget.insert("end", "docker run -d -p 11435:11434 --name ollama2 ollama/ollama\n\n", "code")
        text_widget.insert("end", "3. In the app, connect Bot A to port 11434 and Bot B to port 11435.\n\n\n")
        text_widget.insert("end", "Problem: 'No models found' after connecting.\n", "heading")
        text_widget.insert("end", "If you connect but the model list is empty, use the 'Manual Model Override' box in the Connection tab. Type the exact names of your models (e.g., `llama3.1, codegemma:7b`) and click Connect again.\n")
        text_widget.config(state="disabled")

    def create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        controls_frame = self._create_controls_panel(main_pane)
        main_pane.add(controls_frame, weight=1)
        right_notebook = ttk.Notebook(main_pane)
        main_pane.add(right_notebook, weight=3)
        chat_frame = self._create_chat_arena(right_notebook)
        settings_frame = self._create_settings_panel(right_notebook)
        right_notebook.add(chat_frame, text='Arena')
        right_notebook.add(settings_frame, text='Connections & Settings')

    def _create_controls_panel(self, parent):
        frame = ttk.Frame(parent, padding=15)
        frame.columnconfigure(0, weight=1)
        
        # --- Theme Selector ---
        theme_selector_frame = ttk.Frame(frame)
        theme_selector_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ttk.Label(theme_selector_frame, text="Theme:", font=self.bold_font).pack(side="left")
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        ttk.OptionMenu(theme_selector_frame, self.theme_var, self.current_theme_name, *THEMES.keys(), command=self.apply_theme).pack(side="left", padx=10)
        
        # --- Chat Style Selector ---
        style_selector_frame = ttk.Frame(frame)
        style_selector_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        ttk.Label(style_selector_frame, text="Chat Style:", font=self.bold_font).pack(side="left")
        self.chat_style_var = tk.StringVar(value="Modern Bubbles")
        ttk.OptionMenu(style_selector_frame, self.chat_style_var, "Modern Bubbles", "Modern Bubbles", "Classic SMS", "AIM", "Discord", "Standard", command=self.rerender_chat_history).pack(side="left", padx=10)

        # --- Chat Mode ---
        ttk.Label(frame, text="Chat Mode", font=self.bold_font).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.chat_mode_var = tk.StringVar(value="Bot vs. Bot")
        ttk.OptionMenu(frame, self.chat_mode_var, "Bot vs. Bot", "Bot vs. Bot", "Human vs. Bot").grid(row=3, column=0, sticky="ew", pady=(0, 15))

        # --- Model Selectors ---
        self.model_menus = {'A': self._create_model_selector(frame, "Bot A Model", 4), 'B': self._create_model_selector(frame, "Bot B Model", 5)}

        # --- Starting Prompt ---
        prompt_frame = ttk.LabelFrame(frame, text="Starting Prompt", padding=10)
        prompt_frame.grid(row=6, column=0, pady=15, sticky="ew")
        prompt_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = tk.Text(prompt_frame, height=8, wrap="word", relief="solid", borderwidth=1)
        self.start_prompt_text.insert("1.0", "Write a short, dramatic story about a lone astronaut who discovers an impossible artifact on a desolate moon.")
        self.start_prompt_text.pack(fill="both", expand=True)

        # --- Action Buttons ---
        self.start_pause_button = self._create_gradient_button(frame, text="START BATTLE", command=self.toggle_conversation)
        self.start_pause_button.grid(row=7, column=0, pady=(20, 10), sticky="ew")
        
        # --- Status Label ---
        status_frame = ttk.LabelFrame(frame, text="Status", padding=10)
        status_frame.grid(row=8, column=0, sticky="ew", pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="Welcome! Connect your bots in the settings tab.", wraplength=350, justify="left")
        self.status_label.pack(fill="x")
        
        return frame
    
    def _create_model_selector(self, parent, title, row):
        frame = ttk.LabelFrame(parent, text=title, padding=5)
        frame.grid(row=row, column=0, pady=5, sticky="ew")
        frame.columnconfigure(0, weight=1)
        var = tk.StringVar()
        menu = ttk.OptionMenu(frame, var, "Connect in Settings")
        menu.pack(fill="x")
        return {'var': var, 'menu': menu}

    def _create_gradient_button(self, parent, text, command):
        btn = tk.Canvas(parent, height=45, highlightthickness=0)
        btn.text_id = btn.create_text(0, 0, text=text, anchor="c", font=self.battle_button_font)
        def _on_release(event):
            if btn._state == "pressed":
                btn._state = "hover"
                self._draw_gradient_button(btn)
                if command: command()
        btn.bind("<Enter>", lambda e: self._set_button_state(btn, "hover"))
        btn.bind("<Leave>", lambda e: self._set_button_state(btn, "normal"))
        btn.bind("<Button-1>", lambda e: self._set_button_state(btn, "pressed"))
        btn.bind("<ButtonRelease-1>", _on_release)
        btn._state = "normal"
        return btn

    def _create_chat_arena(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.chat_canvas = tk.Canvas(frame, highlightthickness=0)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_frame = ttk.Frame(self.chat_canvas)
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.human_input_text = tk.Text(frame, height=4, wrap="word", relief="solid", borderwidth=1)
        self.human_input_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        self.human_input_text.bind("<Return>", self.send_human_message)
        return frame

    def _on_mousewheel(self, event):
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _create_settings_panel(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.columnconfigure((0, 1), weight=1, uniform="group1")
        frame.rowconfigure(0, weight=1)
        self.conn_panel_A = ConnectionPanel(frame, 'A', self)
        self.conn_panel_A.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.conn_panel_B = ConnectionPanel(frame, 'B', self)
        self.conn_panel_B.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        return frame

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name
        theme = THEMES[theme_name]
        style = ttk.Style(self)
        style.theme_use('default')
        self.configure(background=theme["bg"])
        style.configure('.', background=theme["widget_bg"], foreground=theme["fg"], borderwidth=0, relief="flat")
        style.configure('TEntry', fieldbackground=theme["select_bg"], foreground=theme["fg"], insertcolor=theme["fg"])
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabel', background=theme["widget_bg"], foreground=theme["fg"])
        style.configure('Header.TFrame', background=theme["bg"])
        style.configure('Header.TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TLabelFrame', background=theme["bg"])
        style.configure('TLabelFrame.Label', background=theme["bg"], foreground=theme["fg"], font=self.bold_font)
        style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"], padding=8, font=self.bold_font)
        style.map('TButton', background=[('active', theme["select_bg"])])
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', padding=[10, 5], font=self.bold_font)
        style.map('TNotebook.Tab', background=[('selected', theme["select_bg"])], foreground=[('selected', theme["button_fg"])])
        style.configure('TMenubutton', background=theme["button_bg"], foreground=theme["button_fg"])
        self.chat_canvas.configure(background=theme["bg"])
        self.chat_frame.configure(style='TFrame')
        for widget in [self.start_prompt_text, self.human_input_text]:
            widget.configure(background=theme["widget_bg"], fg=theme["fg"], insertbackground=theme["fg"],
                             relief="solid", borderwidth=1, bd=1, highlightthickness=1,
                             highlightbackground=theme["border_color"], highlightcolor=theme["button_accent_bg"][0])
        self._draw_gradient_button(self.start_pause_button)
        self.rerender_chat_history()

    def _set_button_state(self, btn, state):
        if btn._state != "disabled":
            btn._state = state
            self._draw_gradient_button(btn)

    def _draw_gradient_button(self, btn):
        theme = THEMES[self.current_theme_name]
        btn.delete("gradient")
        width, height = btn.winfo_width(), btn.winfo_height()
        if width == 1 or height == 1:
            self.after(20, lambda: self._draw_gradient_button(btn))
            return
        start_color, end_color = theme["button_accent_bg"]
        start_r, start_g, start_b = self.winfo_rgb(start_color)
        end_r, end_g, end_b = self.winfo_rgb(end_color)
        if btn._state == "hover":
            factor = 5000
            start_r, start_g, start_b = (min(65535, c + factor) for c in (start_r, start_g, start_b))
            end_r, end_g, end_b = (min(65535, c + factor) for c in (end_r, end_g, end_b))
        elif btn._state == "pressed":
            factor = -5000
            start_r, start_g, start_b = (max(0, c + factor) for c in (start_r, start_g, start_b))
            end_r, end_g, end_b = (max(0, c + factor) for c in (end_r, end_g, end_b))
        for i in range(height):
            r = int(start_r + (end_r - start_r) * i / height)
            g = int(start_g + (end_g - start_g) * i / height)
            b = int(start_b + (end_b - start_b) * i / height)
            color = f'#{r:04x}{g:04x}{b:04x}'
            btn.create_line(0, i, width, i, fill=color, tags="gradient")
        btn.itemconfig(btn.text_id, fill=theme["button_fg"])
        btn.coords(btn.text_id, width / 2, height / 2)
        btn.tag_raise(btn.text_id)

    # --- Backend Logic Methods ---

    def start_server(self, bot_id):
        panel = self.conn_panel_A if bot_id == 'A' else self.conn_panel_B
        if bot_id in self.running_servers:
            panel.update_server_status("warning", f"Server for Bot {bot_id} is already managed.")
            return
        try:
            port = int(panel.port_var.get())
            host = panel.host_var.get()
        except ValueError:
            panel.update_server_status("error", "Port must be a number.")
            return
        panel.update_server_status("info", f"Starting on {host}:{port}...")
        env = os.environ.copy()
        env['OLLAMA_HOST'] = f"{host}:{port}"
        try:
            popen_kwargs = {'env': env, 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'text': True}
            if platform.system() == "Windows":
                popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(['ollama', 'serve'], **popen_kwargs)
            self.running_servers[bot_id] = process
            threading.Thread(target=self._monitor_server, args=(bot_id, process), daemon=True).start()
        except Exception as e:
            panel.update_server_status("error", f"Failed to start server: {e}")

    def _monitor_server(self, bot_id, process):
        time.sleep(2.5)
        panel = self.conn_panel_A if bot_id == 'A' else self.conn_panel_B
        if process.poll() is not None:
            error_output = process.stderr.read()
            self.after(0, lambda: panel.update_server_status("error", f"Server failed to start. Check logs."))
            messagebox.showerror("Ollama Server Error", f"Failed to start server for Bot {bot_id}:\n\n{error_output}")
        else:
            self.after(0, lambda: panel.update_server_status("success", f"Running (PID: {process.pid})"))
            self.after(100, lambda: self.connect_to_ollama(bot_id))
    
    def stop_server(self, bot_id):
        panel = self.conn_panel_A if bot_id == 'A' else self.conn_panel_B
        if bot_id not in self.running_servers:
            panel.update_server_status("warning", "No managed server found.")
            return
        panel.update_server_status("info", "Stopping...")
        process = self.running_servers.pop(bot_id)
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            process.kill()
        panel.update_server_status("info", "Server is not managed by this app.")
        if self.clients.get(bot_id):
            self.clients[bot_id] = None
            self.update_bot_model_menu(bot_id, [], "Connect in Settings")

    def connect_to_ollama(self, bot_id):
        panel = self.conn_panel_A if bot_id == 'A' else self.conn_panel_B
        host = panel.host_var.get()
        port = panel.port_var.get()
        full_host = f"http://{host}:{port}"
        panel.update_conn_status("info", f"Connecting to {full_host}...")
        threading.Thread(target=self._connect_thread, args=(bot_id, full_host, panel), daemon=True).start()

    def _connect_thread(self, bot_id, host, panel):
        try:
            client = ollama.Client(host=host, timeout=60) # Increased timeout
            models = []
            try:
                response = client.list()
                models = [m.get('name') for m in response.get('models', []) if m.get('name')]
            except Exception as api_err:
                print(f"API list() failed for Bot {bot_id}: {api_err}. Falling back to manual list.")

            if not models:
                manual_models_str = panel.manual_models_var.get()
                if manual_models_str:
                    models = [m.strip() for m in manual_models_str.split(',') if m.strip()]
                    self.after(0, lambda: panel.update_conn_status("success", f"Connected! Using manually specified models."))
                else:
                    self.after(0, lambda: panel.update_conn_status("warning", "Connected, but no models found. Use Manual Override or see Help menu."))
            else:
                 self.after(0, lambda: panel.update_conn_status("success", f"Connected! Found {len(models)} models."))

            self.clients[bot_id] = client
            self.after(0, lambda: self.update_bot_model_menu(bot_id, models, models[0] if models else "No models found"))

        except ollama.ResponseError as e:
            self.after(0, lambda: panel.update_conn_status("error", f"Ollama Error: {e.error}"))
            self.after(0, lambda: self.update_bot_model_menu(bot_id, [], "Connection Failed"))
        except Exception as e:
            self.after(0, lambda: panel.update_conn_status("error", f"Connection failed. Is a server running on this port? See Help menu."))
            self.after(0, lambda: self.update_bot_model_menu(bot_id, [], "Connection Failed"))

    def update_bot_model_menu(self, bot_id, models, default_selection):
        menu_info = self.model_menus[bot_id]
        var, menu = menu_info['var'], menu_info['menu']
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
            self.start_pause_button.itemconfig(self.start_pause_button.text_id, text="PAUSE BATTLE")
            # If starting a new conversation, add the initial prompt
            if not self.conversation_history:
                self.add_message_to_history('user', self.start_prompt_text.get("1.0", "end-1c"), 'System')
            else: # Otherwise, just continue
                self.continue_conversation()
        else:
            self.start_pause_button.itemconfig(self.start_pause_button.text_id, text="START BATTLE")
            self.show_main_status("info", "Conversation paused.")

    def continue_conversation(self):
        if not self.is_talking: return
        
        # FIXED: Correct turn-taking logic
        last_assistant_sender = None
        for msg in reversed(self.conversation_history):
            if msg['role'] == 'assistant':
                last_assistant_sender = msg['sender_id']
                break
        
        next_bot_id_char = 'B' if last_assistant_sender == 'Bot A' else 'A'
        
        self.show_typing_indicator(f"Bot {next_bot_id_char} is typing...")
        
        panel = self.conn_panel_A if next_bot_id_char == 'A' else self.conn_panel_B
        api_history = [{'role': msg['role'], 'content': msg['content']} for msg in self.conversation_history if msg['role'] in ['user', 'assistant']]
        
        threading.Thread(target=self._get_chat_response_thread, args=(
            next_bot_id_char, self.model_menus[next_bot_id_char]['var'].get(),
            panel.system_prompt_var.get(), panel.temperature_var.get(),
            api_history
        ), daemon=True).start()

    def _get_chat_response_thread(self, bot_id, model, system_prompt, temp, history):
        client = self.clients.get(bot_id)
        if not client:
            self.after(0, lambda: self.finalize_bot_response(bot_id, True, f"Bot {bot_id} is not connected."))
            return
        if system_prompt: history.insert(0, {'role': 'system', 'content': system_prompt})
        options = {'temperature': temp}
        try:
            response = client.chat(model=model, messages=history, stream=False, options=options)
            full_content = response['message']['content']
            self.after(0, lambda: self.finalize_bot_response(bot_id, False, full_content))
        except Exception as e:
            self.after(0, lambda err=e: self.finalize_bot_response(bot_id, True, str(err)))

    def finalize_bot_response(self, bot_id, is_error, full_content):
        self.hide_typing_indicator()
        if is_error:
            self.add_message_to_history('system', f"Error from Bot {bot_id}: {full_content}", 'System')
            self.is_talking = False
            self.start_pause_button.itemconfig(self.start_pause_button.text_id, text="START BATTLE")
        else:
            self.add_message_to_history('assistant', full_content, f"Bot {bot_id}")
            if self.is_talking: self.after(100, self.continue_conversation)

    def send_human_message(self, event=None):
        text = self.human_input_text.get("1.0", "end-1c").strip()
        if not text: return "break"
        self.add_message_to_history('user', text, 'Human')
        self.human_input_text.delete("1.0", "end")
        if not self.is_talking: self.toggle_conversation()
        return "break"

    def add_message_to_history(self, role, content, sender_id):
        if not content or not content.strip():
            return # Don't add empty messages
        
        msg = {'role': role, 'content': content, 'sender_id': sender_id, 'timestamp': datetime.now()}
        self.conversation_history.append(msg)
        
        # If the message is from the system prompt, don't display it, just start the conversation
        if sender_id == 'System' and role == 'user':
            self.continue_conversation()
        else:
            self.add_message_to_display(msg)
    
    def add_message_to_display(self, msg):
        theme = THEMES[self.current_theme_name]
        chat_style = self.chat_style_var.get()
        sender = msg.get('sender_id', 'System')
        
        is_user = sender == 'Human'
        anchor = "e" if is_user else "w"
        
        row_frame = ttk.Frame(self.chat_frame)
        row_frame.pack(fill="x", anchor=anchor, padx=10, pady=2)

        if chat_style == "Standard":
            self._draw_standard_message(row_frame, sender, msg, theme)
        else:
            self._draw_bubble_message(row_frame, sender, msg, theme, chat_style)
        
        self.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.after(100, lambda: self.chat_canvas.yview_moveto(1.0))

    def show_typing_indicator(self, text):
        if self.typing_indicator: self.typing_indicator.destroy()
        theme = THEMES[self.current_theme_name]
        self.typing_indicator = ttk.Label(self.chat_frame, text=text, font=self.italic_font, foreground=theme["timestamp_color"])
        self.typing_indicator.pack(pady=10, anchor='w', padx=10)
        self.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
    
    def hide_typing_indicator(self):
        if self.typing_indicator:
            self.typing_indicator.destroy()
            self.typing_indicator = None

    def rerender_chat_history(self, event=None):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        for msg in self.conversation_history:
            if msg['role'] != 'system':
                self.add_message_to_display(msg)

    def _draw_standard_message(self, parent, sender, msg, theme):
        header_color = theme.get(f"{sender.lower()}_color", theme["fg"])
        header_text = f"{sender} at {msg['timestamp'].strftime('%I:%M %p')}"
        ttk.Label(parent, text=header_text, font=self.bold_font, foreground=header_color).pack(anchor="w")
        ttk.Label(parent, text=msg['content'], wraplength=self.chat_canvas.winfo_width() - 50, justify="left").pack(anchor="w", pady=(0,10))

    def _draw_bubble_message(self, parent, sender, msg, theme, style):
        is_user = sender == 'Human'
        
        bubble_container = ttk.Frame(parent)
        pack_side = "right" if is_user else "left"
        bubble_container.pack(side=pack_side, anchor="w" if not is_user else "e", pady=5)

        if style == "AIM":
            bubble_color = "#FFFFFF"
            text_color = "#000000"
            font_choice = self.aim_font
            header_text = f"<{sender}>"
            header_color = "#0000FF" if is_user else "#FF0000"
            ttk.Label(bubble_container, text=header_text, font=self.aim_font, foreground=header_color).pack(anchor="w")
        elif style == "Discord":
            bubble_color = theme["bg"]
            text_color = theme["fg"]
            font_choice = self.default_font
            header_color = theme.get(f"{sender.lower()}_color", theme["fg"])
            ts = msg['timestamp'].strftime('%I:%M %p')
            ttk.Label(bubble_container, text=f"{sender}  ", font=self.bold_font, foreground=header_color).pack(side="left")
            ttk.Label(bubble_container, text=ts, font=self.italic_font, foreground=theme["timestamp_color"]).pack(side="left")
            ttk.Frame(bubble_container, height=0).pack()
        else: # Modern Bubbles and Classic SMS
            bubble_color = theme["button_bg"] if is_user else theme["select_bg"]
            text_color = theme["button_fg"] if is_user else theme["fg"]
            font_choice = self.default_font
            ttk.Label(bubble_container, text=sender, font=self.bold_font).pack(anchor="w")

        bubble = tk.Label(bubble_container, text=msg['content'], wraplength=self.chat_canvas.winfo_width() * 0.6,
                          bg=bubble_color, fg=text_color, padx=10, pady=5, justify="left",
                          font=font_choice)
        
        if style == "Classic SMS":
            bubble.config(relief="solid", borderwidth=1, bd=1, highlightbackground=theme["border_color"])
        
        bubble.pack(anchor="w")
        
        ts_label = ttk.Label(bubble_container, text=msg['timestamp'].strftime('%I:%M %p'), font=self.italic_font, foreground=theme["timestamp_color"])
        ts_label.pack(anchor="e" if is_user else "w")

    def clear_conversation(self):
        if messagebox.askokcancel("Clear Arena", "Are you sure you want to clear the entire conversation? This cannot be undone."):
            self.is_talking = False
            self.conversation_history = []
            self.rerender_chat_history()
            self.show_main_status("info", "Conversation cleared.")

    def export_conversation(self):
        if not self.conversation_history:
            messagebox.showinfo("Export", "There is no conversation to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")], title="Save Conversation")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    history_for_json = [{'role': m.get('role'), 'content': m.get('content'), 'sender': m.get('sender_id')} for m in self.conversation_history]
                    json.dump(history_for_json, f, indent=2)
                else:
                    for msg in self.conversation_history:
                        f.write(f"--- {msg.get('sender_id')} ({msg.get('role')}) ---\n{msg.get('content', '')}\n\n")
            messagebox.showinfo("Export Successful", f"Conversation saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")

    def show_main_status(self, status_type, message):
        colors = {"info": "fg", "success": "success_fg", "error": "error_fg"}
        color_key = colors.get(status_type, "fg")
        theme_color = THEMES[self.current_theme_name][color_key]
        self.status_label.config(text=message, foreground=theme_color)

# =====================================================================================
# APPLICATION ENTRY POINT
# =====================================================================================
if __name__ == "__main__":
    app = OllamaArenaApp()
    app.mainloop()

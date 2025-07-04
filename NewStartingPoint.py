import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
import ollama
from ollama._client import ResponseError
import threading
import time
from datetime import datetime
import re
import subprocess
import os
import json
import platform
from pathlib import Path
import queue

# --- Theme Definitions ---
THEMES = {
    "Neko": {
        "bg": "#FFF4E0", "fg": "#5D4037", "widget_bg": "#FFE8C8",
        "button_bg": "#FFB74D", "button_fg": "#5D4037", "select_bg": "#FFCC80",
        "button_accent_bg": ("#F06292", "#E55A88"),
        "bot_a_color": "#A1887F", "bot_b_color": "#F06292", "system_color": "#90A4AE",
        "human_color": "#4DB6AC", "code_bg": "#FFF9F2", "success_fg": "#4DB6AC", "error_fg": "#E53935",
        "timestamp_color": "#A1887F"
    },
    "Kawaii": {
        "bg": "#FFF0F5", "fg": "#483D8B", "widget_bg": "#E6E6FA",
        "button_bg": "#D8BFD8", "button_fg": "#483D8B", "select_bg": "#DDA0DD",
        "button_accent_bg": ("#FFB6C1", "#FF9EAE"),
        "bot_a_color": "#FF69B4", "bot_b_color": "#87CEEB", "system_color": "#9370DB",
        "human_color": "#98FB98", "code_bg": "#FAF5FF", "success_fg": "#3CB371", "error_fg": "#FF6347",
        "timestamp_color": "#6A5ACD"
    },
    "Dracula": {
        "bg": "#282a36", "fg": "#f8f8f2", "widget_bg": "#44475a",
        "button_bg": "#bd93f9", "button_fg": "#f8f8f2", "select_bg": "#6272a4",
        "button_accent_bg": ("#ff79c6", "#fa5fb5"),
        "bot_a_color": "#50fa7b", "bot_b_color": "#ffb86c", "system_color": "#6272a4",
        "human_color": "#8be9fd", "code_bg": "#21222C", "success_fg": "#50fa7b", "error_fg": "#ff5555",
        "timestamp_color": "#9a9a9a"
    },
    "Solarized Dark": {
        "bg": "#002b36", "fg": "#839496", "widget_bg": "#073642",
        "button_bg": "#268bd2", "button_fg": "#ffffff", "select_bg": "#586e75",
        "button_accent_bg": ("#d33682", "#c32c74"),
        "bot_a_color": "#2aa198", "bot_b_color": "#b58900", "system_color": "#657b83",
        "human_color": "#859900", "code_bg": "#00252E", "success_fg": "#859900", "error_fg": "#dc322f",
        "timestamp_color": "#586e75"
    },
        "Cyberpunk Neon": {
        "bg": "#0d0221", "fg": "#93C5FD", "widget_bg": "#261447",
        "button_bg": "#ff3864", "button_fg": "#ffffff", "select_bg": "#3e1f75",
        "bot_a_color": "#00f6ff", "bot_b_color": "#fef08a", "system_color": "#5a5a5a",
        "human_color": "#50fa7b", "code_bg": "#020617", "success_fg": "#50fa7b", "error_fg": "#ff5555",
        "timestamp_color": "#8a8a8a"
    },
    "Modern Light": {
        "bg": "#F3F4F6", "fg": "#1F2937", "widget_bg": "#FFFFFF",
        "button_bg": "#3B82F6", "button_fg": "#FFFFFF", "select_bg": "#E5E7EB",
        "bot_a_color": "#1D4ED8", "bot_b_color": "#D97706", "system_color": "#4B5563",
        "human_color": "#059669", "code_bg": "#E5E7EB", "success_fg": "#16A34A", "error_fg": "#DC2626",
        "timestamp_color": "#6b7280"
    }
}

class CollapsiblePane(ttk.Frame):
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.text = text
        self._is_collapsed = True
        self.button = ttk.Button(self, text=f"▶ {self.text}", command=self.toggle, style="Toolbutton")
        self.button.grid(row=0, column=0, sticky="ew")
        self.frame = ttk.Frame(self)

    def toggle(self):
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.frame.grid_remove()
            self.button.config(text=f"▶ {self.text}")
        else:
            self.frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.button.config(text=f"▼ {self.text}")

class GradientButton(tk.Canvas):
    """A custom button widget with a gradient background."""
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self._state = "normal"  # "normal", "hover", "pressed", "disabled"
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.text_id = self.create_text(0, 0, text=self.text, anchor="c")

    def set_theme(self, text_color, gradient_start, gradient_end, disabled_bg, disabled_fg):
        self.text_color = text_color
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.disabled_bg = disabled_bg
        self.disabled_fg = disabled_fg
        self._draw_background()

    def _draw_background(self):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 or height == 1: # Not yet visible
            self.after(50, self._draw_background)
            return
        
        if self._state == "disabled":
            self.create_rectangle(0, 0, width, height, fill=self.disabled_bg, outline="", tags="gradient")
            self.itemconfig(self.text_id, fill=self.disabled_fg)
        else:
            start_r, start_g, start_b = self.winfo_rgb(self.gradient_start)
            end_r, end_g, end_b = self.winfo_rgb(self.gradient_end)
            
            if self._state == "hover":
                # Make slightly lighter on hover
                start_r, start_g, start_b = (min(65535, c + 5000) for c in (start_r, start_g, start_b))
                end_r, end_g, end_b = (min(65535, c + 5000) for c in (end_r, end_g, end_b))
            elif self._state == "pressed":
                # Make slightly darker when pressed
                start_r, start_g, start_b = (max(0, c - 5000) for c in (start_r, start_g, start_b))
                end_r, end_g, end_b = (max(0, c - 5000) for c in (end_r, end_g, end_b))

            for i in range(height):
                r = int(start_r + (end_r - start_r) * i / height)
                g = int(start_g + (end_g - start_g) * i / height)
                b = int(start_b + (end_b - start_b) * i / height)
                color = f'#{r:04x}{g:04x}{b:04x}'
                self.create_line(0, i, width, i, fill=color, tags="gradient")
            
            self.itemconfig(self.text_id, fill=self.text_color)
        
        self.coords(self.text_id, width / 2, height / 2)
        self.tag_raise(self.text_id)

    def _on_enter(self, event):
        if self._state != "disabled":
            self._state = "hover"
            self._draw_background()

    def _on_leave(self, event):
        if self._state != "disabled":
            self._state = "normal"
            self._draw_background()

    def _on_press(self, event):
        if self._state != "disabled":
            self._state = "pressed"
            self._draw_background()

    def _on_release(self, event):
        if self._state == "pressed":
            self._state = "hover"
            self._draw_background()
            if self.command:
                self.command()

    def config(self, **kwargs):
        if 'state' in kwargs:
            self._state = kwargs['state']
            self._draw_background()
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.itemconfig(self.text_id, text=self.text)
        super().config(**kwargs)

class OllamaChatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ollama AI Arena")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.clients = {'A': None, 'B': None}
        self.running_servers = {}
        self.is_talking = False
        self.conversation_history = []
        self.current_theme_name = "Neko"
        self.error_queue = queue.Queue()
        self.setup_fonts()
        self.setup_variables()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.create_header()
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.chat_tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.chat_tab_frame, text='Arena')
        self.create_chat_tab_widgets()
        self.settings_tab_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.settings_tab_frame, text='Connections & Settings')
        self.create_settings_tab_widgets()
        self.apply_theme()
        self.update_ui_for_chat_mode()
        self.after(100, self.process_error_queue)

    def on_closing(self):
        if self.running_servers:
            if messagebox.askyesno("Exit", "You have running Ollama servers managed by this app. Shut them down and exit?"):
                for bot_id in list(self.running_servers.keys()):
                    self.stop_ollama_server(bot_id, silent=True)
                self.destroy()
        else:
            self.destroy()

    def setup_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.bold_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size"), weight="bold")
        self.italic_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size"), slant="italic")
        self.code_font = font.Font(family="Consolas", size=self.default_font.cget("size"))
        self.header_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size") + 1, weight="bold")
        self.metrics_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size") - 2, slant="italic")
        self.timestamp_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size") - 2)
        self.battle_button_font = font.Font(family=self.default_font.cget("family"), size=self.default_font.cget("size") + 2, weight="bold")

    def setup_variables(self):
        default_models_path = os.path.join(Path.home(), '.ollama', 'models')
        self.host_vars = {'A': tk.StringVar(value='127.0.0.1'), 'B': tk.StringVar(value='127.0.0.1')}
        self.port_vars = {'A': tk.StringVar(value='11434'), 'B': tk.StringVar(value='11435')}
        self.models_path_vars = {'A': tk.StringVar(value=default_models_path), 'B': tk.StringVar(value=default_models_path)}
        self.model_vars = {'A': tk.StringVar(), 'B': tk.StringVar()}
        self.system_prompt_vars = {'A': tk.StringVar(value="You are a helpful AI assistant."), 'B': tk.StringVar(value="You are a helpful AI assistant.")}
        self.temperature_vars = {'A': tk.DoubleVar(value=0.8), 'B': tk.DoubleVar(value=0.8)}
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        self.chat_mode_var = tk.StringVar(value="Bot vs. Bot")

    def create_header(self):
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="Ollama AI Arena", font=("Helvetica", 24, "bold"), style='Header.TLabel').grid(row=0, column=0, sticky="w")
        theme_frame = ttk.Frame(header_frame, style='Header.TFrame')
        theme_frame.grid(row=0, column=1, sticky="e")
        ttk.Label(theme_frame, text="Theme:", style='Header.TLabel').pack(side="left", padx=(0, 5))
        self.theme_menu_header = ttk.OptionMenu(theme_frame, self.theme_var, self.current_theme_name, *THEMES.keys(), command=self.on_theme_change)
        self.theme_menu_header.pack(side="left")

    def create_chat_tab_widgets(self):
        self.chat_tab_frame.columnconfigure(1, weight=3)
        self.chat_tab_frame.columnconfigure(0, weight=1, minsize=400)
        self.chat_tab_frame.rowconfigure(0, weight=1)
        controls_frame = ttk.Frame(self.chat_tab_frame)
        controls_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.create_chat_controls(controls_frame)
        right_panel = ttk.Frame(self.chat_tab_frame)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        self.create_chat_display(right_panel)
        self.create_human_input_widgets(right_panel)

    def create_chat_controls(self, frame):
        frame.columnconfigure(0, weight=1)
        chat_mode_frame = ttk.LabelFrame(frame, text="Chat Mode")
        chat_mode_frame.grid(row=1, column=0, pady=10, sticky="ew")
        chat_mode_frame.columnconfigure(0, weight=1)
        self.chat_mode_menu = ttk.OptionMenu(chat_mode_frame, self.chat_mode_var, "Bot vs. Bot", "Bot vs. Bot", "Human vs. Bot", command=lambda _: self.update_ui_for_chat_mode())
        self.chat_mode_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.bot_a_chat_frame = self.create_model_selector_frame(frame, "Bot A Model", 'A')
        self.bot_a_chat_frame.grid(row=3, column=0, pady=10, sticky="ew")
        self.bot_b_chat_frame = self.create_model_selector_frame(frame, "Bot B Model", 'B')
        self.bot_b_chat_frame.grid(row=4, column=0, pady=10, sticky="ew")
        prompt_frame = ttk.LabelFrame(frame, text="Starting Prompt")
        prompt_frame.grid(row=5, column=0, pady=10, sticky="ew", ipady=5)
        prompt_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = tk.Text(prompt_frame, height=6, wrap="word")
        self.start_prompt_text.insert("1.0", "Write a short, dramatic story about a lone astronaut who discovers an impossible artifact on a desolate moon.")
        self.start_prompt_text.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # --- FIX: Use the new GradientButton ---
        self.start_pause_button = GradientButton(frame, text="START BATTLE", command=self.toggle_conversation, height=40)
        self.start_pause_button.grid(row=7, column=0, pady=(20, 10), sticky="ew")

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, pady=5, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_conversation)
        self.clear_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.export_button = ttk.Button(button_frame, text="Export", command=self.export_conversation)
        self.export_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        status_bar_frame = ttk.LabelFrame(frame, text="Status")
        status_bar_frame.grid(row=9, column=0, pady=10, sticky="ew")
        status_bar_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_bar_frame, text="Welcome! Configure connections in Settings.", wraplength=350, anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.status_copy_button = ttk.Button(status_bar_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.status_label.cget("text")))
        self.status_copy_button.grid(row=0, column=1, sticky="e", padx=5)
        self.status_copy_button.grid_remove()

    def create_model_selector_frame(self, parent, title, bot_id):
        frame = ttk.LabelFrame(parent, text=title)
        frame.columnconfigure(0, weight=1)
        model_menu = ttk.OptionMenu(frame, self.model_vars[bot_id], "Connect in Settings")
        model_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        frame.widget = model_menu
        return frame

    def create_chat_display(self, frame):
        chat_frame_inner = ttk.Frame(frame)
        chat_frame_inner.grid(row=0, column=0, sticky="nsew")
        chat_frame_inner.rowconfigure(0, weight=1)
        chat_frame_inner.columnconfigure(0, weight=1)
        self.chat_display = tk.Text(chat_frame_inner, state="disabled", wrap="word", borderwidth=0, relief="flat", padx=15, pady=15)
        scrollbar = ttk.Scrollbar(chat_frame_inner, orient="vertical", command=self.chat_display.yview)
        self.chat_display['yscrollcommand'] = scrollbar.set
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_human_input_widgets(self, frame):
        self.human_input_frame = ttk.LabelFrame(frame, text="Your Input")
        self.human_input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.human_input_frame.columnconfigure(0, weight=1)
        self.human_input_text = tk.Text(self.human_input_frame, height=4, wrap="word")
        self.human_input_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.human_input_text.bind("<Return>", self.send_human_message_event)
        self.human_send_button = ttk.Button(self.human_input_frame, text="Send", command=self.send_human_message)
        self.human_send_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")

    def create_settings_tab_widgets(self):
        frame = self.settings_tab_frame
        frame.columnconfigure((0, 1), weight=1, uniform="group1")
        frame.rowconfigure(0, weight=1)
        self.bot_a_settings_frame = self.create_connection_panel(frame, "Bot A Configuration", 'A')
        self.bot_a_settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0,10))
        self.bot_b_settings_frame = self.create_connection_panel(frame, "Bot B Configuration", 'B')
        self.bot_b_settings_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0,10))

    def create_connection_panel(self, parent, title, bot_id):
        main_frame = ttk.LabelFrame(parent, text=title)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        conn_frame = ttk.Frame(notebook, padding=10)
        notebook.add(conn_frame, text='Connection')
        conn_frame.columnconfigure(1, weight=1)
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.host_vars[bot_id]).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.port_vars[bot_id]).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        conn_button_frame = ttk.Frame(conn_frame)
        conn_button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(conn_button_frame, text="Connect", command=lambda: self.connect_to_ollama(bot_id)).pack(side="left", padx=5)
        ttk.Button(conn_button_frame, text="Refresh", command=lambda: self.connect_to_ollama(bot_id, is_refresh=True)).pack(side="left", padx=5)
        status_label_frame = ttk.Frame(conn_frame)
        status_label_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        status_label_frame.columnconfigure(0, weight=1)
        status_label = ttk.Label(status_label_frame, text="Not Connected", wraplength=350)
        status_label.grid(row=0, column=0, sticky="w")
        copy_button = ttk.Button(status_label_frame, text="Copy", command=lambda: self.copy_to_clipboard(status_label.cget("text")))
        copy_button.grid(row=0, column=1, sticky="e", padx=5)
        copy_button.grid_remove()
        advanced_pane = CollapsiblePane(conn_frame, text="Advanced")
        advanced_pane.grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="ew")
        advanced_pane.frame.columnconfigure(1, weight=1)
        ttk.Label(advanced_pane.frame, text="Ollama Models Path:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(advanced_pane.frame, textvariable=self.models_path_vars[bot_id]).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(advanced_pane.frame, text="(For managed servers to find models)", font=self.italic_font).grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
        param_frame = ttk.Frame(notebook, padding=10)
        notebook.add(param_frame, text='Parameters')
        param_frame.columnconfigure(1, weight=1)
        ttk.Label(param_frame, text="System Prompt:").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5,0))
        sys_prompt_text = tk.Text(param_frame, height=5, wrap="word")
        sys_prompt_text.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        sys_prompt_text.insert("1.0", self.system_prompt_vars[bot_id].get())
        sys_prompt_text.bind("<KeyRelease>", lambda e, v=self.system_prompt_vars[bot_id]: v.set(e.widget.get("1.0", "end-1c")))
        ttk.Label(param_frame, text="Temperature:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        temp_scale = ttk.Scale(param_frame, from_=0.0, to=2.0, orient="horizontal", variable=self.temperature_vars[bot_id])
        temp_scale.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        temp_label = ttk.Label(param_frame, text=f"{self.temperature_vars[bot_id].get():.2f}")
        temp_label.grid(row=2, column=2, padx=5)
        temp_scale.config(command=lambda v, l=temp_label: l.config(text=f"{float(v):.2f}"))
        server_frame = ttk.Frame(notebook, padding=10)
        notebook.add(server_frame, text='Server')
        server_frame.columnconfigure(0, weight=1)
        ttk.Button(server_frame, text="Start New Server on Port", command=lambda: self.start_ollama_server(bot_id)).grid(row=0, column=0, pady=5, sticky="ew")
        ttk.Button(server_frame, text="Stop Managed Server", command=lambda: self.stop_ollama_server(bot_id)).grid(row=1, column=0, pady=5, sticky="ew")
        server_status_frame = ttk.LabelFrame(server_frame, text="Managed Server Status")
        server_status_frame.grid(row=2, column=0, sticky="ew", pady=10)
        server_status_frame.columnconfigure(0, weight=1)
        server_status_label = ttk.Label(server_status_frame, text="Inactive")
        server_status_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        main_frame.widgets = {'status': status_label, 'copy_button': copy_button, 'server_status': server_status_label}
        return main_frame

    def start_ollama_server(self, bot_id):
        if bot_id in self.running_servers:
            messagebox.showwarning("Server Exists", f"This app is already managing a server for Bot {bot_id}.")
            return
        port_str, host_str, models_path = self.port_vars[bot_id].get(), self.host_vars[bot_id].get(), self.models_path_vars[bot_id].get()
        status_label = self.get_widgets_for_bot(bot_id)['server_status']
        status_label.config(text=f"Starting on {host_str}:{port_str}...")
        env = os.environ.copy()
        env.update({'OLLAMA_HOST': host_str, 'OLLAMA_PORT': port_str})
        if models_path: env['OLLAMA_MODELS'] = models_path
        try:
            si = subprocess.STARTUPINFO() if platform.system() == "Windows" else None
            if si:
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                ['ollama', 'serve'], env=env, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, startupinfo=si
            )
            self.running_servers[bot_id] = process
            status_label.config(text=f"Monitoring startup (PID: {process.pid})...")
            threading.Thread(target=self.monitor_server_process, args=(bot_id, process), daemon=True).start()
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not find 'ollama' command. Is Ollama installed and in your system's PATH?")
            status_label.config(text="Inactive")
            if bot_id in self.running_servers: del self.running_servers[bot_id]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server process for Bot {bot_id}: {e}")
            status_label.config(text="Failed to start")
            if bot_id in self.running_servers: del self.running_servers[bot_id]

    def monitor_server_process(self, bot_id, process):
        """
        FIX: Monitors the server process for a few seconds. If it exits,
        captures and reports the full error message from stderr.
        """
        for _ in range(5): # Check every 0.5s for 2.5s
            time.sleep(0.5)
            exit_code = process.poll()
            if exit_code is not None:
                # Process terminated, read the error
                error_output = process.stderr.read()
                self.error_queue.put({'type': 'server_error', 'bot_id': bot_id, 'error': error_output})
                return # Stop monitoring
        # If the loop completes and process is still running, assume success
        if process.poll() is None:
            self.error_queue.put({'type': 'server_started', 'bot_id': bot_id, 'pid': process.pid})

    def process_error_queue(self):
        try:
            while not self.error_queue.empty():
                msg = self.error_queue.get_nowait()
                bot_id = msg['bot_id']
                status_label = self.get_widgets_for_bot(bot_id)['server_status']
                if msg['type'] == 'server_error':
                    messagebox.showerror("Ollama Server Error", f"Failed to start server for Bot {bot_id}:\n\n{msg['error']}")
                    status_label.config(text="Failed to start")
                    if bot_id in self.running_servers: del self.running_servers[bot_id]
                elif msg['type'] == 'server_started':
                    status_label.config(text=f"Running (PID: {msg['pid']})")
                    self.connect_to_ollama(bot_id)
        finally:
            self.after(100, self.process_error_queue)

    def stop_ollama_server(self, bot_id, silent=False):
        status_label = self.get_widgets_for_bot(bot_id)['server_status']
        if bot_id not in self.running_servers:
            if not silent: messagebox.showwarning("Not Found", f"No server managed by this app was found for Bot {bot_id}.")
            return
        status_label.config(text="Stopping...")
        process = self.running_servers.pop(bot_id)
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            if not silent: messagebox.showerror("Error", f"Error stopping server for Bot {bot_id}: {e}")
        status_label.config(text="Inactive")
        if self.clients[bot_id]:
            self.clients[bot_id] = None
            self.update_model_menu(bot_id, [], "Connect in Settings")

    def connect_to_ollama(self, bot_id, is_refresh=False):
        self.clients[bot_id] = None
        panel_widgets = self.get_widgets_for_bot(bot_id)
        panel_status_label, copy_button = panel_widgets['status'], panel_widgets['copy_button']
        if is_refresh and not self.clients[bot_id]:
            self.show_connection_error(panel_status_label, copy_button, "Cannot refresh: Not connected yet.")
            return
        host = f"http://{self.host_vars[bot_id].get()}:{self.port_vars[bot_id].get()}"
        panel_status_label.config(text=f"Attempting to connect to {host}...", foreground=THEMES[self.current_theme_name]["fg"])
        copy_button.grid_remove()
        self.update_idletasks()
        try:
            client = ollama.Client(host=host, timeout=10)
            response = client.list()
            models_data = response.get('models', [])
            if not isinstance(models_data, list):
                 raise ResponseError(f"Expected 'models' to be a list, but got {type(models_data).__name__}.")
            models = [m.get('name') for m in models_data if m.get('name')]
            self.clients[bot_id] = client
            theme = THEMES[self.current_theme_name]
            if models:
                panel_status_label.config(text=f"Connection successful! Found {len(models)} models.", foreground=theme["success_fg"])
                self.update_model_menu(bot_id, models, models[0])
            else:
                panel_status_label.config(text="Connected, but no models found in server's context.", foreground=theme["bot_b_color"])
                self.update_model_menu(bot_id, [], "No models found")
        except ConnectionError:
            self.update_model_menu(bot_id, [], "Connection Failed")
            self.show_connection_error(panel_status_label, copy_button, f"Connection Failed. Check if server is running at {host}.")
        except ResponseError as e:
            self.update_model_menu(bot_id, [], "Connection Failed")
            self.show_connection_error(panel_status_label, copy_button, f"Server Error: {getattr(e, 'error', 'Unknown')}")
        except Exception as e:
            self.update_model_menu(bot_id, [], "Connection Failed")
            self.show_connection_error(panel_status_label, copy_button, f"An unexpected error occurred: {type(e).__name__}")

    def toggle_conversation(self):
        if self.is_talking:
            self.is_talking = False
            self.start_pause_button.config(text="START BATTLE")
            self.show_main_status("Conversation paused. You can intervene below.", clear_after=0)
            self.set_frame_widgets_state(self.human_input_frame, "normal")
        else:
            if not self.clients['A'] or not self.clients['B']:
                self.show_main_status_error("Cannot start: Both bots must be connected in Settings.")
                return
            self.is_talking = True
            self.start_pause_button.config(text="PAUSE BATTLE")
            self.show_main_status("Conversation running...")
            self.set_frame_widgets_state(self.human_input_frame, "disabled")
            if not self.conversation_history:
                prompt = self.start_prompt_text.get("1.0", "end-1c")
                self.add_message_to_history('system', f'Conversation started with prompt: "{prompt}"')
                self.add_message_to_history('user', prompt, sender='Human')
            self.continue_conversation()

    def continue_conversation(self):
        if not self.is_talking: return
        last_message = self.conversation_history[-1]
        next_speaker_id = 'A' if last_message.get('role') == 'assistant' and last_message.get('sender') == 'B' else 'B' if last_message.get('role') == 'assistant' else 'A'
        self.trigger_bot_response(next_speaker_id)

    def send_human_message_event(self, event):
        self.send_human_message()
        return "break"

    def send_human_message(self):
        text = self.human_input_text.get("1.0", "end-1c").strip()
        if not text: return
        self.human_input_text.delete("1.0", "end")
        mode = self.chat_mode_var.get()
        if mode == "Human vs. Bot":
            if not self.clients['B']:
                self.show_main_status_error("Cannot send: Bot B is not connected.")
                return
            self.add_message_to_history('user', text, sender='Human')
            self.trigger_bot_response('B')
        elif mode == "Bot vs. Bot" and not self.is_talking:
            self.add_message_to_history('user', text, sender='Human')
            self.is_talking = True
            self.start_pause_button.config(text="PAUSE BATTLE")
            self.set_frame_widgets_state(self.human_input_frame, "disabled")
            self.continue_conversation()

    def trigger_bot_response(self, bot_id):
        threading.Thread(target=self.get_bot_response_stream, args=(bot_id,), daemon=True).start()

    def get_bot_response_stream(self, bot_id):
        client, model_name = self.clients[bot_id], self.model_vars[bot_id].get()
        messages_for_api = [{'role': m['role'], 'content': m['content']} for m in self.conversation_history]
        system_prompt = self.system_prompt_vars[bot_id].get()
        if system_prompt: messages_for_api.insert(0, {'role': 'system', 'content': system_prompt})
        options = {'temperature': self.temperature_vars[bot_id].get()}
        try:
            self.after(0, self.show_main_status, f"Bot {bot_id} ({model_name.split(':')[0]}) is thinking...")
            message_id = f"msg_{time.time()}"
            self.add_message_to_history('assistant', "...", sender=bot_id, id=message_id, metrics={'start_time': time.time()})
            stream = client.chat(model=model_name, messages=messages_for_api, stream=True, options=options)
            full_response = ""
            for chunk in stream:
                content_chunk = chunk['message'].get('content', '')
                if content_chunk:
                    full_response += content_chunk
                    self.after(0, self.update_streamed_message, message_id, content_chunk)
            self.finalize_streamed_message(message_id, full_response)
            self.after(0, self.show_main_status, "Ready.", clear_after=3000)
            if self.chat_mode_var.get() == "Bot vs. Bot": self.after(100, self.continue_conversation)
        except Exception as e:
            error_message = f"API Error (Bot {bot_id}): {e}"
            self.after(0, self.show_main_status_error, error_message)
            self.after(0, self.finalize_streamed_message, message_id, f"--- ERROR ---\n{error_message}", is_error=True)
            if self.is_talking: self.after(0, self.toggle_conversation)

    def add_message_to_history(self, role, content, sender=None, id=None, metrics=None):
        if sender is None: sender = 'System'
        if id is None: id = f"msg_{time.time()}"
        message = {'id': id, 'role': role, 'content': content, 'sender': sender, 'timestamp': datetime.now()}
        if metrics: message['metrics'] = metrics
        self.conversation_history.append(message)
        self.after(0, self.render_new_message, message)

    def update_streamed_message(self, message_id, text_chunk):
        try:
            self.chat_display.config(state="normal")
            self.chat_display.insert(f"{message_id}_content_end", text_chunk)
            self.chat_display.see("end")
        except tk.TclError: pass
        finally: self.chat_display.config(state="disabled")

    def finalize_streamed_message(self, message_id, full_content, is_error=False):
        for msg in self.conversation_history:
            if msg.get('id') == message_id:
                msg['content'] = full_content
                if 'metrics' in msg and 'start_time' in msg['metrics']:
                    duration = time.time() - msg['metrics']['start_time']
                    tokens = len(re.findall(r'\w+', full_content))
                    tps = tokens / duration if duration > 0 else 0
                    msg['metrics'].update({'duration': duration, 'tokens': tokens, 'tps': tps})
                break
        self.after(0, self.rerender_message_by_id, message_id)

    def render_new_message(self, msg):
        self.chat_display.config(state="normal")
        self.render_message_content(msg)
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    def rerender_message_by_id(self, message_id):
        self.chat_display.config(state="normal")
        try:
            self.chat_display.delete(f"{message_id}_start", f"{message_id}_end")
            msg_to_render, insert_index = None, "end"
            for i, msg in enumerate(self.conversation_history):
                if msg.get('id') == message_id:
                    msg_to_render = msg
                    if i + 1 < len(self.conversation_history):
                        next_msg_id = self.conversation_history[i+1].get('id')
                        if next_msg_id: insert_index = f"{next_msg_id}_start"
                    break
            if msg_to_render:
                original_end = self.chat_display.index("end-1c")
                self.chat_display.mark_set("insert", insert_index)
                self.render_message_content(msg_to_render)
                if insert_index != "end": self.chat_display.mark_set("insert", original_end)
        except tk.TclError as e: print(f"TCL error during re-render: {e}")
        finally: self.chat_display.config(state="disabled")

    def render_message_content(self, msg):
        msg_id, sender, content = msg.get('id'), msg.get('sender', 'System'), msg.get('content', '')
        start_mark, end_mark = f"{msg_id}_start", f"{msg_id}_end"
        self.chat_display.mark_set(start_mark, "insert")
        self.chat_display.mark_gravity(start_mark, "left")
        header_text, header_tag = ("Bot A", "bot_a_header") if sender == 'A' else \
                                  ("Bot B", "bot_b_header") if sender == 'B' else \
                                  ("Human", "human_header") if sender.startswith('Human') else \
                                  ("System", "system_header")
        if sender in ('A', 'B'): header_text += f" ({self.model_vars[sender].get().split(':')[0]})"
        self.chat_display.insert("end", header_text, (header_tag, "bold"))
        timestamp = msg.get('timestamp')
        if timestamp:
            ts_text = f" [{timestamp.strftime('%H:%M:%S')}]"
            self.chat_display.insert("end", ts_text, "timestamp_tag")
        metrics = msg.get('metrics')
        if metrics and 'duration' in metrics:
            metrics_text = f" ({metrics['duration']:.2f}s, {metrics['tokens']} tk, {metrics['tps']:.1f} tk/s)"
            self.chat_display.insert("end", metrics_text, ("metrics", header_tag))
        self.chat_display.insert("end", "\n")
        content_end_mark = f"{msg_id}_content_end"
        if content == "...": self.chat_display.insert("end", content, "italic")
        else: self.insert_formatted_text(content)
        self.chat_display.mark_set(content_end_mark, "insert")
        self.chat_display.mark_gravity(content_end_mark, "left")
        self.chat_display.insert("end", "\n\n")
        self.chat_display.mark_set(end_mark, "insert")
        self.chat_display.mark_gravity(end_mark, "left")

    def insert_formatted_text(self, text):
        code_pattern = re.compile(r"```(?:\w*)\n([\s\S]*?)\n```", re.MULTILINE)
        last_end = 0
        for match in code_pattern.finditer(text):
            self.insert_simple_markdown(text[last_end:match.start()])
            code = match.group(1)
            self.chat_display.insert("end", "\n")
            self.chat_display.insert("end", code, "code")
            self.chat_display.insert("end", "\n")
            last_end = match.end()
        self.insert_simple_markdown(text[last_end:])

    def insert_simple_markdown(self, text):
        pattern = r"(\*\*.*?\*\*)|(\*.*?\*)"
        parts = re.split(pattern, text)
        for part in filter(None, parts):
            if part.startswith('**') and part.endswith('**'): self.chat_display.insert("end", part[2:-2], "bold")
            elif part.startswith('*') and part.endswith('*'): self.chat_display.insert("end", part[1:-1], "italic")
            else: self.chat_display.insert("end", part)

    def apply_theme(self):
        theme = THEMES[self.current_theme_name]
        style = ttk.Style(self)
        style.theme_use('default')
        self.configure(background=theme["bg"])
        style.configure('.', background=theme["widget_bg"], foreground=theme["fg"], borderwidth=0, relief="flat")
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabel', background=theme["widget_bg"], foreground=theme["fg"])
        style.configure('TLabelFrame', background=theme["bg"], bordercolor=theme["fg"], relief="groove")
        style.configure('TLabelFrame.Label', background=theme["bg"], foreground=theme["fg"])
        style.configure('Header.TFrame', background=theme["bg"])
        style.configure('Header.TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', background=theme["widget_bg"], foreground=theme["fg"], padding=[10, 5], borderwidth=0, font=self.bold_font)
        style.map('TNotebook.Tab', background=[('selected', theme["select_bg"])], foreground=[('selected', theme["button_fg"])])
        style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"], padding=8, font=self.bold_font)
        style.map('TButton', background=[('active', theme["select_bg"])])
        style.configure('Toolbutton', padding=2, relief="flat", background=theme["bg"])
        style.map('Toolbutton', background=[('active', theme["widget_bg"])])
        style.configure('TMenubutton', background=theme["select_bg"], foreground=theme["fg"], arrowcolor=theme["fg"], padding=5)
        style.configure('TEntry', fieldbackground=theme["select_bg"], foreground=theme["fg"], insertcolor=theme["fg"], borderwidth=1)
        style.configure('TScale', background=theme["widget_bg"])
        for widget in [self.start_prompt_text, self.human_input_text] + self.get_all_text_widgets_in_settings():
            widget.configure(background=theme["select_bg"], foreground=theme["fg"], insertbackground=theme["fg"], relief="flat", borderwidth=1, font=self.default_font)
        
        # --- FIX: Apply theme to the new GradientButton ---
        self.start_pause_button.set_theme(
            text_color=theme["button_fg"],
            gradient_start=theme["button_accent_bg"][0],
            gradient_end=theme["button_accent_bg"][1],
            disabled_bg=theme["select_bg"],
            disabled_fg=theme["system_color"]
        )
        self.start_pause_button.itemconfig(self.start_pause_button.text_id, font=self.battle_button_font)

        self.chat_display.configure(background=theme["widget_bg"], foreground=theme["fg"], font=self.default_font)
        self.chat_display.tag_config("bot_a_header", foreground=theme["bot_a_color"])
        self.chat_display.tag_config("bot_b_header", foreground=theme["bot_b_color"])
        self.chat_display.tag_config("human_header", foreground=theme["human_color"])
        self.chat_display.tag_config("system_header", foreground=theme["system_color"])
        self.chat_display.tag_config("metrics", font=self.metrics_font)
        self.chat_display.tag_config("bold", font=self.bold_font)
        self.chat_display.tag_config("italic", font=self.italic_font)
        self.chat_display.tag_config("code", font=self.code_font, background=theme["code_bg"], relief="sunken", borderwidth=1, lmargin1=10, lmargin2=10, tabs="1c")
        self.chat_display.tag_config("timestamp_tag", foreground=theme["timestamp_color"], font=self.timestamp_font)

    def on_theme_change(self, theme_name: str):
        self.current_theme_name = theme_name
        self.apply_theme()

    def get_widgets_for_bot(self, bot_id):
        return self.bot_a_settings_frame.widgets if bot_id == 'A' else self.bot_b_settings_frame.widgets

    def get_all_text_widgets_in_settings(self):
        widgets = []
        for frame in [self.bot_a_settings_frame, self.bot_b_settings_frame]:
            for w in frame.winfo_children():
                for tab in w.winfo_children():
                    for child in tab.winfo_children():
                        if isinstance(child, tk.Text): widgets.append(child)
        return widgets

    def update_model_menu(self, bot_id, models, default_selection):
        model_var = self.model_vars[bot_id]
        chat_menu = self.bot_a_chat_frame.widget if bot_id == 'A' else self.bot_b_chat_frame.widget
        chat_menu['menu'].delete(0, 'end')
        if not models: models = [default_selection]
        for model in models:
            chat_menu['menu'].add_command(label=model, command=tk._setit(model_var, model))
        model_var.set(default_selection)

    def update_ui_for_chat_mode(self):
        mode = self.chat_mode_var.get()
        if mode == "Human vs. Bot":
            self.set_frame_widgets_state(self.bot_a_chat_frame, "disabled")
            self.set_frame_widgets_state(self.bot_b_chat_frame, "normal")
            self.set_frame_widgets_state(self.human_input_frame, "normal")
            self.start_pause_button.config(state="disabled")
        else:
            self.set_frame_widgets_state(self.bot_a_chat_frame, "normal")
            self.set_frame_widgets_state(self.bot_b_chat_frame, "normal")
            self.start_pause_button.config(state="normal")
            self.set_frame_widgets_state(self.human_input_frame, "disabled")

    def set_frame_widgets_state(self, frame, state):
        for child in frame.winfo_children():
            widget_class = child.winfo_class()
            if widget_class in ('TButton', 'TMenubutton', 'TEntry', 'Text', 'TScale', 'CollapsiblePane', 'Canvas'):
                if hasattr(child, 'toggle') and state == 'disabled' and not child._is_collapsed: child.toggle()
                child.config(state=state)
            if not isinstance(child, CollapsiblePane) or state == 'normal':
                self.set_frame_widgets_state(child, state)

    def clear_conversation(self):
        if self.is_talking:
            self.is_talking = False
            self.start_pause_button.config(text="START BATTLE")
        self.conversation_history = []
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")
        self.show_main_status("Ready.", foreground=THEMES[self.current_theme_name]["fg"])

    def export_conversation(self):
        if not self.conversation_history:
            self.show_main_status_error("Nothing to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")], title="Save Conversation")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    history_for_json = [{'id': msg.get('id'), 'role': msg.get('role'), 'content': msg.get('content'), 'sender': msg.get('sender'), 'timestamp': msg.get('timestamp').isoformat(), 'metrics': msg.get('metrics')} for msg in self.conversation_history]
                    json.dump(history_for_json, f, indent=2)
                else:
                    for msg in self.conversation_history:
                        f.write(f"--- {msg.get('sender')} ({msg.get('role')}) [{msg.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}] ---\n{msg.get('content', '')}\n\n")
            self.show_main_status(f"Conversation exported successfully.", clear_after=3000)
        except Exception as e:
            self.show_main_status_error(f"Error exporting: {e}")

    def copy_to_clipboard(self, text_to_copy):
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        self.show_main_status("Copied to clipboard.", clear_after=2000)

    def show_connection_error(self, status_label, copy_button, error_msg):
        status_label.config(text=error_msg, foreground=THEMES[self.current_theme_name]["error_fg"])
        copy_button.grid()

    def show_main_status(self, msg, foreground=None, clear_after=0):
        if foreground is None: foreground = THEMES[self.current_theme_name]["fg"]
        self.status_label.config(text=msg, foreground=foreground)
        self.status_copy_button.grid_remove()
        if clear_after > 0: self.after(clear_after, lambda: self.status_label.config(text="Ready.", foreground=THEMES[self.current_theme_name]["fg"]))

    def show_main_status_error(self, error_msg):
        self.status_label.config(text=error_msg, foreground=THEMES[self.current_theme_name]["error_fg"])
        self.status_copy_button.grid()

if __name__ == "__main__":
    app = OllamaChatterApp()
    app.mainloop()

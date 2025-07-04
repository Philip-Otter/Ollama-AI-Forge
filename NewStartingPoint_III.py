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
import difflib

# =====================================================================================
#  AI COLOSSEUM: THEME DEFINITIONS
# =====================================================================================
# Themes have been updated to be more vibrant and competitive.
THEMES = {
    "Cyberpunk Neon": {
        "bg": "#0d0221", "fg": "#f0f0f0", "widget_bg": "#241b47", "select_bg": "#3a2d6b",
        "button_bg": "#f900ff", "button_fg": "#ffffff",
        "champion_a_color": "#00f5d4", "champion_b_color": "#ff0054",
        "system_color": "#8d8d8d", "human_color": "#f5a400",
        "code_bg": "#0a0118", "code_fg": "#f0f0f0", "success_fg": "#00f5d4",
        "error_fg": "#ff0054", "timestamp_color": "#6a6a6a", "border_color": "#5a4d8c",
        "chat_bg": "#140a33", "hp_bar_bg": "#404040", "synergy_bar_fill": "#f5a400"
    },
    "Gladiator Arena": {
        "bg": "#2d2424", "fg": "#e8e8e8", "widget_bg": "#4e4343", "select_bg": "#685c5c",
        "button_bg": "#e5a00d", "button_fg": "#000000",
        "champion_a_color": "#c0392b", "champion_b_color": "#2980b9",
        "system_color": "#a0a0a0", "human_color": "#f1c40f",
        "code_bg": "#1c1717", "code_fg": "#e8e8e8", "success_fg": "#2ecc71",
        "error_fg": "#e74c3c", "timestamp_color": "#888888", "border_color": "#7a6f6f",
        "chat_bg": "#3a3030", "hp_bar_bg": "#505050", "synergy_bar_fill": "#f1c40f"
    },
    "Digital Turf": {
        "bg": "#0a192f", "fg": "#ccd6f6", "widget_bg": "#112240", "select_bg": "#173a6e",
        "button_bg": "#64ffda", "button_fg": "#0a192f",

        "champion_a_color": "#64ffda", "champion_b_color": "#ffca86",
        "system_color": "#8892b0", "human_color": "#ffca86",
        "code_bg": "#020c1b", "code_fg": "#a8b2d1", "success_fg": "#64ffda",
        "error_fg": "#ff79c6", "timestamp_color": "#8892b0", "border_color": "#173a6e",
        "chat_bg": "#0a192f", "hp_bar_bg": "#404040", "synergy_bar_fill": "#64ffda"
    }
}

# =====================================================================================
#  UTILITY FUNCTIONS
# =====================================================================================
def calculate_code_diff(text1, text2):
    """
    Calculates a normalized difference score between two blocks of text.
    Uses SequenceMatcher for a robust line-by-line comparison.
    Returns a value between 0 (identical) and 1 (completely different).
    """
    if not text1 and not text2:
        return 0.0
    if not text1 or not text2:
        return 1.0 # One is empty, the other is not; maximum difference.
        
    sm = difflib.SequenceMatcher(None, text1.splitlines(), text2.splitlines())
    return 1.0 - sm.ratio()

# =====================================================================================
#  CHAT MESSAGE WIDGET
# =====================================================================================
class ChatMessage(ttk.Frame):
    def __init__(self, parent, app, msg_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.msg_data = msg_data
        self.full_content = msg_data.get('content', '')
        self.theme = THEMES[self.app.current_theme_name]
        self.sender = msg_data.get('sender_id', 'System')
        self.is_champion = self.sender.startswith("Champion")
        self.is_human = self.sender == 'Human'

        self.configure(style="ChatFrame.TFrame")
        self.pack(fill="x", padx=10, pady=4)

        # Align messages left for Champions/System, right for Human
        align = "e" if self.is_human else "w"
        self.columnconfigure(0, weight=1 if align == "w" else 0)
        self.columnconfigure(1, weight=1 if align == "e" else 0)

        self._render_message(align)

    def _render_message(self, align):
        bubble_frame = ttk.Frame(self, style="Bubble.TFrame")
        bubble_frame.grid(row=0, column=0 if align == "w" else 1, sticky=f"n{align}", padx=5, pady=2, ipadx=5, ipady=5)

        header_frame = ttk.Frame(bubble_frame, style="Bubble.TFrame")
        header_frame.pack(fill="x", padx=10, pady=(5, 2))

        sender_color_key = {
            "Champion A": "champion_a_color",
            "Champion B": "champion_b_color",
            "Human": "human_color"
        }.get(self.sender, "system_color")
        sender_color = self.theme[sender_color_key]

        ttk.Label(header_frame, text=self.sender, font=self.app.bold_font, foreground=sender_color, style="Bubble.TLabel").pack(side="left")

        vitals_text = ""
        if 'response_time' in self.msg_data:
            vitals_text += f" {self.msg_data['response_time']:.2f}s"
        if 'attack_power' in self.msg_data:
            vitals_text += f" | AP: {self.msg_data['attack_power']}"
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
            self.add_code_block(parent_frame, match.group(2), match.group(1))
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
        self.app.show_toast("Code copied to clipboard!")

# =====================================================================================
#  MAIN APPLICATION CLASS
# =====================================================================================
class AIColosseumApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Colosseum")
        self.geometry("1800x1000")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- State Variables ---
        self.current_theme_name = "Cyberpunk Neon"
        self.clients = {'A': None, 'B': None}
        self.is_competing = False
        self.conversation_history = []
        self.current_code_state = ""
        self.next_champion = 'A'
        self.competition_lock = threading.Lock()
        self.auto_scroll_enabled = True

        # --- Competition Stats ---
        self.champion_stats = {
            'A': {'hp': 100, 'ap': 0},
            'B': {'hp': 100, 'ap': 0}
        }
        self.synergy_score = 0

        self.setup_fonts()
        self.configure(background=THEMES[self.current_theme_name]["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.create_header_and_menu()
        self.create_main_layout()
        self.apply_theme(self.current_theme_name)
        self.show_main_status("info", "Welcome to the Colosseum! Configure your Champions and define the challenge.")

    def on_closing(self):
        self.is_competing = False
        self.destroy()

    def setup_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=11)
        self.bold_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.italic_font = font.Font(family="Segoe UI", size=10, slant="italic")
        self.code_font = font.Font(family="Consolas", size=11)
        self.title_font = font.Font(family="Impact", size=28)
        self.big_button_font = font.Font(family="Segoe UI", size=14, weight="bold")

    def create_header_and_menu(self):
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=(20, 10))
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)

        ttk.Label(header_frame, text="AI COLOSSEUM", font=self.title_font, style='Header.TLabel').grid(row=0, column=0, sticky="w")
        
        # Synergy Meter
        synergy_frame = ttk.Frame(header_frame, style='Header.TFrame')
        synergy_frame.grid(row=0, column=1, sticky="ew", padx=50)
        synergy_frame.columnconfigure(0, weight=1)
        ttk.Label(synergy_frame, text="MATCH SYNERGY", font=self.bold_font, style='Header.TLabel').pack()
        self.synergy_canvas = tk.Canvas(synergy_frame, height=10, bg=THEMES[self.current_theme_name]['hp_bar_bg'], highlightthickness=0)
        self.synergy_canvas.pack(fill="x", pady=(5,0))
        self.synergy_bar = self.synergy_canvas.create_rectangle(0, 0, 0, 10, fill=THEMES[self.current_theme_name]['synergy_bar_fill'], outline="")

        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Match Profile...", command=self.save_profile)
        file_menu.add_command(label="Load Match Profile...", command=self.load_profile)
        file_menu.add_separator()
        file_menu.add_command(label="Export Log...", command=self.export_conversation)
        file_menu.add_command(label="Export Final Code...", command=self.export_final_code)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        session_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Match", menu=session_menu)
        session_menu.add_command(label="Reset Match", command=self.reset_match)
        session_menu.add_command(label="Generate Match Report", command=self.generate_match_report)
        
        # Theme menu in the main menubar
        theme_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Theme", menu=theme_menu)
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        for theme_name in THEMES:
            theme_menu.add_radiobutton(label=theme_name, variable=self.theme_var, command=lambda t=theme_name: self.apply_theme(t))

    def create_main_layout(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Left Pane: Champion A
        champ_a_frame = self._create_champion_panel(main_pane, 'A')
        main_pane.add(champ_a_frame, weight=1)

        # Center Pane: Chat Arena & Controls
        center_frame = self._create_center_arena(main_pane)
        main_pane.add(center_frame, weight=3)

        # Right Pane: Champion B
        champ_b_frame = self._create_champion_panel(main_pane, 'B')
        main_pane.add(champ_b_frame, weight=1)

    def _create_champion_panel(self, parent, champ_id):
        theme = THEMES[self.current_theme_name]
        color = theme[f'champion_{champ_id.lower()}_color']
        
        frame = ttk.Frame(parent, padding=15)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # --- Header ---
        header_label = ttk.Label(frame, text=f"CHAMPION {champ_id}", font=self.bold_font, foreground=color)
        header_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # --- HP Bar ---
        hp_frame = ttk.Frame(frame)
        hp_frame.grid(row=1, column=0, sticky="ew", pady=5)
        hp_frame.columnconfigure(1, weight=1)
        ttk.Label(hp_frame, text="HP", font=self.bold_font).grid(row=0, column=0, padx=(0,5))
        hp_canvas = tk.Canvas(hp_frame, height=20, bg=theme['hp_bar_bg'], highlightthickness=1, highlightbackground=theme['border_color'])
        hp_canvas.grid(row=0, column=1, sticky="ew")
        hp_bar = hp_canvas.create_rectangle(0, 0, 200, 20, fill=color, outline="")
        hp_text = hp_canvas.create_text(100, 11, text="100/100", fill=theme['bg'], font=self.bold_font, anchor="center")
        
        # --- Config Notebook ---
        config_notebook = ttk.Notebook(frame)
        config_notebook.grid(row=2, column=0, sticky="nsew", pady=10)
        
        conn_panel = self._create_bot_config_tab(config_notebook, champ_id)
        config_notebook.add(conn_panel, text="Configuration")

        setattr(self, f'panel_{champ_id}_vars', {
            'header_label': header_label,
            'hp_canvas': hp_canvas, 'hp_bar': hp_bar, 'hp_text': hp_text,
            **getattr(self, f'panel_{champ_id}_vars', {}) # merge with vars from config tab
        })
        return frame

    def _create_bot_config_tab(self, parent, champ_id):
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
        ttk.Label(conn_frame, text="Manual Model:", font=self.italic_font).grid(row=2, column=0, sticky="w", padx=5, pady=(5,0))
        ttk.Entry(conn_frame, textvariable=manual_model_var).grid(row=2, column=1, sticky="ew", padx=5, pady=(5,0))

        connect_button = ttk.Button(conn_frame, text="Connect", command=lambda: self.connect_to_ollama(champ_id))
        connect_button.grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="ew")
        
        status_label = ttk.Label(conn_frame, text="Not Connected", wraplength=250)
        status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5)

        model_frame = ttk.LabelFrame(frame, text="Model & Persona", padding=10)
        model_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0,10))
        model_frame.columnconfigure(1, weight=1)
        model_frame.rowconfigure(2, weight=1)

        model_var = tk.StringVar(value="Select Model")
        model_menu = ttk.OptionMenu(model_frame, model_var, "Connect to Server First")
        model_menu.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(model_frame, text="System Prompt (Persona):").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(5,0))
        system_prompt_text = tk.Text(model_frame, wrap="word", relief="solid", borderwidth=1, height=10)
        system_prompt_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(0,10))
        
        meta_prompt = """
MANDATORY INSTRUCTIONS:
1.  You MUST take the code from the previous turn and critically analyze it.
2.  Your goal is to OUTPERFORM your rival. Introduce superior logic, better structure, or more robust features.
3.  Your response MUST contain the complete, updated, and runnable code block.
4.  Below the code block, provide a brief, bulleted list of your specific changes and improvements.
5.  DO NOT add conversational filler, greetings, or apologies. Stick to the objective. Failure to comply will result in disqualification.
"""
        default_prompts = {
            'A': f"You are a Creative Architect. Your purpose is to enhance the application's user experience, visual appeal, and innovative features. Make the code more intuitive and engaging. {meta_prompt}",
            'B': f"You are a Pragmatic Engineer. Your purpose is to ensure the code is correct, efficient, and robust. Refactor for clarity, add comprehensive error handling, and optimize performance. {meta_prompt}"
        }
        system_prompt_text.insert("1.0", default_prompts[champ_id])
        
        temp_var = tk.DoubleVar(value=0.5)
        ttk.Label(model_frame, text="Creativity (Temp):").grid(row=3, column=0, sticky="w", padx=5)
        temp_scale = ttk.Scale(model_frame, from_=0.0, to=2.0, orient="horizontal", variable=temp_var)
        temp_scale.grid(row=3, column=1, sticky="ew", padx=5)
        
        setattr(self, f'panel_{champ_id}_vars', {
            'host': host_var, 'port': port_var, 'status_label': status_label,
            'manual_model': manual_model_var,
            'model_var': model_var, 'model_menu': model_menu,
            'system_prompt_text': system_prompt_text,
            'temperature': temp_var
        })
        return frame

    def _create_center_arena(self, parent):
        frame = ttk.Frame(parent, padding=0)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # --- Top Control Bar ---
        control_bar = ttk.Frame(frame, padding=10)
        control_bar.grid(row=0, column=0, sticky="ew")
        control_bar.columnconfigure(0, weight=1)
        
        self.start_pause_button = ttk.Button(control_bar, text="BEGIN MATCH", style="Big.TButton", command=self.toggle_competition)
        self.start_pause_button.pack(side="left", expand=True, fill="x", padx=(0, 10))

        delay_frame = ttk.LabelFrame(control_bar, text="Turn Pacing", padding=10)
        delay_frame.pack(side="right")
        self.turn_delay_var = tk.DoubleVar(value=1.0)
        self.delay_label_var = tk.StringVar(value="1.0s")
        delay_scale = ttk.Scale(delay_frame, from_=0, to=5, variable=self.turn_delay_var, orient="horizontal", command=lambda v: self.delay_label_var.set(f"{float(v):.1f}s"))
        delay_scale.pack(side="left")
        ttk.Label(delay_frame, textvariable=self.delay_label_var, width=5).pack(side="left", padx=(5,0))

        # --- Chat Arena ---
        chat_outer_frame = ttk.Frame(frame, style="ChatOuter.TFrame", padding=2)
        chat_outer_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        chat_outer_frame.rowconfigure(0, weight=1)
        chat_outer_frame.columnconfigure(0, weight=1)

        self.chat_canvas = tk.Canvas(chat_outer_frame, highlightthickness=0)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(chat_outer_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_frame = ttk.Frame(self.chat_canvas, style="ChatFrame.TFrame")
        self.chat_canvas_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        
        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", lambda e: self.chat_canvas.itemconfig(self.chat_canvas_window, width=e.width))
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- Bottom Input Area ---
        bottom_frame = ttk.Frame(frame, padding=(0, 10))
        bottom_frame.grid(row=2, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)

        prompt_frame = ttk.LabelFrame(bottom_frame, text="Initial Challenge / Code", padding=10)
        prompt_frame.grid(row=0, column=0, pady=5, sticky="ew")
        prompt_frame.columnconfigure(0, weight=1)
        self.start_prompt_text = tk.Text(prompt_frame, height=6, wrap="word", relief="solid", borderwidth=1)
        self.start_prompt_text.pack(fill="both", expand=True)
        self.start_prompt_text.insert("1.0", "Create a Python script with a GUI using tkinter. The script should be a simple stopwatch with start, stop, and reset buttons.")
        
        input_frame = ttk.LabelFrame(bottom_frame, text="Human Intervention", padding=10)
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        self.human_input_text = tk.Text(input_frame, height=3, wrap="word", relief="solid", borderwidth=1, font=self.default_font)
        self.human_input_text.grid(row=0, column=0, sticky="ew")
        self.human_input_text.bind("<Return>", self.send_human_message)
        send_button = ttk.Button(input_frame, text="Send", command=self.send_human_message)
        send_button.grid(row=0, column=1, sticky="ns", padx=(10,0))
        
        # --- Status Bar ---
        status_frame = ttk.Frame(frame, style="Status.TFrame", padding=5)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(10,0))
        self.status_label = ttk.Label(status_frame, text="", style="Status.TLabel")
        self.status_label.pack(fill="x")

        return frame

    def apply_theme(self, theme_name):
        self.current_theme_name = theme_name
        theme = THEMES[theme_name]
        style = ttk.Style(self)
        style.theme_use('default')

        # --- Global Styles ---
        self.configure(background=theme["bg"])
        style.configure('.', background=theme["bg"], foreground=theme["fg"], borderwidth=0, relief="flat", font=self.default_font)
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TLabelFrame', background=theme["bg"], bordercolor=theme['border_color'], relief="solid", borderwidth=1)
        style.configure('TLabelFrame.Label', background=theme["bg"], foreground=theme["fg"], font=self.bold_font)
        style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"], padding=8, font=self.bold_font, borderwidth=1, relief='raised')
        style.map('TButton', background=[('active', theme["select_bg"])])
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', padding=[10, 5], font=self.bold_font, background=theme['widget_bg'], foreground=theme['fg'])
        style.map('TNotebook.Tab', background=[('selected', theme["select_bg"])], foreground=[('selected', theme["button_fg"])])
        style.configure('TMenubutton', background=theme["button_bg"], foreground=theme["button_fg"])
        style.configure('TEntry', fieldbackground=theme["widget_bg"], foreground=theme["fg"], insertcolor=theme["fg"], bordercolor=theme['border_color'], lightcolor=theme['border_color'], darkcolor=theme['border_color'])

        # --- Custom Styles ---
        style.configure('Big.TButton', font=self.big_button_font, background=theme['button_bg'], foreground=theme['button_fg'], borderwidth=2, relief='raised')
        style.map('Big.TButton', background=[('active', theme['select_bg'])], relief=[('pressed', 'sunken')])
        style.configure('Header.TFrame', background=theme["bg"])
        style.configure('Header.TLabel', background=theme["bg"], foreground=theme["button_bg"])
        style.configure('ChatOuter.TFrame', background=theme['border_color'])
        self.chat_canvas.configure(background=theme["chat_bg"])
        style.configure('ChatFrame.TFrame', background=theme["chat_bg"])
        style.configure('Bubble.TFrame', background=theme['select_bg'], relief='solid', borderwidth=1, bordercolor=theme['border_color'])
        style.configure('Bubble.TLabel', background=theme['select_bg'], foreground=theme['fg'])
        style.configure('Code.TFrame', background=theme['code_bg'], relief='solid', borderwidth=1, bordercolor=theme['border_color'])
        style.configure('Code.TLabel', background=theme['code_bg'], foreground=theme['timestamp_color'])
        style.configure('Code.TButton', font=('Segoe UI', 8))
        style.configure('Status.TFrame', background=theme['widget_bg'])
        style.configure('Status.TLabel', background=theme['widget_bg'])

        # --- Widget-specific Theming ---
        text_widget_bg = theme["widget_bg"]
        for champ_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{champ_id}_vars', None)
            if panel_vars:
                panel_vars['system_prompt_text'].config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_bg"])
                panel_vars['header_label'].config(foreground=theme[f'champion_{champ_id.lower()}_color'])
                panel_vars['hp_canvas'].config(bg=theme['hp_bar_bg'], highlightbackground=theme['border_color'])
                panel_vars['hp_canvas'].itemconfig(panel_vars['hp_bar'], fill=theme[f'champion_{champ_id.lower()}_color'])
                panel_vars['hp_canvas'].itemconfig(panel_vars['hp_text'], fill=theme['bg'])

        self.start_prompt_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_bg"])
        self.human_input_text.config(background=text_widget_bg, fg=theme["fg"], insertbackground=theme["fg"], relief="solid", borderwidth=1, highlightbackground=theme["border_color"], highlightcolor=theme["button_bg"])
        self.synergy_canvas.config(bg=theme['hp_bar_bg'])
        self.synergy_canvas.itemconfig(self.synergy_bar, fill=theme['synergy_bar_fill'])
        
        self.rerender_chat_history()
        self.update_all_champion_stats()

    def _on_mousewheel(self, event):
        # Determine if the scrollbar is at the bottom before scrolling
        top, bottom = self.scrollbar.get()
        is_at_bottom = bottom >= 1.0

        # Scroll the canvas
        if platform.system() == 'Windows': self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else: self.chat_canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

        # Disable auto-scroll if user scrolls up from the bottom
        if is_at_bottom and event.delta > 0:
            self.auto_scroll_enabled = False
        
        # Re-enable auto-scroll if user scrolls back to the bottom
        new_top, new_bottom = self.scrollbar.get()
        if not is_at_bottom and new_bottom >= 1.0:
            self.auto_scroll_enabled = True

    def scroll_to_bottom(self):
        if self.auto_scroll_enabled:
            self.chat_canvas.update_idletasks()
            self.chat_canvas.yview_moveto(1.0)

    def connect_to_ollama(self, champ_id):
        panel_vars = getattr(self, f'panel_{champ_id}_vars')
        host = panel_vars['host'].get()
        port = panel_vars['port'].get()
        full_host = f"http://{host}:{port}"
        self.update_bot_status(champ_id, "info", f"Connecting to {full_host}...")
        threading.Thread(target=self._connect_thread, args=(champ_id, full_host), daemon=True).start()

    def _connect_thread(self, champ_id, host):
        try:
            client = ollama.Client(host=host, timeout=300)
            response = client.list()
            models = [m.get('name') for m in response.get('models', []) if m.get('name')]
            
            if not models:
                panel_vars = getattr(self, f'panel_{champ_id}_vars')
                manual_models_str = panel_vars['manual_model'].get()
                if manual_models_str:
                    models = [m.strip() for m in manual_models_str.split(',') if m.strip()]
                    self.after(0, lambda: self.update_bot_status(champ_id, "success", f"Connected! Using manual models."))
                else:
                    self.after(0, lambda: self.update_bot_status(champ_id, "warning", "Connected, but no models detected."))
            else:
                 self.after(0, lambda: self.update_bot_status(champ_id, "success", f"Connected! Found {len(models)} models."))

            self.clients[champ_id] = client
            self.after(0, lambda: self.update_bot_model_menu(champ_id, models, models[0] if models else "No models found"))

        except Exception as e:
            self.after(0, lambda: self.update_bot_status(champ_id, "error", f"Connection failed."))
            self.after(0, lambda: self.update_bot_model_menu(champ_id, [], "Connection Failed"))
            self.clients[champ_id] = None

    def update_bot_status(self, champ_id, status_type, message):
        panel_vars = getattr(self, f'panel_{champ_id}_vars')
        colors = {"info": "fg", "success": "success_fg", "warning": "human_color", "error": "error_fg"}
        theme_color = THEMES[self.current_theme_name][colors.get(status_type, "fg")]
        panel_vars['status_label'].config(text=message, foreground=theme_color)

    def update_bot_model_menu(self, champ_id, models, default_selection):
        panel_vars = getattr(self, f'panel_{champ_id}_vars')
        var, menu = panel_vars['model_var'], panel_vars['model_menu']
        menu['menu'].delete(0, 'end')
        if not models: models = [default_selection]
        for model in models:
            menu['menu'].add_command(label=model, command=tk._setit(var, model))
        var.set(default_selection)

    def toggle_competition(self):
        self.is_competing = not self.is_competing
        if self.is_competing:
            if not self.clients['A'] or not self.clients['B']:
                self.show_main_status("error", "Both Champions must be connected to begin the match.")
                self.is_competing = False
                return
            
            self.start_pause_button.config(text="PAUSE MATCH")
            
            if not self.conversation_history:
                self.reset_match_state()
                initial_prompt = self.start_prompt_text.get("1.0", "end-1c")
                self.current_code_state = self.extract_code_from_prompt(initial_prompt)
                self.add_message_to_history(role='user', content=initial_prompt, sender_id='System')
            
            self.continue_competition()
        else:
            self.start_pause_button.config(text="RESUME MATCH")
            self.show_main_status("info", "Match paused by user.")

    def continue_competition(self):
        if not self.is_competing or self.competition_lock.locked():
            return

        champ_id = self.next_champion
        panel_vars = getattr(self, f'panel_{champ_id}_vars')
        
        # The prompt now includes the current code state explicitly.
        prompt_content = f"""It is your turn, Champion {champ_id}.
The current state of the code is:
---
{self.current_code_state if self.current_code_state else "No code exists yet. You must create the initial version based on the challenge."}
---
Your persona is: {panel_vars['system_prompt_text'].get("1.0", "end-1c").strip()}
Execute your role on the code above.
"""
        api_history = [{'role': 'user', 'content': prompt_content}]
        
        self.show_main_status("info", f"Champion {self.next_champion} is preparing their move...")
        
        threading.Thread(target=self._get_chat_response_thread, args=(
            champ_id, panel_vars['model_var'].get(),
            panel_vars['temperature'].get(), api_history
        ), daemon=True).start()

    def _get_chat_response_thread(self, champ_id, model, temp, history):
        self.competition_lock.acquire()
        try:
            if not self.is_competing: return
            client = self.clients.get(champ_id)
            if not client:
                self.schedule_finalization(champ_id, True, f"Champion {champ_id} is not connected.")
                return

            options = {'temperature': temp}
            start_time = time.time()
            
            response = client.chat(model=model, messages=history, stream=False, options=options)
            full_content = response['message']['content']
            response_time = time.time() - start_time
            
            self.schedule_finalization(champ_id, False, full_content, response_time)

        except Exception as e:
            self.schedule_finalization(champ_id, True, str(e))
        finally:
            if self.competition_lock.locked():
                self.competition_lock.release()

    def schedule_finalization(self, champ_id, is_error, content, response_time=0):
        delay_ms = int(self.turn_delay_var.get() * 1000)
        self.after(delay_ms, lambda: self.finalize_champion_response(champ_id, is_error, content, response_time))

    def finalize_champion_response(self, champ_id, is_error, content, response_time):
        if not content or not content.strip():
            self.show_main_status("warning", f"Champion {champ_id} returned an empty response. Turn skipped.")
            if self.is_competing:
                self.next_champion = 'B' if champ_id == 'A' else 'A'
                self.after(100, self.continue_competition)
            return

        if is_error:
            self.add_message_to_history(role='system', content=f"Error from Champion {champ_id}: {content}", sender_id='System')
            self.is_competing = False
            self.start_pause_button.config(text="BEGIN MATCH")
            return

        # --- New Logic: Analyze response and update stats ---
        new_code = self.extract_code_from_prompt(content)
        diff_score = calculate_code_diff(self.current_code_state, new_code)
        
        attack_power = int(diff_score * 100)
        damage = int(attack_power * 0.5) # Damage is half the attack power
        
        opponent_id = 'B' if champ_id == 'A' else 'A'
        self.champion_stats[opponent_id]['hp'] = max(0, self.champion_stats[opponent_id]['hp'] - damage)
        self.champion_stats[champ_id]['ap'] = attack_power

        # Update Synergy: reward smaller, constructive changes
        self.synergy_score = min(100, self.synergy_score + (5 - int(diff_score * 5)))

        self.update_all_champion_stats()
        
        self.current_code_state = new_code # Update the canonical code state
        
        msg_data = {
            'role': 'assistant',
            'content': content,
            'sender_id': f"Champion {champ_id}",
            'response_time': response_time,
            'attack_power': attack_power
        }
        self.add_message_to_history(**msg_data)
        
        if self.champion_stats[opponent_id]['hp'] <= 0:
            self.is_competing = False
            self.start_pause_button.config(text="MATCH OVER")
            self.show_main_status("success", f"MATCH OVER! Champion {champ_id} is victorious by knockout!")
            messagebox.showinfo("Match Over", f"Champion {opponent_id} has been defeated!\nChampion {champ_id} wins the match!")
            return

        if self.is_competing:
            self.next_champion = opponent_id
            self.after(100, self.continue_competition)

    def send_human_message(self, event=None):
        text = self.human_input_text.get("1.0", "end-1c").strip()
        if not text: return "break"
        
        self.auto_scroll_enabled = True # Re-enable on send
        self.add_message_to_history(role='user', content=text, sender_id='Human')
        self.human_input_text.delete("1.0", "end")
        
        # Human intervention updates the canonical code state
        new_code_from_human = self.extract_code_from_prompt(text)
        if new_code_from_human:
            self.current_code_state = new_code_from_human
            self.show_main_status("info", "Human intervention has updated the code state.")

        if self.is_competing:
            self.after(100, self.continue_competition)
        return "break"

    def add_message_to_history(self, **msg_data):
        msg_data['timestamp'] = datetime.now()
        self.conversation_history.append(msg_data)
        
        # Don't display the initial system prompt in the chat
        if msg_data['sender_id'] == 'System' and msg_data.get('role') == 'user':
            return

        ChatMessage(self.chat_frame, self, msg_data)
        self.scroll_to_bottom()

    def rerender_chat_history(self):
        for widget in self.chat_frame.winfo_children(): widget.destroy()
        for msg in self.conversation_history:
            if not (msg['sender_id'] == 'System' and msg.get('role') == 'user'):
                ChatMessage(self.chat_frame, self, msg)
        self.scroll_to_bottom()
        
    def reset_match(self):
        if messagebox.askokcancel("Reset Match", "This will end the current match and clear all progress. Are you sure?"):
            self.is_competing = False
            if self.competition_lock.locked(): self.competition_lock.release()
            self.conversation_history = []
            self.rerender_chat_history()
            self.reset_match_state()
            self.show_main_status("info", "Match has been reset. Configure Champions and begin a new match.")
            self.start_pause_button.config(text="BEGIN MATCH")
            
    def reset_match_state(self):
        self.next_champion = 'A'
        self.current_code_state = ""
        self.champion_stats = {'A': {'hp': 100, 'ap': 0}, 'B': {'hp': 100, 'ap': 0}}
        self.synergy_score = 0
        self.update_all_champion_stats()
        
    def update_all_champion_stats(self):
        self.update_champion_stats('A')
        self.update_champion_stats('B')
        self.update_synergy_bar()

    def update_champion_stats(self, champ_id):
        panel_vars = getattr(self, f'panel_{champ_id}_vars')
        stats = self.champion_stats[champ_id]
        hp = stats['hp']
        
        canvas = panel_vars['hp_canvas']
        bar = panel_vars['hp_bar']
        text = panel_vars['hp_text']
        
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1: # Canvas not rendered yet
            self.after(50, lambda: self.update_champion_stats(champ_id))
            return
            
        bar_width = (hp / 100) * canvas_width
        canvas.coords(bar, 0, 0, bar_width, canvas.winfo_height())
        canvas.coords(text, canvas_width / 2, canvas.winfo_height() / 2)
        canvas.itemconfig(text, text=f"{hp}/100")

    def update_synergy_bar(self):
        canvas_width = self.synergy_canvas.winfo_width()
        if canvas_width <= 1:
            self.after(50, self.update_synergy_bar)
            return
        
        bar_width = (self.synergy_score / 100) * canvas_width
        self.synergy_canvas.coords(self.synergy_bar, 0, 0, bar_width, self.synergy_canvas.winfo_height())

    def show_main_status(self, status_type, message):
        colors = {"info": "fg", "success": "success_fg", "warning": "human_color", "error": "error_fg"}
        color_key = colors.get(status_type, "fg")
        theme = THEMES[self.current_theme_name]
        self.status_label.config(text=f" {message}", foreground=theme[color_key])

    def show_toast(self, message):
        try:
            toast = tk.Toplevel(self)
            toast.wm_overrideredirect(True)
            toast.wm_geometry(f"+{self.winfo_x()+self.winfo_width()//2-150}+{self.winfo_y()+self.winfo_height()-100}")
            toast.attributes("-alpha", 0.9)
            theme = THEMES[self.current_theme_name]
            label = tk.Label(toast, text=message, bg=theme['success_fg'], fg=theme['bg'], padx=20, pady=10, font=self.bold_font)
            label.pack()
            toast.after(2500, toast.destroy)
        except tk.TclError: # Can happen if main window is closed
            pass

    def extract_code_from_prompt(self, text):
        code_match = re.search(r"```(?:\w*\n)?(.*?)```", text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        # If no code block, assume the whole text is code if it looks like it
        # This is a simple heuristic
        if any(kw in text for kw in ['def ', 'import ', 'class ', 'public class', 'function(']):
             return text.strip()
        return ""

    def save_profile(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Match Profiles", "*.json")], title="Save Match Profile")
        if not filepath: return
        profile_data = {'theme': self.theme_var.get(), 'challenge_prompt': self.start_prompt_text.get("1.0", "end-1c"), 'champion_a': {}, 'champion_b': {}}
        for champ_id in ['A', 'B']:
            panel_vars = getattr(self, f'panel_{champ_id}_vars')
            profile_data[f'champion_{champ_id.lower()}'] = {
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
        filepath = filedialog.askopenfilename(filetypes=[("Match Profiles", "*.json")], title="Load Match Profile")
        if not filepath: return
        try:
            with open(filepath, 'r') as f: profile_data = json.load(f)
            self.theme_var.set(profile_data.get('theme', 'Cyberpunk Neon'))
            self.apply_theme(self.theme_var.get())
            self.start_prompt_text.delete("1.0", "end")
            self.start_prompt_text.insert("1.0", profile_data.get('challenge_prompt', ''))
            for champ_id_lower in ['champion_a', 'champion_b']:
                champ_id_upper = champ_id_lower[-1].upper()
                bot_data = profile_data.get(champ_id_lower, {})
                panel_vars = getattr(self, f'panel_{champ_id_upper}_vars')
                panel_vars['host'].set(bot_data.get('host', '127.0.0.1'))
                panel_vars['port'].set(bot_data.get('port', '11434'))
                panel_vars['manual_model'].set(bot_data.get('manual_model', ''))
                panel_vars['system_prompt_text'].delete("1.0", "end")
                panel_vars['system_prompt_text'].insert("1.0", bot_data.get('system_prompt', ''))
                panel_vars['temperature'].set(bot_data.get('temperature', 0.7))
                self.clients[champ_id_upper] = None
                self.update_bot_model_menu(champ_id_upper, [bot_data.get('model', 'Connect to Server')], bot_data.get('model', 'Connect to Server'))
                self.update_bot_status(champ_id_upper, "info", "Profile loaded. Please connect.")
            self.show_main_status("success", f"Profile loaded: {os.path.basename(filepath)}")
            self.reset_match()
        except Exception as e: messagebox.showerror("Load Error", f"Failed to load profile: {e}")

    def generate_match_report(self):
        if not self.conversation_history: messagebox.showinfo("Summary", "No match data to analyze."); return
        report = "--- MATCH REPORT ---\n\n"
        stats = {'A': {'count': 0, 'times': [], 'total_ap': 0}, 'B': {'count': 0, 'times': [], 'total_ap': 0}}
        for msg in self.conversation_history:
            if msg['sender_id'] == 'Champion A':
                stats['A']['count'] += 1
                if 'response_time' in msg: stats['A']['times'].append(msg['response_time'])
                if 'attack_power' in msg: stats['A']['total_ap'] += msg['attack_power']
            elif msg['sender_id'] == 'Champion B':
                stats['B']['count'] += 1
                if 'response_time' in msg: stats['B']['times'].append(msg['response_time'])
                if 'attack_power' in msg: stats['B']['total_ap'] += msg['attack_power']
        
        report += f"Total Turns: {stats['A']['count'] + stats['B']['count']}\n"
        report += f"Final Synergy Score: {self.synergy_score}/100\n\n"

        for champ_id in ['A', 'B']:
            s = stats[champ_id]
            panel_vars = getattr(self, f'panel_{champ_id}_vars')
            report += f"Champion {champ_id} ({panel_vars['model_var'].get()}):\n"
            report += f"  - Final HP: {self.champion_stats[champ_id]['hp']}/100\n"
            report += f"  - Turns Taken: {s['count']}\n"
            if s['times']:
                avg_time = sum(s['times']) / len(s['times'])
                report += f"  - Avg. Response Time: {avg_time:.2f}s\n"
            if s['count'] > 0:
                avg_ap = s['total_ap'] / s['count']
                report += f"  - Avg. Attack Power (AP): {avg_ap:.0f}\n\n"
        messagebox.showinfo("Match Report", report, parent=self)
        
    def export_conversation(self):
        if not self.conversation_history: messagebox.showinfo("Export", "There is no log to export."); return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json")], title="Save Match Log")
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    history_for_json = [{'role': m.get('role'), 'content': m.get('content'), 'sender': m.get('sender_id')} for m in self.conversation_history]
                    json.dump(history_for_json, f, indent=2)
                else:
                    for msg in self.conversation_history:
                        f.write(f"--- {msg.get('sender_id')} ({msg.get('role')}) @ {msg['timestamp']} ---\n{msg.get('content', '')}\n\n")
            self.show_toast("Match log exported successfully!")
        except Exception as e: messagebox.showerror("Export Error", f"Failed to save file: {e}")

    def export_final_code(self):
        if not self.current_code_state:
            messagebox.showinfo("Export Code", "No final code has been generated yet.")
            return
        
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")], title="Save Final Code")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.current_code_state)
            self.show_toast("Final code exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save code: {e}")

# =====================================================================================
#  APPLICATION ENTRY POINT
# =====================================================================================
if __name__ == "__main__":
    app = AIColosseumApp()
    app.mainloop()

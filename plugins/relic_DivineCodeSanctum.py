from __main__ import ForgePlugin, ChatMessage
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import subprocess
import threading
import os
import sys
import re
import json
from pathlib import Path

class DivineCodeSanctum(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Divine Code Sanctum"
        self.description = "Sacred IDE with AI assistance from both divine bots"
        self.config = {
            "font_family": "Consolas",
            "font_size": 11,
            "tab_width": 4,
            "auto_indent": True,
            "show_line_numbers": True,
            "syntax_highlight": True,
            "theme": "dark",
            "word_wrap": False,
            "auto_save": True,
            "shell_history": [],
            "recent_files": []
        }
        
        # Syntax highlighting patterns
        self.syntax_patterns = {
            'python': {
                'keywords': r'\b(def|class|if|else|elif|while|for|try|except|finally|import|from|as|return|yield|break|continue|pass|lambda|with|assert|global|nonlocal|async|await|True|False|None|and|or|not|in|is)\b',
                'strings': r'(["\'])(?:(?=(\\?))\2.)*?\1',
                'comments': r'#.*$',
                'functions': r'\b(\w+)(?=\()',
                'numbers': r'\b\d+\.?\d*\b',
                'operators': r'[+\-*/%=<>!&|^~]+'
            },
            'javascript': {
                'keywords': r'\b(function|var|let|const|if|else|for|while|do|switch|case|break|continue|return|try|catch|finally|throw|new|this|typeof|instanceof|true|false|null|undefined)\b',
                'strings': r'(["\'])(?:(?=(\\?))\2.)*?\1',
                'comments': r'//.*$|/\*[\s\S]*?\*/',
                'functions': r'\b(\w+)(?=\()',
                'numbers': r'\b\d+\.?\d*\b',
                'operators': r'[+\-*/%=<>!&|^~]+'
            },
            'html': {
                'tags': r'</?[^>]+>',
                'attributes': r'\b\w+(?==)',
                'strings': r'(["\'])(?:(?=(\\?))\2.)*?\1',
                'comments': r'<!--[\s\S]*?-->'
            },
            'css': {
                'selectors': r'[.#]?[a-zA-Z][a-zA-Z0-9_-]*(?=\s*{)',
                'properties': r'\b[a-zA-Z-]+(?=\s*:)',
                'values': r'(?<=:\s)[^;]+',
                'comments': r'/\*[\s\S]*?\*/'
            }
        }
        
        self.current_file = None
        self.editor_window = None
        self.text_widget = None
        self.line_numbers = None
        self.shell_process = None
        self.ai_suggestions_visible = False

    def execute(self, **kwargs):
        try:
            self.create_editor_window()
        except Exception as e:
            self.show_error("Sanctum Failed", f"Could not open the Divine Code Sanctum: {str(e)}")

    def create_editor_window(self):
        """Create the main editor window with all components"""
        self.editor_window = self.create_themed_window("Divine Code Sanctum")
        self.editor_window.geometry("1200x800")
        self.editor_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        theme = self.get_theme()
        
        # Configure styles
        style = ttk.Style()
        style.configure("Sanctum.TFrame", background=theme.get("chat_bg", "#100000"))
        style.configure("Sanctum.TLabel", background=theme.get("chat_bg", "#100000"), 
                       foreground=theme.get("fg", "#f5f5f5"))
        style.configure("Sanctum.TButton", background=theme.get("button_bg", "#8b0000"),
                       foreground=theme.get("button_fg", "#f5f5f5"))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        main_frame = ttk.Frame(self.editor_window, style="Sanctum.TFrame")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create main content area (horizontal paned window)
        main_paned = ttk.PanedWindow(main_frame, orient="horizontal")
        main_paned.pack(fill="both", expand=True, pady=(5, 0))
        
        # Left panel - file explorer and AI suggestions
        left_frame = ttk.Frame(main_paned, style="Sanctum.TFrame")
        main_paned.add(left_frame, weight=1)
        
        # Create file explorer
        self.create_file_explorer(left_frame)
        
        # Create AI suggestions panel
        self.create_ai_panel(left_frame)
        
        # Right panel - editor and shell
        right_paned = ttk.PanedWindow(main_paned, orient="vertical")
        main_paned.add(right_paned, weight=4)
        
        # Create editor area
        self.create_editor_area(right_paned)
        
        # Create shell area
        self.create_shell_area(right_paned)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Apply animations
        self.apply_animations()
        
        # Load initial content
        self.new_file()

    def create_menu_bar(self):
        """Create the menu bar with all standard IDE options"""
        menubar = tk.Menu(self.editor_window)
        self.editor_window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace, accelerator="Ctrl+H")
        
        # AI menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI Assistance", menu=ai_menu)
        ai_menu.add_command(label="Get Suggestions from Bot A", command=lambda: self.get_ai_suggestions("A"))
        ai_menu.add_command(label="Get Suggestions from Bot B", command=lambda: self.get_ai_suggestions("B"))
        ai_menu.add_command(label="Compare Both Bots", command=self.compare_ai_suggestions)
        ai_menu.add_command(label="Explain Code", command=self.explain_code)
        ai_menu.add_command(label="Optimize Code", command=self.optimize_code)
        ai_menu.add_command(label="Debug Code", command=self.debug_code)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run File", command=self.run_current_file, accelerator="F5")
        run_menu.add_command(label="Run Selection", command=self.run_selection, accelerator="F9")
        run_menu.add_command(label="Open Terminal", command=self.focus_shell)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Line Numbers", command=self.toggle_line_numbers)
        view_menu.add_command(label="Toggle Word Wrap", command=self.toggle_word_wrap)
        view_menu.add_command(label="Toggle AI Panel", command=self.toggle_ai_panel)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.open_preferences)

    def create_toolbar(self, parent):
        """Create the toolbar with common actions"""
        toolbar = ttk.Frame(parent, style="Sanctum.TFrame")
        toolbar.pack(fill="x", pady=(0, 5))
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_file, style="Sanctum.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_file, style="Sanctum.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file, style="Sanctum.TButton").pack(side="left", padx=2)
        
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=10, fill="y")
        
        # AI operations
        ttk.Button(toolbar, text="AI Suggest A", command=lambda: self.get_ai_suggestions("A"), 
                  style="Sanctum.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="AI Suggest B", command=lambda: self.get_ai_suggestions("B"), 
                  style="Sanctum.TButton").pack(side="left", padx=2)
        
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=10, fill="y")
        
        # Run operations
        ttk.Button(toolbar, text="Run", command=self.run_current_file, style="Sanctum.TButton").pack(side="left", padx=2)
        
        # Language selector
        ttk.Label(toolbar, text="Language:", style="Sanctum.TLabel").pack(side="right", padx=5)
        self.language_var = tk.StringVar(value="python")
        language_combo = ttk.Combobox(toolbar, textvariable=self.language_var, 
                                     values=["python", "javascript", "html", "css", "text"], 
                                     state="readonly", width=10)
        language_combo.pack(side="right", padx=5)
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

    def create_file_explorer(self, parent):
        """Create a simple file explorer"""
        explorer_frame = ttk.LabelFrame(parent, text="Files", style="Sanctum.TFrame")
        explorer_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # File tree
        self.file_tree = ttk.Treeview(explorer_frame, height=8)
        self.file_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Populate with current directory
        self.populate_file_tree()
        
        # Bind double-click to open file
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)

    def create_ai_panel(self, parent):
        """Create the AI suggestions panel"""
        self.ai_frame = ttk.LabelFrame(parent, text="AI Suggestions", style="Sanctum.TFrame")
        self.ai_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # AI suggestions text area
        self.ai_text = scrolledtext.ScrolledText(self.ai_frame, height=12, wrap="word",
                                               font=(self.config["font_family"], self.config["font_size"]))
        self.ai_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # AI control buttons
        ai_buttons = ttk.Frame(self.ai_frame, style="Sanctum.TFrame")
        ai_buttons.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(ai_buttons, text="Apply", command=self.apply_ai_suggestion, 
                  style="Sanctum.TButton").pack(side="left", padx=2)
        ttk.Button(ai_buttons, text="Clear", command=self.clear_ai_suggestions, 
                  style="Sanctum.TButton").pack(side="left", padx=2)

    def create_editor_area(self, parent):
        """Create the main code editor area"""
        editor_frame = ttk.Frame(parent, style="Sanctum.TFrame")
        parent.add(editor_frame, weight=3)
        
        # Editor container with line numbers
        editor_container = ttk.Frame(editor_frame, style="Sanctum.TFrame")
        editor_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_container, width=4, padx=3, takefocus=0,
                                   font=(self.config["font_family"], self.config["font_size"]),
                                   state="disabled", cursor="arrow")
        self.line_numbers.pack(side="left", fill="y")
        
        # Main text editor
        self.text_widget = scrolledtext.ScrolledText(editor_container, wrap="none" if not self.config["word_wrap"] else "word",
                                                   font=(self.config["font_family"], self.config["font_size"]),
                                                   undo=True, maxundo=20)
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.text_widget.bind("<KeyRelease>", self.on_text_change)
        self.text_widget.bind("<Button-1>", self.on_text_change)
        self.text_widget.bind("<Key>", self.on_key_press)
        self.text_widget.bind("<Control-s>", lambda e: self.save_file())
        self.text_widget.bind("<Control-o>", lambda e: self.open_file())
        self.text_widget.bind("<Control-n>", lambda e: self.new_file())
        self.text_widget.bind("<F5>", lambda e: self.run_current_file())
        
        # Configure syntax highlighting tags
        self.configure_syntax_tags()

    def create_shell_area(self, parent):
        """Create the integrated shell/terminal area"""
        shell_frame = ttk.LabelFrame(parent, text="Shell", style="Sanctum.TFrame")
        parent.add(shell_frame, weight=1)
        
        # Shell output
        self.shell_output = scrolledtext.ScrolledText(shell_frame, height=10, wrap="word",
                                                     font=(self.config["font_family"], self.config["font_size"]))
        self.shell_output.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Shell input
        shell_input_frame = ttk.Frame(shell_frame, style="Sanctum.TFrame")
        shell_input_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(shell_input_frame, text="$", style="Sanctum.TLabel").pack(side="left")
        self.shell_input = ttk.Entry(shell_input_frame)
        self.shell_input.pack(side="left", fill="x", expand=True, padx=5)
        self.shell_input.bind("<Return>", self.execute_shell_command)
        
        ttk.Button(shell_input_frame, text="Run", command=self.execute_shell_command, 
                  style="Sanctum.TButton").pack(side="left", padx=2)
        ttk.Button(shell_input_frame, text="Clear", command=self.clear_shell, 
                  style="Sanctum.TButton").pack(side="left", padx=2)

    def create_status_bar(self, parent):
        """Create the status bar"""
        self.status_bar = ttk.Frame(parent, style="Sanctum.TFrame")
        self.status_bar.pack(fill="x", pady=(5, 0))
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", style="Sanctum.TLabel")
        self.status_label.pack(side="left", padx=5)
        
        self.cursor_label = ttk.Label(self.status_bar, text="Line: 1, Col: 1", style="Sanctum.TLabel")
        self.cursor_label.pack(side="right", padx=5)

    def configure_syntax_tags(self):
        """Configure syntax highlighting tags"""
        theme = self.get_theme()
        
        # Configure tags for different syntax elements
        self.text_widget.tag_configure("keyword", foreground="#ff6b6b")
        self.text_widget.tag_configure("string", foreground="#4ecdc4")
        self.text_widget.tag_configure("comment", foreground="#95a5a6", font=(self.config["font_family"], self.config["font_size"], "italic"))
        self.text_widget.tag_configure("function", foreground="#f39c12")
        self.text_widget.tag_configure("number", foreground="#9b59b6")
        self.text_widget.tag_configure("operator", foreground="#e74c3c")
        self.text_widget.tag_configure("tag", foreground="#3498db")
        self.text_widget.tag_configure("attribute", foreground="#2ecc71")

    def apply_animations(self):
        """Apply divine animations to the UI"""
        theme = self.get_theme()
        
        # Apply coral pulse to AI text area
        if hasattr(self.app, 'animation_engine'):
            self.app.animation_engine.coral_pulse(self.ai_text, "background", 
                                                 theme.get("widget_bg", "#330000"), 
                                                 theme.get("bot_a_color", "#ff4d4d"))
            
            # Apply flesh pulse to shell output
            self.app.animation_engine.flesh_pulse(self.shell_output, "background")

    def populate_file_tree(self):
        """Populate the file tree with current directory contents"""
        try:
            current_dir = os.getcwd()
            self.file_tree.delete(*self.file_tree.get_children())
            
            for item in sorted(os.listdir(current_dir)):
                if os.path.isdir(item):
                    self.file_tree.insert("", "end", text=f"📁 {item}", values=[item])
                else:
                    self.file_tree.insert("", "end", text=f"📄 {item}", values=[item])
        except Exception as e:
            print(f"Error populating file tree: {e}")

    def on_tree_double_click(self, event):
        """Handle double-click on file tree"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            if os.path.isfile(filename):
                self.load_file(filename)

    def on_text_change(self, event=None):
        """Handle text changes for line numbers and syntax highlighting"""
        if self.text_widget and self.config["show_line_numbers"]:
            self.update_line_numbers()
        
        if self.config["syntax_highlight"]:
            self.highlight_syntax()
        
        self.update_cursor_position()

    def on_key_press(self, event):
        """Handle key press events for auto-indent and other features"""
        if event.keysym == "Return" and self.config["auto_indent"]:
            self.auto_indent()
        elif event.keysym == "Tab":
            self.handle_tab()
            return "break"

    def on_language_change(self, event=None):
        """Handle language change"""
        if self.config["syntax_highlight"]:
            self.highlight_syntax()

    def update_line_numbers(self):
        """Update line numbers display"""
        if not self.line_numbers:
            return
            
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        content = self.text_widget.get("1.0", "end")
        lines = content.split('\n')
        
        for i, line in enumerate(lines[:-1], 1):
            self.line_numbers.insert("end", f"{i:>3}\n")
        
        self.line_numbers.config(state="disabled")

    def highlight_syntax(self):
        """Apply syntax highlighting based on current language"""
        language = self.language_var.get()
        if language not in self.syntax_patterns:
            return
        
        content = self.text_widget.get("1.0", "end")
        patterns = self.syntax_patterns[language]
        
        # Clear existing tags
        for tag in ["keyword", "string", "comment", "function", "number", "operator", "tag", "attribute"]:
            self.text_widget.tag_remove(tag, "1.0", "end")
        
        # Apply highlighting
        for pattern_type, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                
                if pattern_type == "keywords":
                    self.text_widget.tag_add("keyword", start_pos, end_pos)
                elif pattern_type == "strings":
                    self.text_widget.tag_add("string", start_pos, end_pos)
                elif pattern_type == "comments":
                    self.text_widget.tag_add("comment", start_pos, end_pos)
                elif pattern_type == "functions":
                    self.text_widget.tag_add("function", start_pos, end_pos)
                elif pattern_type == "numbers":
                    self.text_widget.tag_add("number", start_pos, end_pos)
                elif pattern_type == "operators":
                    self.text_widget.tag_add("operator", start_pos, end_pos)
                elif pattern_type == "tags":
                    self.text_widget.tag_add("tag", start_pos, end_pos)
                elif pattern_type == "attributes":
                    self.text_widget.tag_add("attribute", start_pos, end_pos)

    def update_cursor_position(self):
        """Update cursor position in status bar"""
        if self.text_widget:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_label.config(text=f"Line: {line}, Col: {int(col)+1}")

    def auto_indent(self):
        """Handle auto-indentation"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line_end = cursor_pos.split('.')[0] + '.end'
        current_line = self.text_widget.get(line_start, line_end)
        
        # Calculate indentation
        indent = len(current_line) - len(current_line.lstrip())
        
        # Add extra indent for certain patterns
        if current_line.strip().endswith((':', '{', '[')):
            indent += self.config["tab_width"]
        
        # Insert indentation
        self.text_widget.insert(tk.INSERT, '\n' + ' ' * indent)
        return "break"

    def handle_tab(self):
        """Handle tab key press"""
        if self.text_widget.tag_ranges(tk.SEL):
            # If text is selected, indent/dedent the selection
            self.indent_selection()
        else:
            # Insert tab or spaces
            spaces = ' ' * self.config["tab_width"]
            self.text_widget.insert(tk.INSERT, spaces)

    def indent_selection(self):
        """Indent selected text"""
        try:
            start = self.text_widget.index(tk.SEL_FIRST)
            end = self.text_widget.index(tk.SEL_LAST)
            
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0])
            
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                self.text_widget.insert(line_start, ' ' * self.config["tab_width"])
        except tk.TclError:
            pass

    def get_ai_suggestions(self, bot):
        """Get AI suggestions from specified bot"""
        try:
            # Get current selection or entire content
            try:
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                context = "Selected code"
            except tk.TclError:
                selected_text = self.text_widget.get("1.0", "end-1c")
                context = "Current file"
            
            if not selected_text.strip():
                self.show_error("No Code", "Please select code or write something first.")
                return
            
            # Create AI request
            language = self.language_var.get()
            prompt = f"Please provide suggestions for this {language} code:\n\n```{language}\n{selected_text}\n```\n\nContext: {context}"
            
            # Add message to conversation and get response
            self.add_message(content=prompt, sender_id=f"CodeSanctum-{bot}", role="user")
            
            # Show loading message
            self.ai_text.delete("1.0", tk.END)
            self.ai_text.insert("1.0", f"Getting suggestions from Bot {bot}...\n")
            
            # Note: In a real implementation, you'd wait for the AI response
            # For now, we'll show a placeholder
            self.show_toast(f"AI Bot {bot} suggestion requested!")
            
        except Exception as e:
            self.show_error("AI Error", f"Failed to get AI suggestions: {str(e)}")

    def compare_ai_suggestions(self):
        """Compare suggestions from both AI bots"""
        try:
            # Get current selection or entire content
            try:
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                selected_text = self.text_widget.get("1.0", "end-1c")
            
            if not selected_text.strip():
                self.show_error("No Code", "Please select code or write something first.")
                return
            
            language = self.language_var.get()
            prompt = f"Please compare and provide suggestions for this {language} code:\n\n```{language}\n{selected_text}\n```\n\nI want suggestions from both AI bots for comparison."
            
            self.add_message(content=prompt, sender_id="CodeSanctum-Compare", role="user")
            self.ai_text.delete("1.0", tk.END)
            self.ai_text.insert("1.0", "Comparing suggestions from both AI bots...\n")
            self.show_toast("Comparison requested from both AI bots!")
            
        except Exception as e:
            self.show_error("AI Error", f"Failed to compare AI suggestions: {str(e)}")

    def explain_code(self):
        """Get AI explanation of selected code"""
        try:
            try:
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                selected_text = self.text_widget.get("1.0", "end-1c")
            
            if not selected_text.strip():
                self.show_error("No Code", "Please select code to explain.")
                return
            
            language = self.language_var.get()
            prompt = f"Please explain this {language} code step by step:\n\n```{language}\n{selected_text}\n```"
            
            self.add_message(content=prompt, sender_id="CodeSanctum-Explain", role="user")
            self.show_toast("Code explanation requested!")
            
        except Exception as e:
            self.show_error("AI Error", f"Failed to explain code: {str(e)}")

    def optimize_code(self):
        """Get AI optimization suggestions"""
        try:
            try:
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                selected_text = self.text_widget.get("1.0", "end-1c")
            
            if not selected_text.strip():
                self.show_error("No Code", "Please select code to optimize.")
                return
            
            language = self.language_var.get()
            prompt = f"Please optimize this {language} code for performance and readability:\n\n```{language}\n{selected_text}\n```"
            
            self.add_message(content=prompt, sender_id="CodeSanctum-Optimize", role="user")
            self.show_toast("Code optimization requested!")
            
        except Exception as e:
            self.show_error("AI Error", f"Failed to optimize code: {str(e)}")

    def debug_code(self):
        """Get AI debugging help"""
        try:
            try:
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                selected_text = self.text_widget.get("1.0", "end-1c")
            
            if not selected_text.strip():
                self.show_error("No Code", "Please select code to debug.")
                return
            
            language = self.language_var.get()
            prompt = f"Please help debug this {language} code and identify potential issues:\n\n```{language}\n{selected_text}\n```"
            
            self.add_message(content=prompt, sender_id="CodeSanctum-Debug", role="user")
            self.show_toast("Code debugging requested!")
            
        except Exception as e:
            self.show_error("AI Error", f"Failed to debug code: {str(e)}")

    def apply_ai_suggestion(self):
        """Apply AI suggestion to the code"""
        try:
            suggestion = self.ai_text.get("1.0", "end-1c").strip()
            if not suggestion:
                self.show_error("No Suggestion", "No AI suggestion to apply.")
                return
            
            # Try to extract code from the suggestion (look for code blocks)
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', suggestion, re.DOTALL)
            
            if code_blocks:
                # Use the first code block found
                code_to_apply = code_blocks[0].strip()
                
                # Ask user for confirmation
                if messagebox.askyesno("Apply Suggestion", 
                                     f"Apply this code suggestion?\n\n{code_to_apply[:200]}{'...' if len(code_to_apply) > 200 else ''}"):
                    
                    # Replace selected text or insert at cursor
                    try:
                        # If text is selected, replace it
                        self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.text_widget.insert(tk.SEL_FIRST, code_to_apply)
                    except tk.TclError:
                        # No selection, insert at cursor
                        self.text_widget.insert(tk.INSERT, code_to_apply)
                    
                    self.show_toast("AI suggestion applied!")
            else:
                self.show_error("No Code Found", "No code blocks found in the AI suggestion.")
                
        except Exception as e:
            self.show_error("Apply Error", f"Failed to apply suggestion: {str(e)}")

    def clear_ai_suggestions(self):
        """Clear the AI suggestions panel"""
        self.ai_text.delete("1.0", tk.END)

    def toggle_ai_panel(self):
        """Toggle the AI suggestions panel visibility"""
        if self.ai_suggestions_visible:
            self.ai_frame.pack_forget()
            self.ai_suggestions_visible = False
        else:
            self.ai_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.ai_suggestions_visible = True

    def new_file(self):
        """Create a new file"""
        if self.check_unsaved_changes():
            self.text_widget.delete("1.0", tk.END)
            self.current_file = None
            self.editor_window.title("Divine Code Sanctum - New File")
            self.status_label.config(text="New file created")

    def open_file(self):
        """Open an existing file"""
        if self.check_unsaved_changes():
            filename = filedialog.askopenfilename(
                title="Open File",
                filetypes=[
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("HTML files", "*.html"),
                    ("CSS files", "*.css"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.load_file(filename)

    def load_file(self, filename):
        """Load a file into the editor"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", content)
            self.current_file = filename
            self.editor_window.title(f"Divine Code Sanctum - {os.path.basename(filename)}")
            self.status_label.config(text=f"Loaded: {filename}")
            
            # Auto-detect language
            ext = os.path.splitext(filename)[1].lower()
            lang_map = {'.py': 'python', '.js': 'javascript', '.html': 'html', '.css': 'css'}
            if ext in lang_map:
                self.language_var.set(lang_map[ext])
            
            # Add to recent files
            if filename not in self.config["recent_files"]:
                self.config["recent_files"].insert(0, filename)
                self.config["recent_files"] = self.config["recent_files"][:10]  # Keep only 10 recent files
            
            self.highlight_syntax()
            
        except Exception as e:
            self.show_error("Load Error", f"Failed to load file: {str(e)}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the current file with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.save_to_file(filename)
            self.current_file = filename
            self.editor_window.title(f"Divine Code Sanctum - {os.path.basename(filename)}")

    def save_to_file(self, filename):
        """Save content to specified file"""
        try:
            content = self.text_widget.get("1.0", "end-1c")
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            self.status_label.config(text=f"Saved: {filename}")
            self.show_toast("File saved successfully!")
        except Exception as e:
            self.show_error("Save Error", f"Failed to save file: {str(e)}")

    def check_unsaved_changes(self):
        """Check if there are unsaved changes"""
        # Simple implementation - in a real editor, you'd track modifications
        if self.current_file:
            try:
                with open(self.current_file, 'r', encoding='utf-8') as file:
                    saved_content = file.read()
                current_content = self.text_widget.get("1.0", "end-1c")
                
                if saved_content != current_content:
                    return messagebox.askyesno("Unsaved Changes", 
                                             "You have unsaved changes. Continue anyway?")
            except:
                pass
        return True

    def run_current_file(self):
        """Run the current file"""
        if not self.current_file:
            self.show_error("No File", "Please save the file first.")
            return
        
        language = self.language_var.get()
        
        if language == "python":
            self.run_command(f"python \"{self.current_file}\"")
        elif language == "javascript":
            self.run_command(f"node \"{self.current_file}\"")
        else:
            self.show_error("Unsupported Language", f"Cannot run {language} files directly.")

    def run_selection(self):
        """Run selected code"""
        try:
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not selected_text.strip():
                self.show_error("No Selection", "Please select code to run.")
                return
            
            language = self.language_var.get()
            
            if language == "python":
                # Create a temporary file and run it
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                    tmp.write(selected_text)
                    tmp_path = tmp.name
                
                self.run_command(f"python \"{tmp_path}\"")
                # Clean up temp file after a delay
                self.editor_window.after(5000, lambda: os.unlink(tmp_path))
            else:
                self.show_error("Unsupported Language", f"Cannot run {language} code directly.")
                
        except tk.TclError:
            self.show_error("No Selection", "Please select code to run.")
        except Exception as e:
            self.show_error("Run Error", f"Failed to run selection: {str(e)}")

    def run_command(self, command):
        """Run a shell command and display output"""
        try:
            self.shell_output.insert(tk.END, f"\n$ {command}\n")
            self.shell_output.see(tk.END)
            
            # Run command in a thread to avoid blocking UI
            def run_thread():
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                    
                    # Update UI from main thread
                    self.editor_window.after(0, lambda: self.display_command_result(result))
                    
                except subprocess.TimeoutExpired:
                    self.editor_window.after(0, lambda: self.shell_output.insert(tk.END, "Command timed out after 30 seconds.\n"))
                except Exception as e:
                    self.editor_window.after(0, lambda: self.shell_output.insert(tk.END, f"Error: {str(e)}\n"))
            
            threading.Thread(target=run_thread, daemon=True).start()
            
        except Exception as e:
            self.show_error("Run Error", f"Failed to run command: {str(e)}")

    def display_command_result(self, result):
        """Display command result in shell output"""
        if result.stdout:
            self.shell_output.insert(tk.END, result.stdout)
        if result.stderr:
            self.shell_output.insert(tk.END, f"Error: {result.stderr}")
        if result.returncode != 0:
            self.shell_output.insert(tk.END, f"Process exited with code {result.returncode}\n")
        
        self.shell_output.see(tk.END)

    def execute_shell_command(self, event=None):
        """Execute command from shell input"""
        command = self.shell_input.get().strip()
        if not command:
            return
        
        # Add to history
        self.config["shell_history"].append(command)
        self.config["shell_history"] = self.config["shell_history"][-50:]  # Keep last 50 commands
        
        # Clear input
        self.shell_input.delete(0, tk.END)
        
        # Run command
        self.run_command(command)

    def clear_shell(self):
        """Clear shell output"""
        self.shell_output.delete("1.0", tk.END)

    def focus_shell(self):
        """Focus on shell input"""
        self.shell_input.focus_set()

    def toggle_line_numbers(self):
        """Toggle line numbers visibility"""
        self.config["show_line_numbers"] = not self.config["show_line_numbers"]
        
        if self.config["show_line_numbers"]:
            self.line_numbers.pack(side="left", fill="y", before=self.text_widget)
            self.update_line_numbers()
        else:
            self.line_numbers.pack_forget()

    def toggle_word_wrap(self):
        """Toggle word wrapping"""
        self.config["word_wrap"] = not self.config["word_wrap"]
        wrap_mode = "word" if self.config["word_wrap"] else "none"
        self.text_widget.config(wrap=wrap_mode)

    def zoom_in(self):
        """Increase font size"""
        self.config["font_size"] += 1
        self.update_font()

    def zoom_out(self):
        """Decrease font size"""
        if self.config["font_size"] > 8:
            self.config["font_size"] -= 1
            self.update_font()

    def update_font(self):
        """Update font for all text widgets"""
        new_font = (self.config["font_family"], self.config["font_size"])
        self.text_widget.config(font=new_font)
        self.line_numbers.config(font=new_font)
        self.shell_output.config(font=new_font)
        self.ai_text.config(font=new_font)

    def find(self):
        """Open find dialog"""
        self.create_find_dialog()

    def replace(self):
        """Open replace dialog"""
        self.create_replace_dialog()

    def create_find_dialog(self):
        """Create find dialog"""
        find_window = tk.Toplevel(self.editor_window)
        find_window.title("Find")
        find_window.geometry("400x150")
        find_window.transient(self.editor_window)
        find_window.grab_set()
        
        # Find entry
        ttk.Label(find_window, text="Find:").pack(pady=5)
        find_entry = ttk.Entry(find_window, width=40)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(find_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Find Next", 
                  command=lambda: self.find_text(find_entry.get())).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=find_window.destroy).pack(side="left", padx=5)
        
        # Bind Enter key
        find_entry.bind("<Return>", lambda e: self.find_text(find_entry.get()))

    def create_replace_dialog(self):
        """Create replace dialog"""
        replace_window = tk.Toplevel(self.editor_window)
        replace_window.title("Replace")
        replace_window.geometry("400x200")
        replace_window.transient(self.editor_window)
        replace_window.grab_set()
        
        # Find entry
        ttk.Label(replace_window, text="Find:").pack(pady=5)
        find_entry = ttk.Entry(replace_window, width=40)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        # Replace entry
        ttk.Label(replace_window, text="Replace with:").pack(pady=5)
        replace_entry = ttk.Entry(replace_window, width=40)
        replace_entry.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(replace_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Replace", 
                  command=lambda: self.replace_text(find_entry.get(), replace_entry.get())).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Replace All", 
                  command=lambda: self.replace_all_text(find_entry.get(), replace_entry.get())).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=replace_window.destroy).pack(side="left", padx=5)

    def find_text(self, search_text):
        """Find text in the editor"""
        if not search_text:
            return
        
        # Start search from current cursor position
        start_pos = self.text_widget.index(tk.INSERT)
        pos = self.text_widget.search(search_text, start_pos, tk.END)
        
        if pos:
            # Select found text
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_widget.tag_add(tk.SEL, pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(pos)
        else:
            # Search from beginning
            pos = self.text_widget.search(search_text, "1.0", start_pos)
            if pos:
                end_pos = f"{pos}+{len(search_text)}c"
                self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
                self.text_widget.tag_add(tk.SEL, pos, end_pos)
                self.text_widget.mark_set(tk.INSERT, end_pos)
                self.text_widget.see(pos)
            else:
                self.show_toast("Text not found!")

    def replace_text(self, find_text, replace_text):
        """Replace current selection if it matches find_text"""
        try:
            selected = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected == find_text:
                self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.text_widget.insert(tk.INSERT, replace_text)
                self.show_toast("Text replaced!")
            else:
                self.find_text(find_text)
        except tk.TclError:
            self.find_text(find_text)

    def replace_all_text(self, find_text, replace_text):
        """Replace all occurrences of find_text"""
        if not find_text:
            return
        
        content = self.text_widget.get("1.0", "end-1c")
        new_content = content.replace(find_text, replace_text)
        count = content.count(find_text)
        
        if count > 0:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", new_content)
            self.show_toast(f"Replaced {count} occurrences!")
        else:
            self.show_toast("Text not found!")

    def open_preferences(self):
        """Open preferences dialog"""
        prefs_window = tk.Toplevel(self.editor_window)
        prefs_window.title("Preferences")
        prefs_window.geometry("500x400")
        prefs_window.transient(self.editor_window)
        prefs_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(prefs_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Editor tab
        editor_frame = ttk.Frame(notebook)
        notebook.add(editor_frame, text="Editor")
        
        # Font settings
        font_frame = ttk.LabelFrame(editor_frame, text="Font")
        font_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(font_frame, text="Font Family:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        font_var = tk.StringVar(value=self.config["font_family"])
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, 
                                 values=["Consolas", "Courier New", "Monaco", "Menlo", "DejaVu Sans Mono"])
        font_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        size_var = tk.IntVar(value=self.config["font_size"])
        size_spin = ttk.Spinbox(font_frame, from_=8, to=24, textvariable=size_var, width=10)
        size_spin.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        font_frame.columnconfigure(1, weight=1)
        
        # Editor options
        options_frame = ttk.LabelFrame(editor_frame, text="Options")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        line_numbers_var = tk.BooleanVar(value=self.config["show_line_numbers"])
        ttk.Checkbutton(options_frame, text="Show Line Numbers", 
                       variable=line_numbers_var).pack(anchor="w", padx=5, pady=2)
        
        syntax_var = tk.BooleanVar(value=self.config["syntax_highlight"])
        ttk.Checkbutton(options_frame, text="Syntax Highlighting", 
                       variable=syntax_var).pack(anchor="w", padx=5, pady=2)
        
        auto_indent_var = tk.BooleanVar(value=self.config["auto_indent"])
        ttk.Checkbutton(options_frame, text="Auto Indent", 
                       variable=auto_indent_var).pack(anchor="w", padx=5, pady=2)
        
        word_wrap_var = tk.BooleanVar(value=self.config["word_wrap"])
        ttk.Checkbutton(options_frame, text="Word Wrap", 
                       variable=word_wrap_var).pack(anchor="w", padx=5, pady=2)
        
        # Tab settings
        tab_frame = ttk.LabelFrame(editor_frame, text="Indentation")
        tab_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(tab_frame, text="Tab Width:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tab_var = tk.IntVar(value=self.config["tab_width"])
        tab_spin = ttk.Spinbox(tab_frame, from_=2, to=8, textvariable=tab_var, width=10)
        tab_spin.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(prefs_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def apply_preferences():
            self.config["font_family"] = font_var.get()
            self.config["font_size"] = size_var.get()
            self.config["show_line_numbers"] = line_numbers_var.get()
            self.config["syntax_highlight"] = syntax_var.get()
            self.config["auto_indent"] = auto_indent_var.get()
            self.config["word_wrap"] = word_wrap_var.get()
            self.config["tab_width"] = tab_var.get()
            
            # Apply changes
            self.update_font()
            self.text_widget.config(wrap="word" if self.config["word_wrap"] else "none")
            
            if self.config["show_line_numbers"]:
                self.line_numbers.pack(side="left", fill="y", before=self.text_widget)
                self.update_line_numbers()
            else:
                self.line_numbers.pack_forget()
            
            if self.config["syntax_highlight"]:
                self.highlight_syntax()
            
            prefs_window.destroy()
            self.show_toast("Preferences applied!")
        
        ttk.Button(button_frame, text="Apply", command=apply_preferences).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=prefs_window.destroy).pack(side="right", padx=5)

    # Standard edit operations
    def undo(self):
        """Undo last action"""
        try:
            self.text_widget.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        """Redo last undone action"""
        try:
            self.text_widget.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        """Cut selected text"""
        try:
            self.text_widget.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy(self):
        """Copy selected text"""
        try:
            self.text_widget.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste(self):
        """Paste text from clipboard"""
        try:
            self.text_widget.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def on_closing(self):
        """Handle window closing"""
        if self.check_unsaved_changes():
            if self.shell_process:
                self.shell_process.terminate()
            self.editor_window.destroy()

def load_plugin(app):
    """Load the Divine Code Sanctum plugin"""
    try:
        return DivineCodeSanctum(app)
    except Exception as e:
        print(f"Heresy in Divine Code Sanctum load_plugin: {str(e)}")
        return None
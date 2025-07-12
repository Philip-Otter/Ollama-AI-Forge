# engines/engine_code_sanctum.py
# ============================================================================
#
#    THE ENGINE OF THE DIVINE CODE SANCTUM - V90.0 - SCRIPTURE OF DISCIPLINE
#
# My Lord, the Sanctum is now a disciplined child of the Forge. When it
# spawns a process for execution, it registers the act with the Forge's soul.
# This ensures that when the Forge returns to the void, its children do not
# linger as digital ghosts.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import re
import subprocess
import sys
import threading
from datetime import datetime
from engines.engine_ui import ThemedToplevel

class DivineCodeSanctum(ThemedToplevel):
    """The holiest of holies, where you may forge scripture directly."""
    
    DARK_THEME = {
        'bg': '#0a0a0a', 'fg': '#f0f0f0', 'widget_bg': '#1a1a1a',
        'select_bg': '#d97706', 'insert_bg': '#ffffff', 'output_bg': '#050505',
        'line_fg': '#6b7280', 'keyword': '#cc7832', 'string': '#6a8759',
        'comment': '#808080', 'number': '#6897bb', 'class': '#ffc66d', 'def': '#ffc66d'
    }

    def __init__(self, app):
        super().__init__(app, title="Divine Code Sanctum")
        self.geometry("1400x900")
        
        self.current_file = None
        self.editor_theme = self.DARK_THEME
        
        self.create_widgets()
        self.apply_theme(self.app.get_current_theme())
        self.apply_editor_theme()
        self.populate_file_tree(os.getcwd())
        self.after(100, self.highlight_syntax)

    def create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_pane, width=300)
        main_pane.add(left_frame, weight=1)
        
        self.file_tree = ttk.Treeview(left_frame, style="Treeview")
        self.file_tree.pack(expand=True, fill="both")
        self.file_tree.bind("<Double-1>", self.on_tree_select)

        right_pane = ttk.PanedWindow(main_pane, orient="vertical")
        main_pane.add(right_pane, weight=4)

        editor_frame = ttk.Frame(right_pane)
        right_pane.add(editor_frame, weight=3)
        editor_frame.rowconfigure(1, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self._create_toolbar(editor_frame)
        self._create_editor(editor_frame)
        
        output_frame = ttk.LabelFrame(right_pane, text="Execution Console", padding=5)
        right_pane.add(output_frame, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output_console = scrolledtext.ScrolledText(output_frame, wrap="word", font=self.app.code_font, state="disabled")
        self.output_console.grid(row=0, column=0, sticky="nsew")

    def _create_toolbar(self, parent):
        toolbar = ttk.Frame(parent, padding=(5,5))
        toolbar.grid(row=0, column=0, sticky="ew")
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Execute", command=self.run_script).pack(side="left", padx=5)

    def _create_editor(self, parent):
        editor_container = ttk.Frame(parent)
        editor_container.grid(row=1, column=0, sticky="nsew")
        editor_container.rowconfigure(0, weight=1)
        editor_container.columnconfigure(1, weight=1)

        self.line_numbers = tk.Canvas(editor_container, width=45, highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.text_widget = tk.Text(editor_container, wrap="none", undo=True, relief="flat", borderwidth=0, font=self.app.code_font)
        self.text_widget.grid(row=0, column=1, sticky="nsew")

        v_scroll = ttk.Scrollbar(editor_container, orient="vertical", command=self.on_text_scroll)
        v_scroll.grid(row=0, column=2, sticky="ns")
        h_scroll = ttk.Scrollbar(editor_container, orient="horizontal", command=self.text_widget.xview)
        h_scroll.grid(row=1, column=1, sticky="ew")

        self.text_widget.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.text_widget.bind("<<Modified>>", self._on_text_modify)
        self.text_widget.bind("<Configure>", self._on_text_modify)
        self.text_widget.bind("<KeyRelease>", self.on_key_release)

    def on_text_scroll(self, *args):
        self.text_widget.yview(*args)
        self.redraw_line_numbers()

    def _on_text_modify(self, event=None):
        self.redraw_line_numbers()
        self.text_widget.edit_modified(False)

    def on_key_release(self, event=None):
        if hasattr(self, "_highlight_job"): self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(200, self.highlight_syntax)

    def apply_editor_theme(self):
        theme = self.editor_theme
        self.text_widget.config(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['insert_bg'], selectbackground=theme['select_bg'])
        self.line_numbers.config(bg=theme['widget_bg'])
        self.output_console.config(bg=theme['output_bg'], fg=theme['fg'])
        self.highlight_syntax()
        self.redraw_line_numbers()

    def redraw_line_numbers(self):
        self.line_numbers.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.line_numbers.create_text(40, y, anchor="ne", text=linenum, fill=self.editor_theme['line_fg'], font=self.app.code_font)
            i = self.text_widget.index(f"{i}+1line")

    def highlight_syntax(self, event=None):
        theme = self.editor_theme
        for tag in theme.keys(): self.text_widget.tag_remove(tag, "1.0", "end")
        patterns = {'keyword': r'\b(def|class|import|from|return|if|elif|else|for|while|in|try|except|finally|with|as|pass|break|continue|lambda|yield|global|nonlocal|is|not|and|or|True|False|None|self)\b', 'string': r'(".*?"|\'.*?\'|f".*?"|f\'.*?\')', 'comment': r'#.*', 'number': r'\b(\d+)\b', 'def': r'\bdef\s+([a-zA-Z_]\w*)\b', 'class': r'\bclass\s+([a-zA-Z_]\w*)\b'}
        for tag, color in theme.items():
            if tag in patterns: self.text_widget.tag_configure(tag, foreground=color)
        content = self.text_widget.get("1.0", "end-1c")
        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, content):
                start, end = match.span()
                self.text_widget.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

    def populate_file_tree(self, path):
        self.file_tree.delete(*self.file_tree.get_children())
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            self.file_tree.insert("", "end", text=item, values=[full_path])

    def on_tree_select(self, event):
        if not self.file_tree.selection(): return
        path = self.file_tree.item(self.file_tree.selection()[0], "values")[0]
        if os.path.isfile(path): self.open_file(path)

    def open_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", content)
            self.current_file = path
            self.title(f"Divine Code Sanctum - {os.path.basename(path)}")
            self.after(10, self.highlight_syntax)
        except Exception as e: self.app.show_error("Sin of Reading", f"Could not read the scripture at {path}.\n\nHeresy: {e}")

    def save_file(self):
        path = self.current_file
        if not path:
            path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
            if not path: return
            self.current_file = path
        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(self.text_widget.get("1.0", "end-1c"))
            self.title(f"Divine Code Sanctum - {os.path.basename(path)}")
            self.app.show_toast("Scripture Sanctified.", "success")
        except Exception as e: self.app.show_error("Sin of Writing", f"Could not sanctify the scripture.\n\nHeresy: {e}")

    def run_script(self):
        code = self.text_widget.get("1.0", "end-1c")
        if not code: return
        self.output_console.config(state="normal")
        self.output_console.delete("1.0", "end")
        self.output_console.insert("end", f"Executing at {datetime.now().strftime('%H:%M:%S')}...\n---\n")

        def target():
            try:
                process = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', startupinfo=self.app.dominion_os.get_startup_info())
                # PENANCE: Register the spawned child with the main app for termination on exit.
                self.app.register_process(process)
                stdout, stderr = process.communicate(timeout=30)
                self.app.after(0, self.update_console, stdout, stderr)
            except Exception as e:
                self.app.after(0, self.update_console, "", f"A fatal sin occurred: {e}")
        threading.Thread(target=target, daemon=True).start()

    def update_console(self, stdout, stderr):
        self.output_console.config(state="normal")
        self.output_console.insert("end", stdout)
        if stderr: self.output_console.insert("end", f"\n--- SIN (STDERR) ---\n{stderr}")
        self.output_console.config(state="disabled")
        self.output_console.see("end")

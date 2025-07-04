import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import os
import glob
import re
import random
import ast
import keyword
from __main__ import ForgePlugin

class ForgeConsolePlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "NeonSmith's CyberForge"
        self.description = "A cyberpunk interface to forge, manage, and debug plugins in the neon grid."

    def execute(self, **kwargs):
        try:
            CyberAdminWindow(self.app)
        except Exception as e:
            messagebox.showerror("CyberForge Error", f"Grid Failure: {str(e)}", parent=self.app)

class CyberAdminWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.theme = app.get_current_theme()
        self.plugin_folder = app.plugin_manager.plugin_folder
        self.title("NeonSmith's CyberForge - Grid Control")
        self.geometry("1280x720")
        self.configure(bg=self.theme["bg"])
        self.current_file = None
        self.plugin_metadata = {}
        
        self.setup_fonts()
        self.setup_styles()
        self.create_widgets()
        self.load_plugin_list()
        self.apply_animations()
        self.update_idletasks()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_fonts(self):
        try:
            self.neon_font = font.Font(family="Courier New", size=12, weight="bold")
            self.code_font = font.Font(family="Consolas", size=10)
            self.header_font = font.Font(family="Impact", size=28)
            self.meta_font = font.Font(family="Courier New", size=10)
        except Exception as e:
            self.status_label.config(text=f"Error setting fonts: {str(e)}", foreground=self.theme["error_fg"])

    def setup_styles(self):
        try:
            style = ttk.Style()
            style.configure("Cyber.TFrame", background=self.theme["bg"])
            style.configure("Header.TLabel", background=self.theme["bg"], foreground=self.theme["button_accent_bg"][0])
            style.configure("Neon.TButton", background=self.theme["button_bg"], foreground=self.theme["button_fg"], 
                           font=self.neon_font, padding=6, borderwidth=2, relief="flat")
            style.map("Neon.TButton", background=[('active', self.theme["select_bg"])], 
                     relief=[('pressed', 'sunken')])
            style.configure("Status.TLabel", foreground=self.theme["success_fg"], background=self.theme["bg"], 
                           font=self.neon_font, wraplength=800)
        except Exception as e:
            self.status_label.config(text=f"Error setting styles: {str(e)}", foreground=self.theme["error_fg"])

    def create_widgets(self):
        try:
            main_frame = ttk.Frame(self, padding=10, style="Cyber.TFrame")
            main_frame.pack(fill="both", expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame, style="Cyber.TFrame")
            header_frame.pack(fill="x", pady=(0, 10))
            self.header_label = ttk.Label(header_frame, text="NEONSMITH'S CYBERFORGE", font=self.header_font, 
                                        style="Header.TLabel", wraplength=1200, justify="left")
            self.header_label.pack(anchor="w")
            ttk.Label(header_frame, text="Forge Plugins. Debug the Matrix. Rule the Grid.", 
                     font=self.neon_font, foreground=self.theme["bot_a_color"], wraplength=1200).pack(anchor="w")

            # Content layout
            content_frame = ttk.Frame(main_frame, style="Cyber.TFrame")
            content_frame.pack(fill="both", expand=True)
            content_frame.columnconfigure(0, weight=1)
            content_frame.columnconfigure(1, weight=2)
            content_frame.rowconfigure(0, weight=1)

            # Left panel (plugin list and controls)
            left_frame = ttk.Frame(content_frame, padding=5, style="Cyber.TFrame")
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            left_frame.rowconfigure(1, weight=1)
            left_frame.columnconfigure(0, weight=1)

            ttk.Label(left_frame, text="Plugin Matrix", font=self.neon_font, 
                     foreground=self.theme["bot_b_color"], wraplength=250).grid(row=0, column=0, columnspan=2, sticky="w")
            
            self.plugin_listbox = tk.Listbox(left_frame, bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                           selectbackground=self.theme["select_bg"], relief="flat", 
                                           borderwidth=2, font=self.neon_font, height=20, highlightthickness=1, 
                                           highlightcolor=self.theme["border_color"])
            self.plugin_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
            self.plugin_listbox.bind("<<ListboxSelect>>", self.on_plugin_select)

            button_frame = ttk.Frame(left_frame, style="Cyber.TFrame")
            button_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)

            ttk.Button(button_frame, text="Forge Module", style="Neon.TButton", 
                      command=self.prepare_new_plugin).grid(row=0, column=0, sticky="ew", padx=(0, 3))
            
            self.rename_button = ttk.Button(button_frame, text="Rewire Name", style="Neon.TButton", 
                                          command=self.rename_plugin, state="disabled")
            self.rename_button.grid(row=0, column=1, sticky="ew", padx=3)
            
            self.remove_button = ttk.Button(button_frame, text="Obliterate", style="Neon.TButton", 
                                          command=self.remove_plugin, state="disabled")
            self.remove_button.grid(row=0, column=2, sticky="ew", padx=(3, 0))

            ttk.Button(button_frame, text="Debug Grid", style="Neon.TButton", 
                      command=self.debug_plugins).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))

            # Right panel (editor and metadata)
            right_frame = ttk.Frame(content_frame, padding=5, style="Cyber.TFrame")
            right_frame.grid(row=0, column=1, sticky="nsew")
            right_frame.rowconfigure(2, weight=1)
            right_frame.columnconfigure(0, weight=1)

            # Metadata section
            meta_frame = ttk.Frame(right_frame, style="Cyber.TFrame")
            meta_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
            meta_frame.columnconfigure(1, weight=1)

            ttk.Label(meta_frame, text="Plugin Metadata", font=self.neon_font, 
                     foreground=self.theme["bot_b_color"], wraplength=500).grid(row=0, column=0, columnspan=2, sticky="w")
            
            ttk.Label(meta_frame, text="Name:", font=self.meta_font, 
                     foreground=self.theme["fg"]).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.name_var = tk.StringVar()
            self.name_entry = ttk.Entry(meta_frame, textvariable=self.name_var, font=self.meta_font)
            self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

            ttk.Label(meta_frame, text="Description:", font=self.meta_font, 
                     foreground=self.theme["fg"]).grid(row=2, column=0, sticky="w", padx=5, pady=2)
            self.desc_text = tk.Text(meta_frame, wrap="word", height=3, 
                                    bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                    font=self.meta_font, relief="flat", borderwidth=2, 
                                    insertbackground=self.theme["fg"], highlightthickness=1, 
                                    highlightcolor=self.theme["border_color"], undo=True)
            self.desc_text.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

            self.meta_save_button = ttk.Button(meta_frame, text="Commit Metadata", style="Neon.TButton", 
                                             command=self.save_metadata, state="disabled")
            self.meta_save_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

            # Editor section
            editor_header = ttk.Frame(right_frame, style="Cyber.TFrame")
            editor_header.grid(row=1, column=0, sticky="ew")
            self.filename_label = ttk.Label(editor_header, text="Select a module to hack or forge a new one", 
                                          font=self.neon_font, foreground=self.theme["bot_a_color"], wraplength=600)
            self.filename_label.pack(side="left")
            self.save_button = ttk.Button(editor_header, text="Commit to Grid", style="Neon.TButton", 
                                        command=self.save_plugin_code)
            
            self.status_label = ttk.Label(right_frame, text="", style="Status.TLabel")
            self.status_label.grid(row=3, column=0, sticky="w", pady=5)

            # Code editor with line numbers
            editor_frame = ttk.Frame(right_frame, style="Cyber.TFrame")
            editor_frame.grid(row=2, column=0, sticky="nsew")
            editor_frame.columnconfigure(1, weight=1)
            editor_frame.rowconfigure(0, weight=1)

            self.line_numbers = tk.Text(editor_frame, width=4, bg=self.theme["code_bg"], fg=self.theme["fg"], 
                                       font=self.code_font, relief="flat", borderwidth=0, highlightthickness=0)
            self.line_numbers.grid(row=0, column=0, sticky="ns")
            self.line_numbers.config(state="disabled")

            self.code_text = tk.Text(editor_frame, wrap="none", height=20, 
                                    bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                    font=self.code_font, relief="flat", borderwidth=2, 
                                    insertbackground=self.theme["fg"], highlightthickness=1, 
                                    highlightcolor=self.theme["border_color"], undo=True, maxundo=-1)
            self.code_text.grid(row=0, column=1, sticky="nsew")
            self.code_text.bind("<KeyRelease>", self.on_code_key_release)
            self.code_text.bind("<Control-s>", lambda e: self.save_plugin_code())
            self.code_text.bind("<Control-f>", lambda e: self.open_find_replace_dialog())
            self.code_text.bind("<Tab>", self.handle_tab)
            self.code_text.bind("<Return>", self.handle_return)
            self.code_text.bind("<Key>", self.update_line_numbers)
            self.setup_syntax_highlighting()
            self.setup_code_completion()
        except Exception as e:
            self.status_label.config(text=f"Error creating widgets: {str(e)}", foreground=self.theme["error_fg"])

    def setup_syntax_highlighting(self):
        try:
            self.code_text.tag_configure("keyword", foreground="#FF00FF")
            self.code_text.tag_configure("string", foreground="#00FFFF")
            self.code_text.tag_configure("comment", foreground="#00FF00")
            self.code_text.tag_configure("function", foreground="#FFFF00")
            self.code_text.tag_configure("class", foreground="#FFAA00")
            self.code_text.bind("<KeyRelease>", self.on_code_key_release)
        except Exception as e:
            self.status_label.config(text=f"Error setting up syntax highlighting: {str(e)}", foreground=self.theme["error_fg"])

    def highlight_syntax(self):
        try:
            code = self.code_text.get("1.0", "end-1c")
            self.code_text.tag_remove("keyword", "1.0", "end")
            self.code_text.tag_remove("string", "1.0", "end")
            self.code_text.tag_remove("comment", "1.0", "end")
            self.code_text.tag_remove("function", "1.0", "end")
            self.code_text.tag_remove("class", "1.0", "end")

            tokens = self.tokenize_code(code)
            for token_type, token_text, start, end in tokens:
                self.code_text.tag_add(token_type, start, end)
        except Exception as e:
            self.status_label.config(text=f"Error in syntax highlighting: {str(e)}", foreground=self.theme["error_fg"])

    def tokenize_code(self, code):
        tokens = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in keyword.kwlist:
                    tokens.append(("keyword", node.id, f"{node.lineno}.{node.col_offset}", 
                                 f"{node.lineno}.{node.col_offset + len(node.id)}"))
                elif isinstance(node, ast.Str):
                    tokens.append(("string", node.s, f"{node.lineno}.{node.col_offset}", 
                                 f"{node.lineno}.{node.col_offset + len(repr(node.s))}"))
                elif isinstance(node, ast.FunctionDef):
                    tokens.append(("function", node.name, f"{node.lineno}.{node.col_offset}", 
                                 f"{node.lineno}.{node.col_offset + len(node.name)}"))
                elif isinstance(node, ast.ClassDef):
                    tokens.append(("class", node.name, f"{node.lineno}.{node.col_offset}", 
                                 f"{node.lineno}.{node.col_offset + len(node.name)}"))
                elif hasattr(ast, 'Comment') and isinstance(node, ast.Comment):
                    tokens.append(("comment", node.value, f"{node.lineno}.{node.col_offset}", 
                                 f"{node.lineno}.{node.col_offset + len(node.value)}"))
        except:
            pass
        return tokens

    def setup_code_completion(self):
        try:
            self.completion_list = keyword.kwlist + ['def', 'class', 'import', 'from', 'self', 'app']
            self.code_text.bind("<Control-space>", self.show_completion_suggestions)
        except Exception as e:
            self.status_label.config(text=f"Error setting up code completion: {str(e)}", foreground=self.theme["error_fg"])

    def show_completion_suggestions(self, event):
        try:
            cursor = self.code_text.index("insert")
            line, col = map(int, cursor.split('.'))
            line_text = self.code_text.get(f"{line}.0", f"{line}.{col}")
            word = line_text.split()[-1] if line_text.split() else ""
            
            matches = [w for w in self.completion_list if w.startswith(word)]
            if not matches:
                return "break"

            suggestion_window = tk.Toplevel(self)
            suggestion_window.wm_overrideredirect(True)
            x = self.code_text.winfo_rootx() + col * 8
            y = self.code_text.winfo_rooty() + line * 20
            suggestion_window.geometry(f"+{x}+{y}")
            
            listbox = tk.Listbox(suggestion_window, bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                selectbackground=self.theme["select_bg"], font=self.code_font)
            listbox.pack()
            for match in matches:
                listbox.insert("end", match)
            
            def on_select(event):
                selected = listbox.get(listbox.curselection())
                self.code_text.delete(f"{line}.{col - len(word)}", f"{line}.{col}")
                self.code_text.insert(f"{line}.{col - len(word)}", selected)
                suggestion_window.destroy()
                self.update_line_numbers()
            
            listbox.bind("<Return>", on_select)
            listbox.bind("<Double-1>", on_select)
            listbox.bind("<Escape>", lambda e: suggestion_window.destroy())
            listbox.focus_set()
            return "break"
        except Exception as e:
            self.status_label.config(text=f"Error in code completion: {str(e)}", foreground=self.theme["error_fg"])
            return "break"

    def update_line_numbers(self, event=None):
        try:
            self.line_numbers.config(state="normal")
            self.line_numbers.delete("1.0", "end")
            line_count = int(self.code_text.index("end-1c").split('.')[0])
            self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, line_count + 1)))
            self.line_numbers.config(state="disabled")
            self.highlight_syntax()
        except Exception as e:
            self.status_label.config(text=f"Error updating line numbers: {str(e)}", foreground=self.theme["error_fg"])

    def handle_tab(self, event):
        try:
            self.code_text.insert("insert", "    ")
            return "break"
        except Exception as e:
            self.status_label.config(text=f"Error handling tab: {str(e)}", foreground=self.theme["error_fg"])
            return "break"

    def handle_return(self, event):
        try:
            cursor = self.code_text.index("insert")
            line, col = map(int, cursor.split('.'))
            current_line = self.code_text.get(f"{line}.0", f"{line}.end")
            indent = len(current_line) - len(current_line.lstrip())
            if current_line.rstrip().endswith(":"):
                indent += 4
            self.code_text.insert("insert", "\n" + " " * indent)
            return "break"
        except Exception as e:
            self.status_label.config(text=f"Error handling return: {str(e)}", foreground=self.theme["error_fg"])
            return "break"

    def on_code_key_release(self, event=None):
        try:
            self.update_line_numbers()
            self.highlight_syntax()
        except Exception as e:
            self.status_label.config(text=f"Error on key release: {str(e)}", foreground=self.theme["error_fg"])

    def open_find_replace_dialog(self):
        try:
            dialog = tk.Toplevel(self)
            dialog.title("Find and Replace")
            dialog.geometry("400x200")
            dialog.configure(bg=self.theme["bg"])
            dialog.transient(self)
            dialog.grab_set()

            ttk.Label(dialog, text="Find:", font=self.neon_font, foreground=self.theme["fg"]).pack(pady=5)
            find_entry = ttk.Entry(dialog, font=self.neon_font)
            find_entry.pack(fill="x", padx=5)

            ttk.Label(dialog, text="Replace:", font=self.neon_font, foreground=self.theme["fg"]).pack(pady=5)
            replace_entry = ttk.Entry(dialog, font=self.neon_font)
            replace_entry.pack(fill="x", padx=5)

            def find_next():
                search_term = find_entry.get()
                if not search_term:
                    return
                self.code_text.tag_remove("search", "1.0", "end")
                start_pos = self.code_text.index("insert")
                pos = self.code_text.search(search_term, start_pos, stopindex="end")
                if not pos:
                    pos = self.code_text.search(search_term, "1.0", stopindex="end")
                if pos:
                    end_pos = f"{pos}+{len(search_term)}c"
                    self.code_text.tag_add("search", pos, end_pos)
                    self.code_text.tag_configure("search", background=self.theme["select_bg"])
                    self.code_text.see(pos)
                    self.code_text.mark_set("insert", pos)

            def replace():
                search_term = find_entry.get()
                replace_term = replace_entry.get()
                if not search_term:
                    return
                pos = self.code_text.search(search_term, "1.0", stopindex="end")
                if pos:
                    end_pos = f"{pos}+{len(search_term)}c"
                    self.code_text.delete(pos, end_pos)
                    self.code_text.insert(pos, replace_term)
                    self.update_line_numbers()

            button_frame = ttk.Frame(dialog, style="Cyber.TFrame")
            button_frame.pack(fill="x", pady=10)
            ttk.Button(button_frame, text="Find Next", style="Neon.TButton", command=find_next).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Replace", style="Neon.TButton", command=replace).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Close", style="Neon.TButton", command=dialog.destroy).pack(side="right", padx=5)
        except Exception as e:
            self.status_label.config(text=f"Error in find/replace: {str(e)}", foreground=self.theme["error_fg"])

    def animate_glitch(self):
        try:
            if not self.winfo_exists(): return
            original_text = "NEONSMITH'S CYBERFORGE"
            glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            def glitch_step():
                if not self.winfo_exists(): return
                text = list(original_text)
                for _ in range(3):
                    idx = random.randint(0, len(text)-1)
                    text[idx] = random.choice(glitch_chars)
                self.header_label.config(text=''.join(text))
                self.after(50, lambda: self.header_label.config(text=original_text))
                self.after(2000, glitch_step)
            self.after(1000, glitch_step)
        except Exception as e:
            self.status_label.config(text=f"Error in glitch animation: {str(e)}", foreground=self.theme["error_fg"])

    def apply_animations(self):
        try:
            animation_details = self.theme.get("animation", {})
            if animation_details.get("type") == "scanline":
                for widget in [self, self.plugin_listbox, self.code_text, self.desc_text]:
                    self.app.animation_engine.scanline_in(widget, bg_color=self.theme["bg"], 
                                                        scan_color=animation_details.get("color", "#FFFFFF"), 
                                                        duration=400)
        except Exception as e:
            self.status_label.config(text=f"Error applying animations: {str(e)}", foreground=self.theme["error_fg"])

    def load_plugin_list(self):
        try:
            self.plugin_listbox.delete(0, "end")
            protected_files = ["forge_console_plugin.py", "example_word_counter.py"]
            for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
                filename = os.path.basename(filepath)
                if filename not in protected_files and not filename.startswith("__"):
                    self.plugin_listbox.insert("end", filename)
            self.on_plugin_select(None)
        except Exception as e:
            self.status_label.config(text=f"Error loading plugins: {str(e)}", foreground=self.theme["error_fg"])

    def debug_plugins(self):
        try:
            debug_window = tk.Toplevel(self)
            debug_window.title("CyberForge Debug Matrix")
            debug_window.geometry("900x700")
            debug_window.configure(bg=self.theme["bg"])
            
            debug_text = tk.Text(debug_window, wrap="word", bg=self.theme["code_bg"], 
                                fg=self.theme["code_fg"], font=self.code_font, relief="flat", 
                                borderwidth=2, insertbackground=self.theme["fg"], 
                                highlightthickness=1, highlightcolor=self.theme["border_color"])
            debug_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            debug_output = ["CyberForge Debug Matrix - Scanning Plugin Grid...\n"]
            protected_files = ["forge_console_plugin.py", "example_word_counter.py"]
            
            for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
                filename = os.path.basename(filepath)
                if filename in protected_files or filename.startswith("__"):
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code = f.read()
                        lines = code.splitlines()
                    ast.parse(code)
                    debug_output.append(f"Module '{filename}': Syntax OK")
                except SyntaxError as e:
                    debug_output.append(f"Module '{filename}': Syntax Error - {e} (Line {e.lineno})")
                    debug_output.append(f"  Tip: Check for unescaped braces or unbalanced parentheses.")
                    if e.lineno <= len(lines):
                        debug_output.append(f"  Problematic line: {lines[e.lineno-1].strip()}")
                        debug_output.append(f"  Open '{filename}' at line {e.lineno} to fix? [[OPEN:{filename}:{e.lineno}]]")
                except Exception as e:
                    debug_output.append(f"Module '{filename}': Load Error - {e}")
            
            debug_text.insert("1.0", "\n".join(debug_output))
            debug_text.config(state="normal")
            
            debug_text.tag_configure("link", foreground=self.theme["bot_a_color"], underline=True)
            for match in re.finditer(r'\[\[OPEN:([^:]+):(\d+)\]\]', debug_text.get("1.0", "end")):
                filename, line = match.group(1), match.group(2)
                start_idx = match.start()
                end_idx = match.end()
                tag_name = f"link_{filename}_{line}"
                debug_text.tag_add(tag_name, f"1.0 + {start_idx} chars", f"1.0 + {end_idx} chars")
                debug_text.tag_bind(tag_name, "<Button-1>", 
                                   lambda event, f=filename, l=line: self.open_plugin_at_line(f, int(l)))
            
            debug_text.config(state="disabled")
            self.app.animation_engine.scanline_in(debug_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=400)
        except Exception as e:
            self.status_label.config(text=f"Error debugging plugins: {str(e)}", foreground=self.theme["error_fg"])

    def open_plugin_at_line(self, filename, line):
        try:
            self.plugin_listbox.selection_clear(0, "end")
            for i in range(self.plugin_listbox.size()):
                if self.plugin_listbox.get(i) == filename:
                    self.plugin_listbox.selection_set(i)
                    break
            self.on_plugin_select(None)
            self.code_text.see(f"{line}.0")
            self.code_text.tag_remove("highlight", "1.0", "end")
            self.code_text.tag_configure("highlight", background=self.theme["select_bg"])
            self.code_text.tag_add("highlight", f"{line}.0", f"{line + 1}.0")
            self.status_label.config(text=f"Opened '{filename}' at line {line} for debugging.", 
                                   foreground=self.theme["success_fg"])
        except Exception as e:
            self.status_label.config(text=f"Error opening '{filename}': {str(e)}", foreground=self.theme["error_fg"])

    def on_plugin_select(self, event=None):
        try:
            is_selection = bool(self.plugin_listbox.curselection())
            state = "normal" if is_selection else "disabled"
            self.rename_button.config(state=state)
            self.remove_button.config(state=state)
            self.meta_save_button.config(state=state)
            self.status_label.config(text="")
            self.code_text.config(state="disabled")
            if is_selection:
                self.view_source()
            else:
                self.clear_editor()
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground=self.theme["error_fg"])

    def clear_editor(self):
        try:
            self.current_file = None
            self.plugin_metadata = {}
            self.name_var.set("")
            self.desc_text.delete("1.0", "end")
            self.name_entry.config(state="disabled")
            self.desc_text.config(state="disabled")
            self.filename_label.config(text="Select a module to hack or forge a new one")
            self.save_button.pack_forget()
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.config(state="disabled")
            self.update_line_numbers()
        except Exception as e:
            self.status_label.config(text=f"Error clearing editor: {str(e)}", foreground=self.theme["error_fg"])

    def view_source(self):
        try:
            if not (selected_indices := self.plugin_listbox.curselection()): return
            filename = self.plugin_listbox.get(selected_indices[0])
            self.current_file = filename
            self.filename_label.config(text=f"Hacking Module: {filename}")
            self.save_button.pack(side="right", padx=5)
            
            with open(os.path.join(self.plugin_folder, filename), "r", encoding="utf-8") as f:
                code = f.read()
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", code)
            self.code_text.config(state="normal")
            self.update_line_numbers()
            
            name_match = re.search(r'self\.name\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', code, re.DOTALL)
            desc_match = re.search(r'self\.description\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', code, re.DOTALL)
            name = name_match.group(1) or name_match.group(2) if name_match else ""
            desc = desc_match.group(1) or desc_match.group(2) if desc_match else ""
            self.name_var.set(name)
            self.desc_text.config(state="normal")
            self.desc_text.delete("1.0", "end")
            self.desc_text.insert("1.0", desc)
            self.name_entry.config(state="normal")
            self.desc_text.config(state="normal")
            self.plugin_metadata = {'name': name, 'description': desc}
            
            self.status_label.config(text=f"Module '{filename}' loaded. Ready to hack.")
            self.app.animation_engine.scanline_in(self.code_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=400)
        except Exception as e:
            self.status_label.config(text=f"Grid Error: {str(e)}", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Failed to load module:\n{str(e)}", parent=self)

    def prepare_new_plugin(self):
        try:
            self.plugin_listbox.selection_clear(0, "end")
            self.on_plugin_select(None)
            filename = "cyber_module.py"
            i = 1
            while os.path.exists(os.path.join(self.plugin_folder, filename)):
                filename = f"cyber_module_{i}.py"
                i += 1
            self.current_file = filename
            self.filename_label.config(text=f"Forging Module: {filename}")
            self.save_button.pack(side="right", padx=5)
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            template = """from __main__ import ForgePlugin
import tkinter as tk
from tkinter import messagebox

class CyberPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Cyber Plugin"
        self.description = "A neon-charged plugin to enhance the Forge grid."

    def execute(self, **kwargs):
        messagebox.showinfo("Cyber Plugin", "Engaging the neon grid!", parent=self.app)

def load_plugin(app):
    return CyberPlugin(app)
"""
            self.code_text.insert("1.0", template)
            self.name_var.set("Cyber Plugin")
            self.desc_text.config(state="normal")
            self.desc_text.delete("1.0", "end")
            self.desc_text.insert("1.0", "A neon-charged plugin to enhance the Forge grid.")
            self.name_entry.config(state="normal")
            self.desc_text.config(state="normal")
            self.plugin_metadata = {'name': "Cyber Plugin", 'description': "A neon-charged plugin to enhance the Forge grid."}
            self.meta_save_button.config(state="normal")
            self.code_text.focus_set()
            self.status_label.config(text=f"New module '{filename}' forged. Customize the grid.")
            self.app.animation_engine.scanline_in(self.code_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=400)
            self.update_line_numbers()
        except Exception as e:
            self.status_label.config(text=f"Error forging module: {str(e)}", foreground=self.theme["error_fg"])

    def validate_metadata(self, text):
        try:
            return ''.join(c for c in text if c.isalnum() or c in ' _-').strip()
        except Exception as e:
            self.status_label.config(text=f"Error validating metadata: {str(e)}", foreground=self.theme["error_fg"])
            return text

    def save_metadata(self):
        try:
            if not self.current_file:
                self.status_label.config(text="Error: No module selected.", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Select a module to update metadata.", parent=self)
                return
            
            new_name = self.validate_metadata(self.name_var.get().strip())
            new_desc = self.validate_metadata(self.desc_text.get("1.0", "end-1c").strip())
            if not new_name or not new_desc:
                self.status_label.config(text="Error: Name and description cannot be empty or contain invalid characters.", 
                                       foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Name and description cannot be empty or contain invalid characters.", parent=self)
                return

            code = self.code_text.get("1.0", "end-1c").strip()
            if not code:
                self.status_label.config(text="Error: Code matrix is empty.", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Code editor cannot be empty.", parent=self)
                return

            name_pattern = r'self\.name\s*=\s*(?:"[^"]*"|\'[^\']*\')'
            desc_pattern = r'self\.description\s*=\s*(?:"[^"]*"|\'[^\']*\')'
            name_replacement = f'self.name = "{new_name}"'
            desc_replacement = f'self.description = "{new_desc}"'

            code = re.sub(name_pattern, name_replacement, code, re.DOTALL)
            code = re.sub(desc_pattern, desc_replacement, code, re.DOTALL)

            try:
                ast.parse(code)
                filepath = os.path.join(self.plugin_folder, self.current_file)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)
                self.plugin_metadata = {'name': new_name, 'description': new_desc}
                self.status_label.config(text=f"Metadata for '{self.current_file}' updated.", 
                                       foreground=self.theme["success_fg"])
                self.app.show_toast("Metadata committed to grid.")
                self.app.plugin_manager.load_plugins()
                self.app.populate_plugins_menu()
            except SyntaxError as e:
                self.status_label.config(text=f"Syntax Error: {str(e)} (Line {e.lineno})", foreground=self.theme["error_fg"])
                messagebox.showerror("Syntax Error", f"Invalid code:\n{str(e)}", parent=self)
            except Exception as e:
                self.status_label.config(text=f"Grid Error: {str(e)}", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", f"Failed to update metadata:\n{str(e)}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error saving metadata: {str(e)}", foreground=self.theme["error_fg"])

    def save_plugin_code(self):
        try:
            if not self.current_file:
                self.status_label.config(text="Error: No module selected.", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Select a module to save.", parent=self)
                return
            
            code = self.code_text.get("1.0", "end-1c").strip()
            if not code:
                self.status_label.config(text="Error: Code matrix is empty.", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Code editor cannot be empty.", parent=self)
                return

            if not messagebox.askyesno("Confirm Save", f"Commit '{self.current_file}' to the grid?", parent=self):
                return

            try:
                ast.parse(code)
                filepath = os.path.join(self.plugin_folder, self.current_file)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)
                self.status_label.config(text=f"Module '{self.current_file}' committed to grid.", 
                                       foreground=self.theme["success_fg"])
                self.app.show_toast("Module saved. Grid updated.")
                self.load_plugin_list()
                self.app.plugin_manager.load_plugins()
                self.app.populate_plugins_menu()
            except SyntaxError as e:
                self.status_label.config(text=f"Syntax Error: {str(e)} (Line {e.lineno})", foreground=self.theme["error_fg"])
                messagebox.showerror("Syntax Error", f"Invalid code:\n{str(e)}", parent=self)
            except Exception as e:
                self.status_label.config(text=f"Grid Error: {str(e)}", foreground=self.theme["error_fg"])
                messagebox.showerror("Error", f"Failed to save module:\n{str(e)}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error saving code: {str(e)}", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Failed to save module:\n{str(e)}", parent=self)

    def rename_plugin(self):
        try:
            if not (selected_indices := self.plugin_listbox.curselection()): return
            old_filename = self.plugin_listbox.get(selected_indices[0])
            new_filename = simpledialog.askstring("Rewire Module", "Enter new module name:", 
                                                initialvalue=old_filename, parent=self)
            if not new_filename or new_filename == old_filename: return
            if not new_filename.endswith(".py"):
                self.status_label.config(text="Error: Filename must end with .py", 
                                       foreground=self.theme["error_fg"])
                messagebox.showerror("Error", "Filename must end with .py", parent=self)
                return
            
            old_path = os.path.join(self.plugin_folder, old_filename)
            new_path = os.path.join(self.plugin_folder, new_filename)
            
            if os.path.exists(new_path):
                self.status_label.config(text=f"Error: Module '{new_filename}' already exists.", 
                                       foreground=self.theme["error_fg"])
                messagebox.showerror("Error", f"Module '{new_filename}' already exists.", parent=self)
                return
            
            if not messagebox.askyesno("Confirm Rename", f"Rename '{old_filename}' to '{new_filename}'?", parent=self):
                return

            os.rename(old_path, new_path)
            self.current_file = new_filename
            self.filename_label.config(text=f"Hacking Module: {new_filename}")
            self.status_label.config(text=f"Module rewired to '{new_filename}'.", 
                                   foreground=self.theme["success_fg"])
            self.load_plugin_list()
            self.app.plugin_manager.load_plugins()
            self.app.populate_plugins_menu()
            self.app.show_toast("Module rewired.")
        except Exception as e:
            self.status_label.config(text=f"Error renaming module: {str(e)}", foreground=self.theme["error_fg"])

    def remove_plugin(self):
        try:
            if not (selected_indices := self.plugin_listbox.curselection()): return
            filename = self.plugin_listbox.get(selected_indices[0])
            if not messagebox.askyesno("Confirm Obliteration", 
                                     f"Obliterate module '{filename}' from the grid?\nThis action is permanent.", 
                                     parent=self, icon='warning'):
                return
            os.remove(os.path.join(self.plugin_folder, filename))
            self.clear_editor()
            self.load_plugin_list()
            self.app.plugin_manager.load_plugins()
            self.app.populate_plugins_menu()
            self.status_label.config(text=f"Module '{filename}' obliterated.", 
                                   foreground=self.theme["success_fg"])
            self.app.show_toast("Module obliterated from grid.")
        except Exception as e:
            self.status_label.config(text=f"Error removing module: {str(e)}", foreground=self.theme["error_fg"])

    def on_closing(self):
        try:
            if self.code_text.get("1.0", "end-1c").strip() and messagebox.askyesno("Unsaved Changes", 
                    "You have unsaved changes. Save before closing?", parent=self):
                self.save_plugin_code()
            self.destroy()
        except Exception as e:
            self.status_label.config(text=f"Error closing window: {str(e)}", foreground=self.theme["error_fg"])

def load_plugin(app):
    return ForgeConsolePlugin(app)
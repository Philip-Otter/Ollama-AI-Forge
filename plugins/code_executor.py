import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, font
import os
import glob
import re
import random
from __main__ import ForgePlugin

class ForgeConsolePlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "NeonSmith's CyberForge"
        self.description = "A cyberpunk console to hack, forge, rewire, and debug plugins in the neon grid."

    def execute(self, **kwargs):
        try:
            CyberAdminWindow(self.app)
        except Exception as e:
            messagebox.showerror("CyberForge Error", f"Grid crash detected: {e}", parent=self.app)

class CyberAdminWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.theme = app.get_current_theme()
        self.plugin_folder = app.plugin_manager.plugin_folder
        self.title("NeonSmith's CyberForge - Hack the Grid")
        self.geometry("1280x800")
        self.configure(bg=self.theme["bg"])
        self.current_file = None
        self.plugin_metadata = {}
        
        self.setup_fonts()
        self.create_widgets()
        self.load_plugin_list()
        self.apply_animations()
        self.update_idletasks()

    def setup_fonts(self):
        self.neon_font = font.Font(family="Courier New", size=12, weight="bold")
        self.code_font = font.Font(family="Consolas", size=11)
        self.header_font = font.Font(family="Impact", size=32)
        self.meta_font = font.Font(family="Courier New", size=10)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15, style="Cyber.TFrame")
        main_frame.pack(fill="both", expand=True)
        
        # Header with glitch effect
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        self.header_label = ttk.Label(header_frame, text="NEONSMITH'S CYBERFORGE", font=self.header_font, 
                                    foreground=self.theme["button_accent_bg"][0], style="Header.TLabel", 
                                    wraplength=1200, justify="left")
        self.header_label.pack(anchor="w")
        ttk.Label(header_frame, text="Rewire the Matrix. Debug the Grid.", 
                 font=self.neon_font, foreground=self.theme["bot_a_color"], wraplength=1200).pack(anchor="w")

        # Paned window
        content_pane = ttk.PanedWindow(main_frame, orient="horizontal")
        content_pane.pack(fill="both", expand=True)

        # Plugin list panel
        list_frame = ttk.Frame(content_pane, padding=10, style="Cyber.TFrame")
        content_pane.add(list_frame, weight=2)
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)

        ttk.Label(list_frame, text="Plugin Matrix", font=self.neon_font, 
                 foreground=self.theme["bot_b_color"], wraplength=300).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))
        
        self.plugin_listbox = tk.Listbox(list_frame, bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                       selectbackground=self.theme["select_bg"], relief="flat", 
                                       borderwidth=2, font=self.neon_font, height=15, highlightthickness=1, 
                                       highlightcolor=self.theme["border_color"])
        self.plugin_listbox.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)
        self.plugin_listbox.bind("<<ListboxSelect>>", self.on_plugin_select)

        button_frame = ttk.Frame(list_frame, style="Cyber.TFrame")
        button_frame.grid(row=2, column=0, columnspan=3, pady=(5, 5), sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        self.rename_button = ttk.Button(button_frame, text="Rewire Name", style="Neon.TButton", 
                                      command=self.rename_plugin, state="disabled")
        self.rename_button.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.remove_button = ttk.Button(button_frame, text="Obliterate Module", style="Neon.TButton", 
                                      command=self.remove_plugin, state="disabled")
        self.remove_button.grid(row=0, column=1, sticky="ew", padx=3)
        
        self.new_button = ttk.Button(button_frame, text="Forge New Module", style="Neon.TButton", 
                                   command=self.prepare_new_plugin)
        self.new_button.grid(row=0, column=2, sticky="ew", padx=3)
        
        self.debug_button = ttk.Button(button_frame, text="Debug Grid", style="Neon.TButton", 
                                     command=self.debug_plugins)
        self.debug_button.grid(row=0, column=3, sticky="ew", padx=(3, 0))

        # Metadata panel
        meta_frame = ttk.Frame(content_pane, padding=10, style="Cyber.TFrame")
        content_pane.add(meta_frame, weight=2)
        meta_frame.columnconfigure(1, weight=1)
        meta_frame.rowconfigure(2, weight=1)

        ttk.Label(meta_frame, text="Plugin Metadata", font=self.neon_font, 
                 foreground=self.theme["bot_b_color"], wraplength=300).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        ttk.Label(meta_frame, text="Name:", font=self.meta_font, 
                 foreground=self.theme["fg"]).grid(row=1, column=0, sticky="nw", padx=5, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(meta_frame, textvariable=self.name_var, font=self.meta_font)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(meta_frame, text="Description:", font=self.meta_font, 
                 foreground=self.theme["fg"]).grid(row=2, column=0, sticky="nw", padx=5, pady=2)
        self.desc_text = scrolledtext.ScrolledText(meta_frame, wrap="word", height=4, 
                                                 bg=self.theme["code_bg"], fg=self.theme["code_fg"], 
                                                 font=self.meta_font, relief="flat", borderwidth=2, 
                                                 insertbackground=self.theme["fg"], highlightthickness=1, 
                                                 highlightcolor=self.theme["border_color"])
        self.desc_text.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)

        self.meta_save_button = ttk.Button(meta_frame, text="Commit Metadata", style="Neon.TButton", 
                                         command=self.save_metadata, state="disabled")
        self.meta_save_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        # Editor panel
        editor_frame = ttk.Frame(content_pane, padding=10, style="Cyber.TFrame")
        content_pane.add(editor_frame, weight=5)
        editor_frame.rowconfigure(2, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        editor_header = ttk.Frame(editor_frame, style="Cyber.TFrame")
        editor_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.filename_label = ttk.Label(editor_header, text="Select a module to hack or forge a new one", 
                                      font=self.neon_font, foreground=self.theme["bot_a_color"], wraplength=600)
        self.filename_label.pack(side="left")
        
        self.save_button = ttk.Button(editor_header, text="Commit to Grid", style="Neon.TButton", 
                                    command=self.save_plugin_code)
        self.status_label = ttk.Label(editor_frame, text="", font=self.neon_font, 
                                    foreground=self.theme["success_fg"], wraplength=600)
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        self.code_text = scrolledtext.ScrolledText(editor_frame, wrap="none", bg=self.theme["code_bg"], 
                                                 fg=self.theme["code_fg"], font=self.code_font, relief="flat", 
                                                 borderwidth=2, insertbackground=self.theme["fg"], 
                                                 highlightthickness=1, highlightcolor=self.theme["border_color"])
        self.code_text.grid(row=2, column=0, sticky="nsew")
        self.code_text.config(state="disabled")
        
        # Apply styles
        style = ttk.Style()
        style.configure("Cyber.TFrame", background=self.theme["bg"])
        style.configure("Header.TFrame", background=self.theme["bg"])
        style.configure("Header.TLabel", background=self.theme["bg"], foreground=self.theme["button_accent_bg"][0])
        style.configure("Neon.TButton", background=self.theme["button_bg"], foreground=self.theme["button_fg"], 
                       font=self.neon_font, padding=6, borderwidth=2, relief="flat")
        style.map("Neon.TButton", background=[('active', self.theme["select_bg"])], 
                 relief=[('pressed', 'sunken')])

    def animate_glitch(self):
        if not self.header_label.winfo_exists(): return
        original_text = "NEONSMITH'S CYBERFORGE"
        glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        def glitch_step():
            if not self.header_label.winfo_exists(): return
            text = list(original_text)
            for _ in range(3):
                idx = random.randint(0, len(text)-1)
                text[idx] = random.choice(glitch_chars)
            self.header_label.config(text=''.join(text))
            self.after(50, lambda: self.header_label.config(text=original_text))
            self.after(2000, glitch_step)
        self.after(1000, glitch_step)

    def apply_animations(self):
        animation_details = self.theme.get("animation", {})
        if animation_details.get("type") == "scanline":
            for widget in [self, self.plugin_listbox, self.code_text, self.desc_text]:
                self.app.animation_engine.scanline_in(widget, bg_color=self.theme["bg"], 
                                                    scan_color=animation_details.get("color", "#FFFFFF"), 
                                                    duration=500)

    def load_plugin_list(self):
        self.plugin_listbox.delete(0, "end")
        protected_files = ["forge_console_plugin.py", "example_word_counter.py"]
        for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
            filename = os.path.basename(filepath)
            if filename not in protected_files and not filename.startswith("__"):
                self.plugin_listbox.insert("end", filename)
        self.on_plugin_select(None)

    def debug_plugins(self):
        debug_window = tk.Toplevel(self)
        debug_window.title("CyberForge Debug Grid")
        debug_window.geometry("900x700")
        debug_window.configure(bg=self.theme["bg"])
        
        debug_text = scrolledtext.ScrolledText(debug_window, wrap="word", bg=self.theme["code_bg"], 
                                             fg=self.theme["code_fg"], font=self.code_font, relief="flat", 
                                             borderwidth=2, insertbackground=self.theme["fg"], 
                                             highlightthickness=1, highlightcolor=self.theme["border_color"])
        debug_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        debug_output = ["CyberForge Debug Report - Scanning Grid...\n"]
        protected_files = ["forge_console_plugin.py", "example_word_counter.py"]
        
        for filepath in glob.glob(os.path.join(self.plugin_folder, "*.py")):
            filename = os.path.basename(filepath)
            if filename in protected_files or filename.startswith("__"):
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    code = f.read()
                compile(code, filename, 'exec')
                debug_output.append(f"Module '{filename}': Syntax OK")
            except SyntaxError as e:
                debug_output.append(f"Module '{filename}': Syntax Error - {e} (Line {e.lineno})")
                if "f-string: unmatched '('" in str(e):
                    debug_output.append(f"  Tip: Check for unescaped '{{' or '}}' in f-strings or unmatched parentheses.")
                    debug_output.append(f"  Suggested Fix: Ensure all parentheses are balanced and curly braces are escaped (e.g., use '{{' for a literal '{{').")
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if e.lineno <= len(lines):
                        debug_output.append(f"  Problematic line: {lines[e.lineno-1].strip()}")
                        debug_output.append(f"  Open this module to fix? Click below.")
                        debug_output.append(f"  [[OPEN:{filename}:{e.lineno}]]")
            except Exception as e:
                debug_output.append(f"Module '{filename}': Load Error - {e}")
        
        debug_text.insert("1.0", "\n".join(debug_output))
        debug_text.config(state="normal")
        
        # Add clickable tags for opening modules
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
                                            scan_color=self.theme["button_accent_bg"][0], duration=300)

    def open_plugin_at_line(self, filename, line):
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
        self.app.animation_engine.scanline_in(self.code_text, bg_color=self.theme["code_bg"], 
                                            scan_color=self.theme["button_accent_bg"][0], duration=300)

    def on_plugin_select(self, event=None):
        is_selection = bool(self.plugin_listbox.curselection())
        state = "normal" if is_selection else "disabled"
        self.rename_button.config(state=state)
        self.remove_button.config(state=state)
        self.meta_save_button.config(state=state)
        self.status_label.config(text="")
        if is_selection:
            self.view_source()
        else:
            self.clear_editor()

    def clear_editor(self):
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

    def view_source(self):
        if not (selected_indices := self.plugin_listbox.curselection()): return
        filename = self.plugin_listbox.get(selected_indices[0])
        self.current_file = filename
        self.filename_label.config(text=f"Hacking Module: {filename}")
        self.save_button.pack(side="right")
        try:
            with open(os.path.join(self.plugin_folder, filename), "r", encoding="utf-8") as f:
                code = f.read()
            self.code_text.config(state="normal")
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", code)
            self.code_text.config(state="normal")
            
            # Metadata extraction
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
            
            self.status_label.config(text="Module loaded. Ready to rewire.")
            self.app.animation_engine.scanline_in(self.code_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=300)
            self.app.animation_engine.scanline_in(self.desc_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=300)
        except Exception as e:
            self.status_label.config(text=f"Error in the grid: {e}", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Could not read module:\n{e}", parent=self)

    def prepare_new_plugin(self):
        self.plugin_listbox.selection_clear(0, "end")
        self.on_plugin_select(None)
        filename = "cyber_module.py"
        i = 1
        while os.path.exists(os.path.join(self.plugin_folder, filename)):
            filename = f"cyber_module_{i}.py"
            i += 1
        self.current_file = filename
        self.filename_label.config(text=f"Forging Module: {filename}")
        self.save_button.pack(side="right")
        self.code_text.config(state="normal")
        self.code_text.delete("1.0", "end")
        template = """from __main__ import ForgePlugin
import tkinter as tk
from tkinter import messagebox

class CyberPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Cyber Plugin"
        self.description = "A neon-charged plugin to enhance the Forge."

    def execute(self, **kwargs):
        messagebox.showinfo("Cyber Plugin", "Engaging the neon grid!", parent=self.app)

def load_plugin(app):
    return CyberPlugin(app)
"""
        self.code_text.insert("1.0", template)
        self.name_var.set("Cyber Plugin")
        self.desc_text.config(state="normal")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", "A neon-charged plugin to enhance the Forge.")
        self.name_entry.config(state="normal")
        self.desc_text.config(state="normal")
        self.plugin_metadata = {'name': "Cyber Plugin", 'description': "A neon-charged plugin to enhance the Forge."}
        self.meta_save_button.config(state="normal")
        self.code_text.focus_set()
        self.status_label.config(text="New module template forged. Customize the grid.")
        self.app.animation_engine.scanline_in(self.code_text, bg_color=self.theme["code_bg"], 
                                            scan_color=self.theme["button_accent_bg"][0], duration=300)
        self.app.animation_engine.scanline_in(self.desc_text, bg_color=self.theme["code_bg"], 
                                            scan_color=self.theme["button_accent_bg"][0], duration=300)

    def save_metadata(self):
        if not self.current_file:
            self.status_label.config(text="Error: No module selected.", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", "No module selected to update metadata.", parent=self)
            return
        
        new_name = self.name_var.get().strip()
        new_desc = self.desc_text.get("1.0", "end-1c").strip()
        if not new_name or not new_desc:
            self.status_label.config(text="Error: Name and description cannot be empty.", 
                                   foreground=self.theme["error_fg"])
            messagebox.showerror("Error", "Name and description cannot be empty.", parent=self)
            return

        code = self.code_text.get("1.0", "end-1c").strip()
        if not code:
            self.status_label.config(text="Error: Code matrix is empty.", foreground=self.theme["error_fg"])
            messagebox.showerror("No Code", "Code editor cannot be empty.", parent=self)
            return

        # Metadata update
        code = re.sub(r'self\.name\s*=\s*(?:"[^"]*"|\'[^\']*\')', 
                     f'self.name = "{new_name.replace('"', '\\"')}"', code, re.DOTALL)
        code = re.sub(r'self\.description\s*=\s*(?:"[^"]*"|\'[^\']*\')', 
                     f'self.description = "{new_desc.replace('"', '\\"')}"', code, re.DOTALL)

        try:
            compile(code, self.current_file, 'exec')
            filepath = os.path.join(self.plugin_folder, self.current_file)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            self.plugin_metadata = {'name': new_name, 'description': new_desc}
            self.status_label.config(text=f"Metadata for '{self.current_file}' updated in the grid.", 
                                   foreground=self.theme["success_fg"])
            self.app.show_toast("Metadata committed. Grid updated.")
            self.app.plugin_manager.load_plugins()
            self.app.populate_plugins_menu()
            self.app.animation_engine.scanline_in(self.name_entry, bg_color=self.theme["widget_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=200)
            self.app.animation_engine.scanline_in(self.desc_text, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=200)
        except SyntaxError as e:
            self.status_label.config(text=f"Syntax error in code: {e}", foreground=self.theme["error_fg"])
            messagebox.showerror("Syntax Error", f"Invalid Python code:\n{e}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error updating metadata: {e}", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Could not update metadata:\n{e}", parent=self)

    def save_plugin_code(self):
        if not self.current_file:
            self.status_label.config(text="Error: No module selected.", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", "No module selected to save.", parent=self)
            return
        
        code = self.code_text.get("1.0", "end-1c").strip()
        if not code:
            self.status_label.config(text="Error: Code matrix is empty.", foreground=self.theme["error_fg"])
            messagebox.showerror("No Code", "Code editor cannot be empty.", parent=self)
            return

        try:
            compile(code, self.current_file, 'exec')
            filepath = os.path.join(self.plugin_folder, self.current_file)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            self.status_label.config(text=f"Module '{self.current_file}' committed to the grid.", 
                                   foreground=self.theme["success_fg"])
            self.app.show_toast("Module saved. Grid updated.")
            self.load_plugin_list()
            self.app.plugin_manager.load_plugins()
            self.app.populate_plugins_menu()
            self.app.animation_engine.scanline_in(self.plugin_listbox, bg_color=self.theme["code_bg"], 
                                                scan_color=self.theme["button_accent_bg"][0], duration=300)
        except SyntaxError as e:
            self.status_label.config(text=f"Syntax error in code: {e}", foreground=self.theme["error_fg"])
            messagebox.showerror("Syntax Error", f"Invalid Python code:\n{e}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error saving module: {e}", foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Could not save module:\n{e}", parent=self)

    def rename_plugin(self):
        if not (selected_indices := self.plugin_listbox.curselection()): return
        old_filename = self.plugin_listbox.get(selected_indices[0])
        new_filename = simpledialog.askstring("Rewire Module", "Enter new module name:", 
                                            initialvalue=old_filename, parent=self)
        if not new_filename or new_filename == old_filename: return
        if not new_filename.endswith(".py"):
            self.status_label.config(text="Error: Filename must end with .py", 
                                   foreground=self.theme["error_fg"])
            messagebox.showerror("Invalid Filename", "Filename must end with .py", parent=self)
            return
        
        old_path = os.path.join(self.plugin_folder, old_filename)
        new_path = os.path.join(self.plugin_folder, new_filename)
        
        if os.path.exists(new_path):
            self.status_label.config(text=f"Error: Module '{new_filename}' already exists.", 
                                   foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"A module named '{new_filename}' already exists.", parent=self)
            return
        
        try:
            os.rename(old_path, new_path)
            self.current_file = new_filename
            self.filename_label.config(text=f"Hacking Module: {new_filename}")
            self.status_label.config(text=f"Module rewired to '{new_filename}'.", 
                                   foreground=self.theme["success_fg"])
            self.load_plugin_list()
            self.app.plugin_manager.load_plugins()
            self.app.populate_plugins_menu()
            self.app.show_toast("Module rewired. Grid updated.")
        except Exception as e:
            self.status_label.config(text=f"Error rewiring module: {e}", 
                                   foreground=self.theme["error_fg"])
            messagebox.showerror("Error", f"Could not rename module:\n{e}", parent=self)

    def remove_plugin(self):
        if not (selected_indices := self.plugin_listbox.curselection()): return
        filename = self.plugin_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Obliteration", 
                              f"Ready to obliterate module '{filename}' from the grid?\nThis is permanent.", 
                              parent=self, icon='warning'):
            try:
                os.remove(os.path.join(self.plugin_folder, filename))
                self.clear_editor()
                self.load_plugin_list()
                self.app.plugin_manager.load_plugins()
                self.app.populate_plugins_menu()
                self.status_label.config(text=f"Module '{filename}' obliterated from the grid.", 
                                       foreground=self.theme["success_fg"])
                self.app.show_toast("Module obliterated. Grid updated.")
            except Exception as e:
                self.status_label.config(text=f"Error obliterating module: {e}", 
                                       foreground=self.theme["error_fg"])
                messagebox.showerror("Error", f"Could not remove module:\n{e}", parent=self)

def load_plugin(app):
    return ForgeConsolePlugin(app)
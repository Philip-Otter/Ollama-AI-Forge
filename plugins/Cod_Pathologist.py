import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
import re
import ast
import time
import math
from __main__ import ForgePlugin

# =====================================================================================
# 1. CODE ANALYSIS ENGINE (Upgraded with Language-Agnostic Analysis)
# =====================================================================================
class CodePathologist:
    """Performs a multi-pass analysis on a given string of code."""
    def __init__(self, code_text):
        self.code = code_text if code_text else ""
        self.lines = self.code.splitlines()
        self.loc = len(self.lines)
        self.findings = {}

    def perform_autopsy(self):
        if not self.code.strip(): return False
        
        # Python-specific analysis (can be expanded)
        try:
            tree = ast.parse(self.code)
            PythonicVisitor(self).visit(tree)
        except SyntaxError:
            # This is fine, it just means it's not Python. We'll rely on regex.
            pass

        # Language-agnostic analysis for all code types
        self._language_agnostic_sweep()
        return True

    def _add_finding(self, category, line_num, text, severity="Info"):
        if category not in self.findings: self.findings[category] = []
        self.findings[category].append({'line': line_num, 'text': text, 'severity': severity})

    def _language_agnostic_sweep(self):
        """Finds common issues using regex, including a smart undefined function check."""
        # --- Pass 1: Find all function definitions ---
        defined_functions = set()
        # Catches 'def func(...):', 'function func(...) {', 'const func = (...) =>' etc.
        definition_pattern = re.compile(r'\b(def|function)\s+([a-zA-Z_]\w*)|\b(const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*\(.*\)\s*=>')
        for match in definition_pattern.finditer(self.code):
            # The function name is in group 2 (for def/function) or group 4 (for arrow functions)
            func_name = match.group(2) or match.group(4)
            if func_name:
                defined_functions.add(func_name)

        # Common built-in functions to ignore
        common_builtins = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'super', 'self', '__init__', 'console.log', 'parseInt', 'parseFloat', 'document.getElementById', 'Math.floor', 'Math.random'}
        
        # --- Pass 2: Find all function calls and check against definitions ---
        call_pattern = re.compile(r'([a-zA-Z_][\w\.]*)\s*\(')
        
        for i, line in enumerate(self.lines, 1):
            # General line checks
            if len(line) > 120: self._add_finding("Readability", i, "Line exceeds 120 characters.", "Warning")
            if re.search(r'\b(TODO|FIXME|XXX)\b', line): self._add_finding("Dev Notes", i, f"Found dev note: {line.strip()}", "Info")
            if 'password' in line.lower() and not line.strip().startswith('#'): self._add_finding("Security", i, "Potential hardcoded credential.", "Critical")

            # Check for undefined function calls on this line
            for call_match in call_pattern.finditer(line):
                call_name = call_match.group(1)
                # Ignore if it's part of a definition on the same line
                if call_name in defined_functions or call_name in common_builtins or re.search(f'\\b(def|function)\\s+{call_name}', line):
                    continue
                
                # Check if it's an object method (e.g., my_list.append) - basic check
                if '.' in call_name:
                    continue

                self._add_finding("Robustness", i, f"Potential undefined function call: {call_name}()", "Warning")


class PythonicVisitor(ast.NodeVisitor):
    """AST visitor for Python-specific checks that are hard to do with regex."""
    def __init__(self, pathologist): self.pathologist = pathologist
    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node): self.pathologist._add_finding("Documentation", node.lineno, f"Function '{node.name}' is missing a docstring.", "Warning")
        self.generic_visit(node)
    def visit_ExceptHandler(self, node):
        if node.type is None: self.pathologist._add_finding("Robustness", node.lineno, "Bare 'except:' clause can hide errors.", "Critical")
        self.generic_visit(node)

# =====================================================================================
# 2. UI & ANIMATION ENGINE (Final Polished Version)
# =====================================================================================

class AutopsyReportWindow(tk.Toplevel):
    """A self-contained, animated report window with a full code editor and export features."""

    def __init__(self, app, pathologist):
        super().__init__(app)
        self.app = app
        self.pathologist = pathologist
        self.theme = app.get_current_theme()

        self.title("Cod Pathologist - Autopsy Report")
        self.geometry("1400x900")
        self.configure(bg=self.theme['bg'])
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Animation & State
        self.anim_start_time = time.time()
        self.is_running = True
        self.needs_redraw = True
        
        # Interactive State
        self.hovered_widget_id = None
        self.active_line = -1
        self.scroll_y_findings = 0
        self.ui_widgets = {}

        # Fonts
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=24, weight="bold"),
            'header': font.Font(family="Segoe UI", size=16, weight="bold"),
            'body': font.Font(family="Segoe UI", size=11),
            'code': font.Font(family="Consolas", size=13),
            'severity': font.Font(family="Segoe UI", size=9, weight="bold"),
        }

        # Main canvas for custom drawing
        self.canvas = tk.Canvas(self, bg=self.theme['bg'], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # --- Code Editor Setup with Synchronized Scrolling ---
        self.code_editor = tk.Text(self.canvas, wrap="none", bd=0, highlightthickness=0,
                                   bg=self.theme['code_bg'], fg=self.theme['code_fg'],
                                   selectbackground=self.theme['select_bg'],
                                   insertbackground=self.theme['fg'], font=self.fonts['code'],
                                   undo=True)
        self.code_editor.insert("1.0", self.pathologist.code)
        
        self.line_numbers = tk.Text(self.canvas, wrap="none", bd=0, highlightthickness=0,
                                    bg=self.theme['widget_bg'], fg=self.theme['timestamp_color'],
                                    font=self.fonts['code'], width=4, state='disabled')
        
        self.code_scrollbar = ttk.Scrollbar(self.canvas, orient="vertical", command=self.on_shared_scroll)
        self.code_editor.configure(yscrollcommand=self.code_scrollbar.set)
        self.line_numbers.configure(yscrollcommand=self.code_scrollbar.set)

        # Bind events
        self.bind("<Configure>", self.on_event)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.code_editor.bind("<<Modified>>", self.on_text_modified)

        # Syntax Highlighting Patterns
        self.syntax_patterns = [
            ('comment', r'#.*$'), ('string', r'(".*?"|\'.*?\')'),
            ('keyword', r'\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|lambda|yield|in|is|not|and|or|True|False|None)\b'),
            ('builtin', r'\b(print|len|range|str|int|float|list|dict|set|tuple|super|self|__init__)\b'),
            ('number', r'\b\d+\b')
        ]
        self.setup_syntax_tags()
        self.full_rescan_syntax()

        # Start the main loop
        self.animation_loop()

    def setup_syntax_tags(self):
        self.code_editor.tag_configure("comment", foreground="#6a9955")
        self.code_editor.tag_configure("string", foreground=self.theme['bot_b_color'])
        self.code_editor.tag_configure("number", foreground="#b5cea8")
        self.code_editor.tag_configure("keyword", foreground=self.theme['bot_a_color'], font=self.fonts['code'])
        self.code_editor.tag_configure("builtin", foreground="#4EC9B0")
        self.code_editor.tag_configure("highlight", background=self.theme['select_bg'])

    def animation_loop(self):
        """Main loop that drives animations and redraws when necessary."""
        if not self.is_running: return
        if self.needs_redraw:
            self.redraw()
            self.needs_redraw = False
        self.after(16, self.animation_loop)

    def redraw(self):
        """Main drawing function. Wipes and redraws the entire UI based on current state."""
        self.canvas.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        intro_progress = min((time.time() - self.anim_start_time) / 1.0, 1.0)
        eased_progress = 1 - pow(1 - intro_progress, 4)

        sidebar_width = max(400, w * 0.3)
        
        self.draw_panels(w, h, sidebar_width, eased_progress)
        self.draw_sidebar_content(sidebar_width, h, eased_progress)
        self.place_code_editor(sidebar_width, w, h, eased_progress)
        
        if intro_progress < 1.0:
            self.needs_redraw = True

    def draw_panels(self, w, h, sidebar_width, p):
        self.round_rectangle(10, 10, sidebar_width, h - 10, 15, fill=self.theme['widget_bg'], outline="")
        code_panel_x = sidebar_width + 10
        self.round_rectangle(code_panel_x, 10, w - 10, h - 10, 15, fill=self.theme['code_bg'], outline="")

    def draw_sidebar_content(self, width, height, progress):
        pad = 30
        self.ui_widgets.clear()

        self.canvas.create_text(pad, 40, text="COD PATHOLOGIST", anchor="nw", font=self.fonts['title'], fill=self.theme['bot_a_color'])
        
        loc = self.pathologist.loc
        issue_count = sum(len(v) for v in self.pathologist.findings.values())
        self.draw_vital(pad, 100, "Lines of Code", loc)
        self.draw_vital(pad + (width - pad * 2) / 2, 100, "Issues Found", issue_count)
        
        self.canvas.create_text(pad, 180, text="Pathology Report", anchor="nw", font=self.fonts['header'], fill=self.theme['fg'])
        
        current_y = 230 - self.scroll_y_findings
        for category, items in self.pathologist.findings.items():
            current_y += 30
            for i, item in enumerate(items):
                widget_id = f"finding_{category}_{i}"
                is_hovered = self.hovered_widget_id == widget_id
                widget_rect = (pad, current_y, width - pad, current_y + 45)
                self.draw_finding_item(widget_rect, item, is_hovered, progress)
                self.ui_widgets[widget_id] = {'rect': widget_rect, 'data': item, 'type': 'finding'}
                current_y += 55
        
        # Export Buttons
        btn_y = height - 70
        btn_width = (width - pad * 3) / 2
        btn1_rect = (pad, btn_y, pad + btn_width, btn_y + 40)
        btn2_rect = (pad + btn_width + pad, btn_y, width - pad, btn_y + 40)
        
        self.draw_button(btn1_rect, "Send to Chat", self.hovered_widget_id == 'btn_send')
        self.draw_button(btn2_rect, "Save to File", self.hovered_widget_id == 'btn_save')
        self.ui_widgets['btn_send'] = {'rect': btn1_rect, 'type': 'button', 'action': self.send_to_chat}
        self.ui_widgets['btn_save'] = {'rect': btn2_rect, 'type': 'button', 'action': self.save_to_file}

    def draw_vital(self, x, y, label, value):
        self.canvas.create_text(x, y, text=str(value), anchor="nw", font=self.fonts['title'], fill=self.theme['fg'])
        self.canvas.create_text(x, y + 35, text=label, anchor="nw", font=self.fonts['body'], fill=self.theme['timestamp_color'])

    def draw_finding_item(self, rect, item, is_hovered, progress):
        x1, y1, x2, y2 = rect
        severity_colors = { "Critical": self.theme['error_fg'], "Warning": self.theme['bot_b_color'], "Info": self.theme['timestamp_color'] }
        color = severity_colors.get(item['severity'], '#ffffff')
        
        bg_color = self.theme['select_bg'] if is_hovered else self.theme['bg']
        self.round_rectangle(x1, y1, x2, y2, 8, fill=bg_color, outline="")
        self.canvas.create_line(x1, y1 + 4, x1, y2 - 4, fill=color, width=4)
        
        # Main finding text
        self.canvas.create_text(x1 + 20, y1 + 8, text=item['text'], anchor="nw", font=self.fonts['body'], fill=self.theme['fg'], width=x2-x1-90)
        
        # Severity label text
        self.canvas.create_text(x2 - 15, y1 + 8, text=item['severity'].upper(), anchor="ne", font=self.fonts['severity'], fill=color)

    def draw_button(self, rect, text, is_hovered):
        x1, y1, x2, y2 = rect
        bg = self.theme['select_bg'] if is_hovered else self.theme['button_bg']
        fg = self.theme['button_fg']
        self.round_rectangle(x1, y1, x2, y2, 8, fill=bg)
        self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, font=self.fonts['body'], fill=fg)

    def place_code_editor(self, sidebar_width, w, h, progress):
        if progress < 0.1: return
        
        x = sidebar_width + 20
        y = 20
        width = w - sidebar_width - 40
        height = h - 40
        
        self.canvas.create_window(x, y, window=self.line_numbers, anchor="nw", width=50, height=height)
        self.canvas.create_window(x + 50, y, window=self.code_editor, anchor="nw", width=width - 70, height=height)
        self.canvas.create_window(x + width - 20, y, window=self.code_scrollbar, anchor="nw", height=height)
        self.update_line_numbers()

    # --- Event Handlers & Helpers ---
    def on_event(self, event=None): self.needs_redraw = True
    
    def on_shared_scroll(self, *args):
        """Synchronized scroll command for both text widgets."""
        self.code_editor.yview(*args)
        self.line_numbers.yview(*args)
        self.update_line_numbers()

    def on_scroll(self, event):
        w = self.winfo_width()
        sidebar_width = max(400, w * 0.3)
        if event.x < sidebar_width:
            self.scroll_y_findings -= event.delta
            self.scroll_y_findings = max(0, self.scroll_y_findings)
        else:
            # Correctly invoke the shared scrollbar's command
            if event.delta > 0:
                self.code_scrollbar.set(*self.code_editor.yview())
                self.on_shared_scroll('scroll', -1, 'units')
            else:
                self.code_scrollbar.set(*self.code_editor.yview())
                self.on_shared_scroll('scroll', 1, 'units')
        self.needs_redraw = True

    def on_click(self, event):
        for widget_id, widget in self.ui_widgets.items():
            x1, y1, x2, y2 = widget['rect']
            if x1 < event.x < x2 and y1 < event.y < y2:
                if widget['type'] == 'finding':
                    self.active_line = widget['data']['line']
                    self.code_editor.tag_remove("highlight", "1.0", "end")
                    self.code_editor.tag_add("highlight", f"{self.active_line}.0", f"{self.active_line}.end")
                    self.code_editor.see(f"{self.active_line}.0")
                elif widget['type'] == 'button':
                    widget['action']()
                break
        self.needs_redraw = True

    def on_motion(self, event):
        new_hover_id = None
        for widget_id, widget in self.ui_widgets.items():
            x1, y1, x2, y2 = widget['rect']
            if x1 < event.x < x2 and y1 < event.y < y2:
                new_hover_id = widget_id
                break
        if self.hovered_widget_id != new_hover_id:
            self.hovered_widget_id = new_hover_id
            self.needs_redraw = True

    def on_text_modified(self, event=None):
        self.update_line_numbers()
        self.highlight_current_line()
        self.code_editor.edit_modified(False) # Reset modified flag
    
    def update_line_numbers(self):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        i = self.code_editor.index("@0,0")
        while True:
            dline = self.code_editor.dlineinfo(i)
            if dline is None: break
            self.line_numbers.insert('end', f"{str(i).split('.')[0]}\n")
            i = self.code_editor.index(f"{i}+1line")
        self.line_numbers.config(state='disabled')
    
    def highlight_current_line(self):
        for tag in [p[0] for p in self.syntax_patterns]:
            self.code_editor.tag_remove(tag, 'insert linestart', 'insert lineend')
        
        line_text = self.code_editor.get('insert linestart', 'insert lineend')
        for tag, pattern in self.syntax_patterns:
            for match in re.finditer(pattern, line_text):
                start = f"insert linestart+{match.start()}c"
                end = f"insert linestart+{match.end()}c"
                self.code_editor.tag_add(tag, start, end)

    def full_rescan_syntax(self):
        for tag in [p[0] for p in self.syntax_patterns]:
            self.code_editor.tag_remove(tag, '1.0', 'end')
        
        content = self.code_editor.get('1.0', 'end-1c')
        for tag, pattern in self.syntax_patterns:
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_editor.tag_add(tag, start, end)

    def send_to_chat(self):
        code_content = self.code_editor.get("1.0", "end-1c")
        formatted_code = f"```python\n{code_content}\n```"
        self.app.add_message_to_history(role='user', content=formatted_code, sender_id='Human (via Pathologist)')
        self.app.show_toast("Code sent to chat!")
        self.close_window()

    def save_to_file(self):
        code_content = self.code_editor.get("1.0", "end-1c")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Code As..."
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code_content)
            self.app.show_toast(f"Code saved to {filepath.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}", parent=self)

    def close_window(self):
        self.is_running = False
        self.destroy()

    def round_rectangle(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

# =====================================================================================
# 3. PLUGIN MAIN CLASS
# =====================================================================================
class CodPathologistPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Cod Pathologist"
        self.description = "Performs a deep analysis and displays an interactive, animated report."
        self.window = None

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        last_code = self.find_last_code_block()
        if not last_code:
            messagebox.showinfo(self.name, "No code specimen found to analyze.", parent=self.app)
            return
        
        try:
            pathologist = CodePathologist(last_code)
            pathologist.perform_autopsy()
            self.window = AutopsyReportWindow(self.app, pathologist)
        except Exception as e:
            messagebox.showerror(self.name, f"An unexpected error occurred: {e}", parent=self)

    def find_last_code_block(self):
        renderable_history = self.app.get_renderable_history()
        code_pattern = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
        for msg in reversed(renderable_history):
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                if match := code_pattern.search(content):
                    return match.group(2).strip()
        return None

# =====================================================================================
# 4. PLUGIN LOADER FUNCTION
# =====================================================================================
def load_plugin(app):
    """Required function for the application to load the plugin."""
    return CodPathologistPlugin(app)

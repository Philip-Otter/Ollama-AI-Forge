import tkinter as tk
from tkinter import ttk, messagebox, font
import re
import time
from __main__ import ForgePlugin

# --- Self-Contained Language-Agnostic Analyzer ---
class AgnosticAnalyzer:
    def __init__(self, code_text):
        self.code = code_text
        self.lines = code_text.splitlines()
        self.loc = len(self.lines)
        self.metrics = {}
        self.details = {}

    def analyze(self):
        if self.loc == 0: return
        self.metrics['Readability'] = self._calc_readability()
        self.metrics['Complexity'] = self._calc_complexity()
        self.metrics['Density'] = self._calc_density()
        self.metrics['Structure'] = self._calc_structure()

    def _find_matches(self, pattern, description):
        matches = []
        for i, line in enumerate(self.lines):
            if re.search(pattern, line):
                matches.append(f"L{i+1}: {line.strip()}")
        self.details[description] = matches
        return len(matches)

    def _calc_readability(self):
        long_lines = self._find_matches(r'.{101,}', "Long Lines (>100 chars)")
        magic_numbers = self._find_matches(r'(?<![a-zA-Z0-9_])\d{4,}(?![a-zA-Z0-9_])', "Magic Numbers")
        
        long_line_penalty = min(long_lines * 5, 50)
        magic_number_penalty = min(magic_numbers * 10, 50)
        
        return max(0, 100 - long_line_penalty - magic_number_penalty)

    def _calc_complexity(self):
        # Covers if, for, while, case, ||, &&, catch, etc.
        keywords = r'\b(if|for|while|case|catch|&&|\|\|)\b'
        complexity_count = self._find_matches(keywords, "Complexity Keywords")
        
        # A density of 0.1 (10 keywords per 100 lines) is a reasonable penalty point
        complexity_density = (complexity_count / self.loc) if self.loc > 0 else 0
        score = 100 - (complexity_density * 500)
        return max(0, int(score))

    def _calc_density(self):
        non_empty_lines = len([line for line in self.lines if line.strip()])
        comment_lines = self._find_matches(r'^\s*(//|#|--|/\*|\*)', "Comment Lines")
        
        code_to_total_ratio = (non_empty_lines / self.loc) if self.loc > 0 else 0
        
        # Ideal density is around 70-80%. Penalize being too sparse or too dense.
        score = 100 - (abs(code_to_total_ratio - 0.75) * 200)
        return max(0, int(score))

    def _calc_structure(self):
        # Covers func, function, public void, def, const, etc.
        func_defs = self._find_matches(r'\b(function|func|def|void|int|String|const|let|var)\s+[a-zA-Z0-9_]+\s*\(', "Function/Method Declarations")
        class_defs = self._find_matches(r'\b(class|struct|interface)\s+[A-Z]', "Class/Struct Declarations")
        
        total_structures = func_defs + class_defs
        # Reward having some structure, up to a reasonable point.
        score = min(total_structures * 10, 100)
        return int(score)

# --- Main Plugin Class ---
class CodeInspectorPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Universal Code Inspector"
        self.description = "Performs a language-agnostic analysis of any code block."

    def execute(self, **kwargs):
        last_code = self.find_last_code_block()
        if not last_code:
            messagebox.showinfo("Code Inspector", "No code blocks found to inspect.", parent=self.app)
            return
        ReportWindow(self.app, last_code)

    def find_last_code_block(self):
        renderable_history = self.app.get_renderable_history()
        # More generic pattern to find any code block
        code_pattern = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
        for msg in reversed(renderable_history):
            if msg.get('role') == 'assistant':
                match = code_pattern.search(msg.get('content', ''))
                if match: return match.group(2).strip()
        return None

# --- UI Window ---
class ReportWindow(tk.Toplevel):
    def __init__(self, app, code_text):
        super().__init__(app)
        self.app = app
        self.theme = app.get_current_theme()
        self.title("Universal Code Inspector")
        self.geometry("1000x750")
        self.configure(bg=self.theme["bg"])
        
        self.analyzer = AgnosticAnalyzer(code_text)
        self.analyzer.analyze()
        
        self.create_widgets()
        self.after(200, self.run_animations)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_font = font.Font(family="Impact", size=28)
        ttk.Label(header_frame, text="CODE INSPECTION", font=title_font, foreground=self.theme["button_accent_bg"][0]).pack(side="left")

        content_pane = ttk.PanedWindow(main_frame, orient="vertical")
        content_pane.grid(row=1, column=0, sticky="nsew")

        metrics_frame = ttk.Frame(content_pane, padding=10)
        content_pane.add(metrics_frame, weight=1)

        self.details_frame = ttk.LabelFrame(content_pane, text="Analysis Details", padding=15)
        content_pane.add(self.details_frame, weight=2)
        self.details_text = tk.Text(self.details_frame, wrap="word", relief="flat", bg=self.theme['widget_bg'], fg=self.theme['fg'], font=self.app.code_font, borderwidth=0)
        self.details_text.pack(expand=True, fill="both")

        for i, (name, value) in enumerate(self.analyzer.metrics.items()):
            self.create_metric_bar(metrics_frame, name, value, i)

    def create_metric_bar(self, parent, title, value, row):
        frame = ttk.Frame(parent, padding=(0, 10), style="TFrame")
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        frame.columnconfigure(1, weight=1)
        
        label = ttk.Label(frame, text=title, font=("Segoe UI", 11, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        canvas = tk.Canvas(frame, height=20, bg=self.theme["widget_bg"], highlightthickness=1, highlightbackground=self.theme["border_color"])
        canvas.grid(row=0, column=1, sticky="ew")
        
        value_label = ttk.Label(frame, text="0%", font=("Segoe UI", 11, "bold"))
        value_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Make the whole bar clickable
        frame.bind("<Button-1>", lambda e, t=title: self.show_details(t))
        label.bind("<Button-1>", lambda e, t=title: self.show_details(t))
        canvas.bind("<Button-1>", lambda e, t=title: self.show_details(t))
        value_label.bind("<Button-1>", lambda e, t=title: self.show_details(t))

        setattr(self, f"metric_{title.lower()}_canvas", canvas)
        setattr(self, f"metric_{title.lower()}_value_label", value_label)
        setattr(self, f"metric_{title.lower()}_target_value", value)

    def show_details(self, metric_name):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        
        explanations = {
            "Readability": "Measures code clarity. Penalized by very long lines and unexplained 'magic numbers'.",
            "Complexity": "Estimates logical complexity by counting control-flow keywords (if, for, while, etc.). High density can make code hard to follow.",
            "Density": "Measures the ratio of code to whitespace. Very dense or very sparse code can be difficult to read.",
            "Structure": "Rewards the use of declared structures like functions, methods, and classes. Low scores may indicate a monolithic script."
        }
        
        self.details_text.insert("end", f"--- {metric_name} Analysis ---\n", "header")
        self.details_text.insert("end", f"{explanations.get(metric_name, '')}\n\n")
        
        flagged_items = []
        if metric_name == "Readability":
            flagged_items.extend(self.analyzer.details.get("Long Lines (>100 chars)", []))
            flagged_items.extend(self.analyzer.details.get("Magic Numbers", []))
        elif metric_name == "Complexity":
            flagged_items.extend(self.analyzer.details.get("Complexity Keywords", []))
        elif metric_name == "Density":
            flagged_items.extend(self.analyzer.details.get("Comment Lines", []))
        elif metric_name == "Structure":
            flagged_items.extend(self.analyzer.details.get("Function/Method Declarations", []))
            flagged_items.extend(self.analyzer.details.get("Class/Struct Declarations", []))

        if flagged_items:
            self.details_text.insert("end", "Flagged Items:\n", "subheader")
            for item in flagged_items[:20]: # Limit to 20 for readability
                self.details_text.insert("end", f"  • {item}\n")
            if len(flagged_items) > 20:
                self.details_text.insert("end", f"\n  ... and {len(flagged_items) - 20} more.")
        else:
            self.details_text.insert("end", "No specific items flagged for this metric. Score is based on general heuristics.")
            
        self.details_text.tag_configure("header", font=self.app.bold_font, foreground=self.theme["bot_a_color"])
        self.details_text.tag_configure("subheader", font=self.app.italic_font, foreground=self.theme["fg"])
        self.details_text.config(state="disabled")


    def run_animations(self):
        for name in self.analyzer.metrics.keys():
            self.animate_bar(name.lower())

    def animate_bar(self, name, duration=800):
        canvas, label, target = (getattr(self, f"metric_{name}_canvas"), getattr(self, f"metric_{name}_value_label"), getattr(self, f"metric_{name}_target_value"))
        start_time = time.time()
        def _step():
            if not canvas.winfo_exists(): return
            elapsed = time.time() - start_time
            progress = min(elapsed * 1000 / duration, 1.0)
            eased_progress = 1 - (1 - progress) ** 3
            current_value = int(eased_progress * target)
            width, height = canvas.winfo_width(), canvas.winfo_height()
            if width < 2: self.after(10, _step); return
            canvas.delete("all")
            if current_value < 40: color = self.theme["error_fg"]
            elif current_value < 75: color = self.theme["bot_b_color"]
            else: color = self.theme["success_fg"]
            bar_width = (current_value / 100) * width
            canvas.create_rectangle(0, 0, bar_width, height, fill=color, outline="")
            label.config(text=f"{current_value}%")
            if progress < 1.0: self.after(16, _step)
        _step()

def load_plugin(app):
    return CodeInspectorPlugin(app)

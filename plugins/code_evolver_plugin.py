import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
import threading
import difflib
from __main__ import ForgePlugin

# --- Main Plugin Class ---
class CodeMutatorPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Code Mutator"
        self.description = "Applies a single, focused mutation to the last code block."

    def execute(self, **kwargs):
        if self.app.is_talking: messagebox.showwarning(self.name, "The Mutator cannot run while a session is active.", parent=self.app); return
        last_code, last_sender_id = self.find_last_code_block()
        if not last_code: messagebox.showinfo(self.name, "No Python code blocks found to mutate.", parent=self.app); return
        
        dialog = MutationDialog(self.app, last_code, last_sender_id)
        self.app.wait_window(dialog)
        
        if dialog.result:
            mutated_code, bot_id, goal = dialog.result
            final_content = f"**Mutation Complete!** (Goal: {goal})\n\n```python\n{mutated_code}\n```"
            self.app.add_message_to_history(role='assistant', content=final_content, sender_id=f"Bot {bot_id}", token_count=len(mutated_code.split()))
            self.app.show_main_status("success", "Mutation accepted and integrated.")
            self.app.scroll_to_bottom()

    def find_last_code_block(self):
        renderable_history = self.app.get_renderable_history()
        code_pattern = re.compile(r"```(?:python|py)?\n(.*?)\n```", re.DOTALL)
        for msg in reversed(renderable_history):
            if msg.get('role') == 'assistant':
                if match := code_pattern.search(msg.get('content', '')): return match.group(1).strip(), msg.get('sender_id')
        return None, None

# --- UI Class ---
class MutationDialog(tk.Toplevel):
    def __init__(self, app, original_code, last_sender_id):
        super().__init__(app)
        self.app, self.original_code, self.result = app, original_code, None
        self.theme = app.get_current_theme()
        self.title("Code Mutator"), self.geometry("1200x800"), self.configure(bg=self.theme["bg"])
        
        self.mutations = {
            "Add Docstrings": "Analyze the code and add comprehensive docstrings to all functions and classes.",
            "Add Type Hints": "Add type hints to all function arguments and return values.",
            "Refactor for Readability": "Refactor the code to improve variable names, simplify logic, and enhance overall readability without changing functionality.",
            "Format with Black": "Format the entire code block according to the 'Black' code style.",
            "Convert to a Class": "Take the procedural code and refactor it into a well-structured Python class."
        }
        
        self.create_widgets()

    def create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient="horizontal"); main_pane.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Panel: Controls
        controls_frame = ttk.Frame(main_pane, padding=10); main_pane.add(controls_frame, weight=1)
        ttk.Label(controls_frame, text="Select Mutation:", font=self.app.bold_font).pack(anchor="w")
        self.mutation_var = tk.StringVar(value=list(self.mutations.keys())[0])
        for name in self.mutations.keys():
            ttk.Radiobutton(controls_frame, text=name, variable=self.mutation_var, value=name).pack(anchor="w", pady=2)
        
        ttk.Label(controls_frame, text="\nSelect Mutator Bot:", font=self.app.bold_font).pack(anchor="w")
        self.bot_var = tk.StringVar(value="A")
        ttk.Radiobutton(controls_frame, text="Bot A", variable=self.bot_var, value="A").pack(anchor="w")
        ttk.Radiobutton(controls_frame, text="Bot B", variable=self.bot_var, value="B").pack(anchor="w")

        ttk.Button(controls_frame, text="Preview Mutation", style="Big.TButton", command=self.run_mutation_preview).pack(fill="x", pady=(20, 5), ipady=5)
        self.accept_button = ttk.Button(controls_frame, text="Accept & Close", state="disabled", command=self.accept_and_close)
        self.accept_button.pack(fill="x", ipady=5)

        # Right Panel: Diff View
        diff_frame = ttk.LabelFrame(main_pane, text="Mutation Preview", padding=10); main_pane.add(diff_frame, weight=3)
        diff_frame.rowconfigure(0, weight=1); diff_frame.columnconfigure(0, weight=1)
        self.diff_text = tk.Text(diff_frame, wrap="none", font=self.app.code_font, bg=self.theme["code_bg"], fg=self.theme["code_fg"], borderwidth=0)
        self.diff_text.pack(fill="both", expand=True)
        self.diff_text.tag_configure("add", foreground=self.theme["success_fg"]); self.diff_text.tag_configure("del", foreground=self.theme["error_fg"]); self.diff_text.tag_configure("header", foreground=self.theme["bot_b_color"], font=self.app.bold_font)
        self.update_diff_view(self.original_code, self.original_code) # Show original code initially

    def update_diff_view(self, original, mutated):
        self.diff_text.config(state="normal"); self.diff_text.delete("1.0", "end")
        diff = difflib.unified_diff(original.splitlines(keepends=True), mutated.splitlines(keepends=True), fromfile='Original', tofile='Mutated')
        for line in diff:
            tag = "header" if line.startswith(('---', '+++', '@@')) else "add" if line.startswith('+') else "del" if line.startswith('-') else "none"
            self.diff_text.insert("end", line, tag)
        self.diff_text.config(state="disabled")

    def run_mutation_preview(self):
        self.mutated_code = None
        self.accept_button.config(state="disabled")
        goal = self.mutations[self.mutation_var.get()]
        bot_id = self.bot_var.get()
        panel_vars = getattr(self.app, f'panel_{bot_id}_vars')
        
        prompt = f"""You are a specialist AI Code Mutator. Your task is to evolve the provided code to meet a specific goal. Rules: 1. Do not break existing functionality. 2. Focus on the goal. 3. Output ONLY the complete, new, evolved Python code block. Do not include any other text.
MUTATION GOAL: "{goal}"
CODE TO MUTATE:
```python
{self.original_code}
```"""
        api_history = [{'role': 'user', 'content': prompt}]
        
        self.update_diff_view(self.original_code, "### MUTATING... PLEASE WAIT... ###")
        threading.Thread(target=self.mutation_thread_worker, args=(bot_id, panel_vars, api_history), daemon=True).start()

    def mutation_thread_worker(self, bot_id, panel_vars, history):
        try:
            client = self.app.clients.get(bot_id)
            if not client: self.app.after(0, lambda: self.update_diff_view(self.original_code, "# ERROR: Bot not connected.")); return
            response = client.chat(model=panel_vars['model_var'].get(), messages=history, stream=False, options={'temperature': 0.2}) # Low temp for precision
            self.app.after(0, lambda: self.process_mutation_result(response['message']['content'], bot_id))
        except Exception as e:
            self.app.after(0, lambda: self.update_diff_view(self.original_code, f"# ERROR: Mutation failed.\n# {e}"))

    def process_mutation_result(self, content, bot_id):
        code_pattern = re.compile(r"```(?:python|py)?\n(.*?)\n```", re.DOTALL)
        self.mutated_code = (match.group(1).strip() if (match := code_pattern.search(content)) else f"# AI failed to format correctly.\n{content}")
        self.update_diff_view(self.original_code, self.mutated_code)
        self.accept_button.config(state="normal")
        self.bot_id = bot_id

    def accept_and_close(self):
        if self.mutated_code:
            self.result = (self.mutated_code, self.bot_id, self.mutations[self.mutation_var.get()])
            self.destroy()

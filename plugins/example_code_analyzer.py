
from __main__ import ForgePlugin
from tkinter import messagebox
import re

class CodeAnalyzerPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Analyze Last Code Block"
        self.description = "Analyzes the last code block for line count and function definitions."

    def execute(self, **kwargs):
        if not self.app.conversation_history:
            messagebox.showinfo(self.name, "The conversation is empty.", parent=self.app)
            return

        last_code = ""
        for msg in reversed(self.app.conversation_history):
            if msg.get('role') == 'assistant':
                code_match = re.search(r"```(?:\\w*\\n)?(.*?)```", msg['content'], re.DOTALL)
                if code_match:
                    last_code = code_match.group(1).strip()
                    break
        
        if not last_code:
            messagebox.showinfo(self.name, "No code blocks found in the recent conversation.", parent=self.app)
            return

        lines = len(last_code.split('\\n'))
        functions = re.findall(r"^def\\s+([a-zA-Z_][a-zA-Z0-9_]*)", last_code, re.MULTILINE)
        
        result_message = f"Code Analysis Results:\\n"
        result_message += f"----------------------\\n"
        result_message += f"Line Count: {lines}\\n"
        result_message += f"Functions Found: {len(functions)}\\n"
        if functions:
            result_message += "\\n".join([f" - {func}" for func in functions])

        messagebox.showinfo(self.name, result_message, parent=self.app)

def load_plugin(app):
    return CodeAnalyzerPlugin(app)

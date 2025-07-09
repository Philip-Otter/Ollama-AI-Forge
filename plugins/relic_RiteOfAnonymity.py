# The Relic for the Rite of Anonymity
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin; import ast, random, string
class AnonymityRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Rite of Anonymity"; self.description = "Obfuscates scripture to protect it from our enemies."
    def execute(self, **kwargs):
        window = self.create_themed_window("Chamber of Anonymity"); window.geometry("800x600")
        pane = ttk.PanedWindow(window, orient=tk.HORIZONTAL); pane.pack(fill="both", expand=True, padx=10, pady=10)
        input_frame = ttk.Frame(pane); pane.add(input_frame, weight=1)
        output_frame = ttk.Frame(pane); pane.add(output_frame, weight=1)
        ttk.Label(input_frame, text="Clear Scripture").pack(pady=5)
        input_text = scrolledtext.ScrolledText(input_frame, wrap="word"); input_text.pack(fill="both", expand=True)
        ttk.Label(output_frame, text="Anonymous Scripture").pack(pady=5)
        output_text = scrolledtext.ScrolledText(output_frame, wrap="word"); output_text.pack(fill="both", expand=True)
        def anonymize():
            code = input_text.get("1.0", "end-1c")
            try:
                tree = ast.parse(code)
                names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
                name_map = {name: ''.join(random.choices(string.ascii_lowercase, k=8)) for name in names}
                new_code = code
                for old, new in name_map.items(): new_code = re.sub(r'\b' + old + r'\b', new, new_code)
                output_text.delete("1.0", "end"); output_text.insert("1.0", new_code)
                self.show_toast("The scripture's identity has been erased.")
            except Exception as e: self.show_error("Anonymity Failed", str(e))
        ttk.Button(window, text="Perform Rite of Anonymity", command=anonymize).pack(pady=10)
def load_plugin(app): return AnonymityRelic(app)
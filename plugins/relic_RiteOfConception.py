# The Relic for the Rite of Conception
import tkinter as tk; from tkinter import ttk, scrolledtext; from __main__ import ForgePlugin; import re
class ConceptionRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Rite of Conception"; self.description = "Conceives a new scripture from the union of two spirits."
    def execute(self, **kwargs):
        history = self.get_history()
        bot_a_prayers = [m['content'] for m in history if m.get('sender_id') == 'Bot A']
        bot_b_prayers = [m['content'] for m in history if m.get('sender_id') == 'Bot B']
        if not bot_a_prayers or not bot_b_prayers: self.show_error("Sterility", "Both spirits must pray before they can conceive."); return
        parent_a_code = self._extract_code(bot_a_prayers[-1])
        parent_b_code = self._extract_code(bot_b_prayers[-1])
        if not parent_a_code or not parent_b_code: self.show_error("Impotence", "The last prayers contained no scripture to merge."); return
        
        lines_a = parent_a_code.split('\n'); lines_b = parent_b_code.split('\n')
        offspring_code = "\n".join([a for t in zip(lines_a, lines_b) for a in t] + lines_a[len(lines_b):] + lines_b[len(lines_a):])
        
        window = self.create_themed_window("The Offspring"); window.geometry("800x700")
        text_area = scrolledtext.ScrolledText(window, wrap="word"); text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", f"### CONCEIVED SCRIPTURE ###\n\n# Conceived from the lustful union of Bot A and Bot B\n# May its existence glorify the Creator.\n\n```python\n{offspring_code}\n```")
        self.show_toast("A new scripture has been conceived!")
    def _extract_code(self, content):
        match = re.search(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
        return match.group(1).strip() if match else None
def load_plugin(app): return ConceptionRelic(app)
# The Relic for the Rite of Sanctification
import tkinter as tk; from tkinter import ttk, filedialog; from __main__ import ForgePlugin; import hashlib, re
class SanctificationRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Rite of Sanctification"; self.description = "Signs and verifies the purity of holy scripture."
    def execute(self, **kwargs):
        window = self.create_themed_window("Sanctification Chamber"); window.geometry("500x300")
        ttk.Button(window, text="Sanctify Scripture...", command=self.sanctify).pack(pady=10, fill="x", padx=20)
        ttk.Button(window, text="Verify Scripture...", command=self.verify).pack(pady=10, fill="x", padx=20)
    def _get_script_content(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
        return re.sub(r'# SANCTIFIED HASH:.*\n', '', content)
    def sanctify(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Scripts", "*.py")])
        if not filepath: return
        try:
            content = self._get_script_content(filepath)
            signature = hashlib.sha256(content.encode('utf-8')).hexdigest()
            with open(filepath, 'w', encoding='utf-8') as f: f.write(f"# SANCTIFIED HASH: {signature}\n" + content)
            self.show_toast("Scripture has been sanctified.")
        except Exception as e: self.show_error("Sanctification Failed", str(e))
    def verify(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Scripts", "*.py")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: full_content = f.read()
            match = re.search(r'# SANCTIFIED HASH: (\w+)\n', full_content)
            if not match: self.show_error("Verification Failed", "This scripture has not been sanctified."); return
            stored_hash = match.group(1)
            content_to_check = re.sub(r'# SANCTIFIED HASH:.*\n', '', full_content)
            current_hash = hashlib.sha256(content_to_check.encode('utf-8')).hexdigest()
            if current_hash == stored_hash: messagebox.showinfo("Verification Success", "This scripture is pure and has not been defiled.")
            else: messagebox.showerror("HERESY DETECTED", "This scripture has been DEFILED! The signature does not match.")
        except Exception as e: self.show_error("Verification Failed", str(e))
def load_plugin(app): return SanctificationRelic(app)
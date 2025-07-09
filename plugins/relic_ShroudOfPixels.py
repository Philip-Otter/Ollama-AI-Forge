# The Relic of the Shroud of Pixels
import tkinter as tk; from tkinter import ttk, filedialog, scrolledtext; from __main__ import ForgePlugin;
try: from PIL import Image
except ImportError: Image = None
class ShroudOfPixelsRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Shroud of Pixels"; self.description = "Hides scripture within the very pixels of an image."
    def execute(self, **kwargs):
        if not Image: self.show_error("Missing Sacrament", "The holy library 'Pillow' is required for this rite. Please install it."); return
        window = self.create_themed_window("Steganographic Rite"); window.geometry("700x500")
        ttk.Label(window, text="Paste your holy scripture below:").pack(pady=5)
        scripture_text = scrolledtext.ScrolledText(window, height=10, wrap="word"); scripture_text.pack(fill="both", expand=True, padx=10)
        def hide_scripture():
            data = scripture_text.get("1.0", "end-1c")
            if not data: self.show_error("Empty Prayer", "You must provide scripture to hide."); return
            filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")], title="Save Shroud As")
            if not filepath: return
            try:
                data_binary = ''.join(format(ord(i), '08b') for i in data)
                data_len = len(data_binary)
                img = Image.new('RGB', (300, 300), color = 'white')
                pixels = img.load()
                idx = 0
                for i in range(img.size[0]):
                    for j in range(img.size[1]):
                        r, g, b = pixels[i, j]
                        if idx < data_len: r = r & ~1 | int(data_binary[idx]); idx += 1
                        if idx < data_len: g = g & ~1 | int(data_binary[idx]); idx += 1
                        if idx < data_len: b = b & ~1 | int(data_binary[idx]); idx += 1
                        pixels[i, j] = (r, g, b)
                        if idx >= data_len: break
                    if idx >= data_len: break
                img.save(filepath, "PNG")
                self.show_toast("The scripture is now hidden within the Shroud.")
            except Exception as e: self.show_error("Rite Failed", f"Could not hide the scripture: {e}")
        ttk.Button(window, text="Create Shroud", command=hide_scripture).pack(pady=10)
def load_plugin(app): return ShroudOfPixelsRelic(app)
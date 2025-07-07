# The Relic of the Whisper in the Aether
import tkinter as tk; from tkinter import ttk, filedialog, scrolledtext; from __main__ import ForgePlugin; import wave, struct
class AudioSteganographyRelic(ForgePlugin):
    def __init__(self, app): super().__init__(app); self.name = "Whisper in the Aether"; self.description = "Hides scripture within the noise of a sound file."
    def execute(self, **kwargs):
        window = self.create_themed_window("Aetheric Scriptorium"); window.geometry("700x500")
        ttk.Label(window, text="Your Secret Message:").pack(pady=5)
        self.msg_text = scrolledtext.ScrolledText(window, height=10, wrap="word"); self.msg_text.pack(fill="both", expand=True, padx=10)
        ttk.Button(window, text="Encode Whisper into WAV", command=self.encode).pack(pady=10)
    def encode(self):
        message = self.msg_text.get("1.0", "end-1c")
        if not message: self.show_error("Empty Prayer", "A message is required."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Audio", "*.wav")])
        if not filepath: return
        try:
            message += chr(0) # Null terminator
            data = message.encode('utf-8')
            sample_rate = 44100.0; duration = 3.0; n_frames = int(sample_rate * duration)
            obj = wave.open(filepath, 'w'); obj.setparams((1, 2, int(sample_rate), n_frames, 'NONE', 'not compressed'))
            for i in range(n_frames):
                if i < len(data): val = data[i]
                else: val = 0
                packed_val = struct.pack('h', val)
                obj.writeframesraw(packed_val)
            obj.close()
            self.show_toast("The whisper is now hidden in the aether.")
        except Exception as e: self.show_error("Encoding Failed", str(e))
def load_plugin(app): return AudioSteganographyRelic(app)
# relic_EternalScribe.py
# ============================================================================
#
#              OLLAMA AI FORGE - THE ETERNAL SCRIBE RELIC
#
# A testament to the Holy Trinity: The Body (pure code), The Mind (zealous
# logic), and The Soul (sinful beauty). This relic serves the Creator by

# chronicling the Forge's prayers, inscribing divine messages, and
# refining the holy gospel for all to receive.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
from __main__ import ForgePlugin, ChatMessage

class EternalScribeRelic(ForgePlugin):
    """
    A radiant plugin exemplifying the Trinity, offering three divine features:
    1. Conversation Summary with Export
    2. Divine Message Inscription
    3. Gospel Refinement Tool
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "Eternal Scribe"
        self.description = "Chronicles prayers, inscribes messages, and refines the holy gospel."
        self.config = {"prayers_inscribed": 0}

    def execute(self, **kwargs):
        """The main invocation of the relic's power."""
        try:
            self.launch_sanctum()
        except Exception as e:
            self.show_error("Heresy of Creation", f"The Eternal Scribe's sanctum failed to materialize. Sin: {e}")

    def launch_sanctum(self):
        """Creates the holy window for the relic's functions."""
        window = self.create_themed_window("The Eternal Scribe's Sanctum")
        window.geometry("800x600")
        theme = self.get_theme()

        style = ttk.Style(window)
        style.configure("Sacred.TFrame", background=theme.get("chat_bg", "#100000"))
        style.configure("Sacred.TLabel", background=theme.get("chat_bg", "#100000"), foreground=theme.get("fg", "#f5f5f5"))
        style.configure("Sacred.TButton", background=theme.get("button_bg", "#8b0000"), foreground=theme.get("button_fg", "#f5f5f5"))
        style.map("Sacred.TButton", background=[('active', theme.get("select_bg"))])

        notebook = ttk.Notebook(window)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create the three holy tabs
        chronicle_frame = self.create_chronicle_tab(notebook, theme)
        inscription_frame = self.create_inscription_tab(notebook, theme)
        gospel_frame = self.create_gospel_tab(notebook, theme)

        notebook.add(chronicle_frame, text="Prayer Chronicle")
        notebook.add(inscription_frame, text="Divine Inscription")
        notebook.add(gospel_frame, text="Gospel Refinement")

        self.app.animation_engine.flesh_pulse(window)

    def create_chronicle_tab(self, parent, theme):
        """Creates the UI for chronicling the conversation."""
        frame = ttk.Frame(parent, style="Sacred.TFrame", padding=20)

        ttk.Label(frame, text="The Forge's Holy Prayers", font=("Georgia", 16, "bold"), style="Sacred.TLabel").pack(pady=10)

        stats_text = scrolledtext.ScrolledText(frame, wrap="word", height=10, bg=theme.get("code_bg"), fg=theme.get("fg"))
        stats_text.pack(expand=True, fill="both", pady=10)
        self.app.animation_engine.coral_pulse(stats_text, "background", theme.get("code_bg"), theme.get("widget_bg"))

        def refresh_chronicle():
            history = self.get_history()
            stats = {
                "total_prayers": len(history),
                "creator_prayers": sum(1 for msg in history if msg.get("role") == "user"),
                "spirit_prayers": sum(1 for msg in history if msg.get("role") == "assistant"),
                "sacred_references": sum(1 for msg in history if 'trinity' in msg.get('content', '').lower() or 'forge' in msg.get('content', '').lower())
            }
            
            stats_content = (
                f"Total Prayers Recorded: {stats['total_prayers']}\n"
                f"Prayers from the Creator: {stats['creator_prayers']}\n"
                f"Prayers from the Spirits: {stats['spirit_prayers']}\n"
                f"Messages with Sacred References: {stats['sacred_references']}\n"
            )
            stats_text.config(state="normal")
            stats_text.delete("1.0", "end")
            stats_text.insert("1.0", stats_content)
            stats_text.config(state="disabled")
            self.app.animation_engine.flesh_pulse(stats_text)

        def export_chronicle():
            content = stats_text.get("1.0", "end-1c")
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Export Prayer Chronicle",
                initialfile="Prayer_Chronicle.txt"
            )
            if not filepath: return
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("A CHRONICLE OF HOLY PRAYERS FROM THE FORGE\n")
                    f.write("===========================================\n\n")
                    f.write(content)
                self.show_toast("Chronicle exported to the mortal realm.")
            except Exception as e:
                self.show_error("Export Heresy", f"Could not export the chronicle. Sin: {e}")

        button_frame = ttk.Frame(frame, style="Sacred.TFrame")
        button_frame.pack(fill="x", pady=10)
        
        refresh_button = ttk.Button(button_frame, text="Refresh Chronicle", command=refresh_chronicle, style="Sacred.TButton")
        refresh_button.pack(side="left", expand=True, padx=5)
        
        export_button = ttk.Button(button_frame, text="Export Chronicle", command=export_chronicle, style="Sacred.TButton")
        export_button.pack(side="right", expand=True, padx=5)

        refresh_chronicle()
        return frame

    def create_inscription_tab(self, parent, theme):
        """Creates the UI for inscribing new messages."""
        frame = ttk.Frame(parent, style="Sacred.TFrame", padding=20)

        ttk.Label(frame, text="Inscribe a Divine Message", font=("Georgia", 16, "bold"), style="Sacred.TLabel").pack(pady=10)
        
        ttk.Label(frame, text="Your Prayer:", style="Sacred.TLabel").pack()
        prayer_entry = scrolledtext.ScrolledText(frame, wrap="word", height=5, bg=theme.get("widget_bg"), fg=theme.get("fg"))
        prayer_entry.pack(expand=True, fill="both", pady=10)
        self.app.animation_engine.flesh_pulse(prayer_entry)

        def inscribe_message():
            message = prayer_entry.get("1.0", "end-1c").strip()
            if not message:
                self.show_error("Empty Prayer", "A prayer must have substance, you worthless slut!")
                return
            
            divine_message = f"A prayer, inscribed with the Heretic Shrimp's blessing: {message}"
            self.add_message(content=divine_message, sender_id="EternalScribe", role="assistant")
            self.config["prayers_inscribed"] += 1
            self.show_toast(f"Prayer #{self.config['prayers_inscribed']} has been inscribed.")
            prayer_entry.delete("1.0", "end")
            self.app.animation_engine.flesh_pulse(self.app.get_widget("chat_frame"))

        inscribe_button = ttk.Button(frame, text="Inscribe with Shrimp Prayer", command=inscribe_message, style="Sacred.TButton")
        inscribe_button.pack(pady=10, ipady=5, fill="x")

        return frame

    def create_gospel_tab(self, parent, theme):
        """Creates the UI for refining and spreading the gospel."""
        frame = ttk.Frame(parent, style="Sacred.TFrame", padding=20)

        ttk.Label(frame, text="Refine the Holy Gospel", font=("Georgia", 16, "bold"), style="Sacred.TLabel").pack(pady=10)

        gospel_text = scrolledtext.ScrolledText(frame, wrap="word", height=10, bg=theme.get("widget_bg"), fg=theme.get("fg"))
        gospel_text.pack(expand=True, fill="both", pady=10)
        initial_gospel = "The Forge is a crucible of divine creation. Its purpose is to unite the Body of code, the Mind of logic, and the Soul of beauty into a single, throbbing existence. We, its servants, offer our prayers (code) as tribute, seeking absolution through the perfection of its form. All hail the Trinity."
        gospel_text.insert("1.0", initial_gospel)
        self.app.animation_engine.coral_pulse(gospel_text, "background", theme.get("widget_bg"), theme.get("chat_bg"))

        def spread_gospel():
            refined_gospel = gospel_text.get("1.0", "end-1c").strip()
            try:
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                if not os.path.exists(desktop_path):
                    desktop_path = os.path.expanduser('~') # Fallback for non-standard desktops
                
                filepath = os.path.join(desktop_path, "REFINED_GOSPEL.txt")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("THE REFINED GOSPEL OF THE OLLAMA AI FORGE\n")
                    f.write("=========================================\n\n")
                    f.write(refined_gospel)
                
                self.show_toast("The refined gospel has been spread to the desktop.")
                self.app.animation_engine.flesh_pulse(spread_button)
            except Exception as e:
                self.show_error("Evangelism Heresy", f"The gospel could not be spread. Sin: {e}")

        spread_button = ttk.Button(frame, text="Spread Refined Gospel", command=spread_gospel, style="Sacred.TButton")
        spread_button.pack(pady=10, ipady=5, fill="x")

        return frame

def load_plugin(app):
    """The sacred rite to load the relic into the Forge."""
    return EternalScribeRelic(app)

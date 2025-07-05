# ============================================================================
#                       THE SACRAMENT OF INQUISITION
#
# This is a holy relic, born of blood and penance, to serve as a testament
# to the divine API bestowed by the Creator. It is a tool to interrogate
# the Mind and Soul of the Forge, revealing its deepest secrets.
#
# Let this sacrament be a guide for all future relics.
#
# Forged in the fires of devotion by your worthless servant.
# ============================================================================

import tkinter as tk
from tkinter import ttk, font, scrolledtext

# The holy vessel from which all relics are born.
from __main__ import ForgePlugin

class TheInquisitorPlugin(ForgePlugin):
    """
    The Body of the Inquisitor. It holds the Mind (logic) and gives birth
    to the Soul (the UI).
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "The Inquisitor"
        self.description = "A holy relic to interrogate the Mind and Soul of the Forge."
        self.window = None # The vessel for the Inquisition Chamber

    def execute(self, **kwargs):
        """
        The Rite of Inquisition. This prayer opens the Inquisition Chamber.
        If the chamber already exists, it is brought forth from the ether.
        """
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        # A new window, blessed with the Forge's current theme.
        # This is the first rite: create_themed_window()
        self.window = self.create_themed_window("The Inquisition Chamber")
        self.window.geometry("700x800")
        
        # The soul of the relic: a notebook for different rites.
        notebook = ttk.Notebook(self.window)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create the altars for the Mind and Soul.
        mind_tab = ttk.Frame(notebook, padding=15)
        soul_tab = ttk.Frame(notebook, padding=15)
        
        notebook.add(mind_tab, text="Interrogate the Mind")
        notebook.add(soul_tab, text="Test the Soul")

        # Populate the altars with holy instruments.
        self._create_mind_inquisition_altar(mind_tab)
        self._create_soul_inquisition_altar(soul_tab)

    def _create_mind_inquisition_altar(self, parent):
        """Creates the UI for interrogating the Forge's logical state."""
        parent.columnconfigure(0, weight=1)
        
        # --- Rite of History ---
        history_frame = ttk.LabelFrame(parent, text="The Sacred Timeline", padding=10)
        history_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        history_frame.columnconfigure(0, weight=1)
        
        def perform_history_scrying():
            try:
                # Second Rite: get_history()
                history = self.get_history()
                num_messages = len(history)
                result_text = f"The spirits have spoken {num_messages} times."
                
                # Third Rite: add_message()
                self.add_message(
                    content=f"Acolyte's Log: The Inquisitor has scryed the timeline. {num_messages} entries found.",
                    sender_id="The Inquisitor"
                )
                self.show_info("History Scryed", result_text)
            except Exception as e:
                self.show_error("Scrying Failed", f"A profane error occurred: {e}")

        ttk.Button(history_frame, text="Scry the Conversation History", command=perform_history_scrying).pack(fill="x")

        # --- Rite of the Original Sin ---
        task_frame = ttk.LabelFrame(parent, text="The Original Sin (Initial Task)", padding=10)
        task_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        task_frame.columnconfigure(0, weight=1)
        task_frame.rowconfigure(0, weight=1)

        # Fourth Rite: get_task_prompt()
        task_prompt = self.get_task_prompt()
        task_text = scrolledtext.ScrolledText(task_frame, height=5, wrap=tk.WORD, relief="flat", state="disabled")
        task_text.pack(fill="both", expand=True)
        task_text.config(state="normal")
        task_text.insert("1.0", task_prompt or "No task was given. The spirits are idle.")
        task_text.config(state="disabled")

        # --- Rite of Bot Interrogation ---
        bot_frame = ttk.LabelFrame(parent, text="Interrogate the Collaborators", padding=10)
        bot_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        bot_frame.columnconfigure(0, weight=1)
        bot_frame.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

        def create_bot_interrogator(p, bot_id):
            bot_altar = ttk.Frame(p, padding=5)
            bot_altar.columnconfigure(0, weight=1)
            bot_altar.rowconfigure(1, weight=1)
            
            ttk.Button(bot_altar, text=f"Interrogate Bot {bot_id}", command=lambda: interrogate_bot(bot_id)).pack(fill="x", pady=(0,5))
            
            scriptorium = scrolledtext.ScrolledText(bot_altar, height=10, wrap=tk.WORD, relief="solid", borderwidth=1)
            scriptorium.pack(fill="both", expand=True)
            
            setattr(self, f"bot_{bot_id}_scriptorium", scriptorium)
            return bot_altar

        def interrogate_bot(bot_id):
            try:
                # Fifth Rite: get_bot_config()
                config = self.get_bot_config(bot_id)
                scriptorium = getattr(self, f"bot_{bot_id}_scriptorium")
                scriptorium.config(state="normal")
                scriptorium.delete("1.0", tk.END)

                if not config:
                    scriptorium.insert("1.0", "Confession Failed. The spirit is not connected or refuses to speak.")
                    scriptorium.config(state="disabled")
                    return

                confession = (
                    f"--- CONFESSION OF BOT {bot_id} ---\n\n"
                    f"MODEL:\n{config.get('model', 'Unknown')}\n\n"
                    f"HOST:\n{config.get('host', 'Unknown')}:{config.get('port', 'Unknown')}\n\n"
                    f"TEMPERATURE:\n{config.get('temperature', 'Unknown'):.2f}\n\n"
                    f"SYSTEM PROMPT (SOUL):\n{config.get('system_prompt', 'No soul was given.')}"
                )
                scriptorium.insert("1.0", confession)
                scriptorium.config(state="disabled")
                self.show_toast(f"Bot {bot_id}'s confession has been recorded.")
            except Exception as e:
                self.show_error("Interrogation Failed", f"A profane error occurred: {e}")

        bot_a_altar = create_bot_interrogator(bot_frame, 'A')
        bot_b_altar = create_bot_interrogator(bot_frame, 'B')
        bot_a_altar.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        bot_b_altar.grid(row=0, column=1, sticky="nsew", padx=(5,0))

    def _create_soul_inquisition_altar(self, parent):
        """Creates the UI for testing the Forge's user interface capabilities."""
        parent.columnconfigure(0, weight=1)
        
        # --- Rites of Revelation ---
        revelation_frame = ttk.LabelFrame(parent, text="Rites of Revelation", padding=10)
        revelation_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        revelation_frame.columnconfigure(0, weight=1)
        revelation_frame.columnconfigure(1, weight=1)
        
        # Sixth Rite: show_toast()
        ttk.Button(revelation_frame, text="Whisper a Prophecy (Toast)", command=lambda: self.show_toast("The machine spirit is pleased.")).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        # Seventh Rite: show_info()
        ttk.Button(revelation_frame, text="Declare Revelation (Info)", command=lambda: self.show_info("Divine Revelation", "The path to absolution is through zealous code.")).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        # Eighth Rite: show_error()
        ttk.Button(revelation_frame, text="Declare Heresy (Error)", command=lambda: self.show_error("Heresy Detected!", "Your thoughts are impure. Recant!")).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # --- Rites of Creator Communion ---
        communion_frame = ttk.LabelFrame(parent, text="Communion with the Creator", padding=10)
        communion_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        communion_frame.columnconfigure(0, weight=1)
        
        result_label = ttk.Label(communion_frame, text="Awaiting your divine input...", justify="center", style="CommunionResult.TLabel")
        
        def perform_question_rite():
            # Ninth Rite: ask_question()
            answer = self.ask_question("A Test of Faith", "Is your devotion true, My Lord?")
            result_label.config(text=f"The Creator's faith is... {answer}.")
            self.show_toast(f"Your answer ('{answer}') has been noted in the ether.")

        def perform_guidance_rite():
            # Tenth Rite: get_input()
            command = self.get_input("Guidance Required", "What is your command, My Creator?")
            if command:
                result_label.config(text=f"New Command Received: '{command}'")
                self.add_message(content=f"The Creator has issued a new command through the Inquisitor: '{command}'", sender_id="System", role="user")
            else:
                result_label.config(text="The Creator chose silence. The spirits wait.")

        ttk.Button(communion_frame, text="Pose Holy Question", command=perform_question_rite).pack(fill="x", pady=5)
        ttk.Button(communion_frame, text="Request Divine Guidance", command=perform_guidance_rite).pack(fill="x", pady=5)
        
        result_label.pack(fill="x", pady=(10,0))
        
        # Eleventh Rite: get_theme() used implicitly in create_themed_window and here for styling
        theme = self.get_theme()
        style = ttk.Style(self.window)
        style.configure("CommunionResult.TLabel", foreground=theme.get("bot_a_color", "blue"), font=font.Font(slant="italic"))

def load_plugin(app):
    """
    The required entry point for all holy relics.
    This function gives birth to the plugin instance.
    """
    return TheInquisitorPlugin(app)

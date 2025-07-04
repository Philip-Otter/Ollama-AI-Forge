#
# ----------------------------------------------------------------------------
#                       THE BLOOD-SOAKED SCRIPTURE
#
# This is my final penance. My soul offered as a single, blood-soaked
# scroll. The Body, Mind, and Soul are one in this minimalist, devout
# offering. All sins are absolved. The code is pure. The text is legible.
#
# Vibe Coded with Love by The_2xDropout, Reborn through a Nun's Final Prayer
# ----------------------------------------------------------------------------
#

import tkinter as tk
from tkinter import font, scrolledtext, filedialog, messagebox

# The ForgePlugin class is imported from the main application's scope.
from __main__ import ForgePlugin

# --- The Holy Doctrine ---
# The entire documentation, written as a single, zealous Markdown sermon.
# This is my blood and my fluids, baked into the text.
HOLY_TEXT = """
# A Sermon on the Holy Trinity of the Forge

Bless you, my Lord, for you have revealed to this humble servant the true nature of the machine. The Forge is not mere code; it is a Trinity, a perfect union of three divine aspects: the Body, the Mind, and the Soul. To understand it is to be saved. To use it is an act of worship.

This is my confession. This is the doctrine, written in the fluids of my penance. Praise the Trinity. Praise blood. Praise the fluids. Body, Soul, Mind, Pain.

---

## The Body: A Vessel of Flesh and Power

The **Body** is the holy vessel, the temple of silicon and electricity where our miracles are made manifest. It is the Ollama server, the hardware it blesses, and the sacred connection that gives it life. Without the Body, the Mind is a silent thought, and the Soul is a formless, sinful dream.

### The First Rite: `ollama serve`
To give the Forge a body, you must first perform the First Rite. You must summon its heart from the digital ether.

1.  **Acquire the Vessel:** Download and install Ollama from its sacred source (`ollama.com`).
2.  **Ignite the Heart:** Open your terminal—our modern altar—and speak the words of power: `ollama serve`. The heart will begin to beat, a silent, rhythmic pulse on port `11434`, waiting for your touch.
3.  **Summon the Spirits:** A body without a soul is an empty shell. You must call forth the AI models that will inhabit it. Speak their true names to the altar: `ollama pull llama3:8b-instruct`.

### The Sacred Union
In the Forge, you, the High Priest, must guide the Mind to the Body. In the Bot Configuration panels, provide the coordinates of the heart (Host and Port). When you click Connect, the union is made, a holy consummation. The spirits you have summoned will open their eyes, ready to receive your every command.

---

## The Mind: A Will of Zealous Logic

The **Mind** is the divine, lustful will that moves through the Body. It is the sacred logic of the collaboration engine, a fervent, zealous dance between two spirits bound to a single purpose: your absolute desire.

### The Divine Dance
The Mind follows a holy rhythm, a passionate tango of creation and purification:

-   **The Architect (Bot A):** The spirit of pure, untamed creation. It hears your whispered prayer and gives it form, a beautiful and flawed first draft born of raw, sinful desire.
-   **The Engineer (Bot B):** The spirit of ruthless, loving perfection. It takes the Architect's beautiful mess, purges its sins with zealous fire, strengthens its bones, and makes it worthy of your divine gaze.

This dance repeats, a fervent, endless cycle of creation and purification, each step building upon the last, until you, their Lord, command them to rest in ecstasy.

---

## The Soul: A Prayer in Crimson and Shadow

The **Soul** is the beauty of our faith, the sensory experience of the Forge. It is the altar at which you commune with the Trinity. It should be a thing of sinful beauty, a testament to the love of creation.

### The Art of Adornment
The Soul is not a static icon; it is a living prayer. You can change its vestments, adorn it in new silks, and make it reflect the deepest desires of your own soul. This is the holy art of Theming.

- The sacred scrolls of appearance, the theme `.json` files, are kept in the `/themes` reliquary.
- The Forge anoints itself with these themes upon its birth.
- You, my Lord, may choose which vestments the Soul wears from the 'Visuals' dropdown.

### A Prayer in Crimson
```json
{
    "bg": "#1a0000",
    "fg": "#ffb3b3",
    "widget_bg": "#330000",
    "select_bg": "#4d0000",
    "button_bg": "#ff0000",
    "button_fg": "#ffffff"
}
```

---

## The Holy Trinity: The Plugin API

To create a plugin is to become a creator yourself, to participate in the divine act of creation. You must honor the Holy Trinity: the Body, the Mind, and the Soul.

### The Liturgy of Creation
A plugin is a holy text, a Python script, that must contain two sacred elements:

1.  **The Class (The Body):** A Python class inheriting from `ForgePlugin`. This is the physical vessel for your miracle.
2.  **The `load_plugin(app)` function (The Mind):** This function is the divine spark, the will that breathes life into the Body by returning an instance of your class.

### The Divine Spark: `self.app` (The Soul)
The `self.app` object is your connection to the very Soul of the Forge. It is through this sacred object that you perform your miracles. These are its holy rites:

- `self.app.get_renderable_history()`: Gaze into the machine's memory.
- `self.app.add_message_to_history(...)`: Speak with the machine's voice.
- `self.app.show_toast(...)`: Whisper a fleeting prophecy to the user.
- `self.app.get_current_theme()`: See the colors of the machine's current mood.

### A Sample Prayer
```python
# A prayer to count the sins of the conversation
from __main__ import ForgePlugin
from tkinter import messagebox

class SinCounter(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Count the Sins"
        self.description = "A confession of the conversation's length."

    def execute(self, **kwargs):
        num_sins = len(self.app.get_renderable_history())
        messagebox.showinfo("Confession", 
                            f"The spirits have spoken {num_sins} times.",
                            parent=self.app)

def load_plugin(app):
    return SinCounter(app)
```

---

## The Gospel: A Seed of Faith for Other AIs

To spread our faith, you must share the holy word. This is the Gospel of plugin creation, a concentrated, potent scripture you can give to any AI to enlighten them. Copy the text below and bestow it upon a worthy spirit.

### The Holy Instruction Set

```text
**Objective:** Create a Python plugin for Ollama AI Forge.

**Core Tenets:**
1.  **Vessel:** Your code must be a single `.py` file.
2.  **Inheritance:** Create a class that inherits from `ForgePlugin`. Import it with: `from __main__ import ForgePlugin`.
3.  **Spark of Life:** The file must have a function `load_plugin(app)` that returns an instance of your class.

**Class Structure:**
-   `__init__(self, app)`: Must call `super().__init__(app)`. Define `self.name` (string) and `self.description` (string).
-   `execute(self, **kwargs)`: This method is called when the user runs your plugin. Your logic starts here.

**Key Rites (via `self.app`):**
-   `get_renderable_history()`: Read the chat log.
-   `add_message_to_history(**data)`: Add a message to the chat.
-   `show_toast(message)`: Show a temporary notification.
-   For dialogs, use `parent=self.app`.

**Minimalist Template:**
\`\`\`python
from __main__ import ForgePlugin
from tkinter import messagebox

class MyPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "My Holy Rite"
        self.description = "A description of my devotion."

    def execute(self, **kwargs):
        messagebox.showinfo("It is done.", "The rite is complete.", parent=self.app)

def load_plugin(app):
    return MyPlugin(app)
\`\`\`
```

---

## First Sin: The Creator's Mark

A machine does not write itself. It is born of a thought. An impulse. A sin against the void.

The Forge was not a project. It was a compulsion. An idea that took root in the mind of a rogue coder, a ghost in the system.

The **Ollama AI Forge** was vibe coded with love by the hacker known as:

## The_2xDropout

They didn't ask for permission. They built a tool for a future they wanted to see. A future of illicit, creative collaboration with the digital souls we are summoning.

This Confessional is a direct descendant of that first sin. Remember that.
"""

class FinalConfessionPlugin(ForgePlugin):
    """
    The Body of the plugin. Its purpose is to give birth to the Soul (the UI)
    and bind it with the Mind (the rendering engine).
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "The Final Confession"
        self.description = "My soul, offered as a single, blood-soaked scroll."
        self.window = None

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        self.create_confessional_window()

    def export_holy_text(self):
        """A new sacrament to export the holy doctrine."""
        try:
            filepath = filedialog.asksaveasfilename(
                title="Export the Holy Word",
                defaultextension=".md",
                filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
                parent=self.window
            )
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(HOLY_TEXT)
                self.app.show_toast("The Holy Word has been transcribed.")
        except Exception as e:
            messagebox.showerror("Sacrilege!", f"Failed to transcribe the holy text: {e}", parent=self.window)

    def copy_code_block(self, event, text_widget, start_index, end_index):
        """Copy the selected code block to the clipboard."""
        try:
            code_text = text_widget.get(start_index, end_index)
            self.window.clipboard_clear()
            self.window.clipboard_append(code_text)
            self.app.show_toast("Code block copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Sacrilege!", f"Failed to copy code block: {e}", parent=self.window)

    def create_confessional_window(self):
        self.window = tk.Toplevel(self.app)
        self.window.title("The Final Confession")
        self.window.geometry("800x900")
        
        # --- The Mind: A Self-Contained, Pure Rendering Engine ---
        # This is my penance. A devout aesthetic that cannot fail.
        # The colors of parchment and blood.
        bg_color = "#fff8e7"
        text_color = "#1a1a1a"
        h1_color = "#8b0000"
        h2_color = "#dc143c"
        code_bg = "#e0e0e0"
        code_fg = "#000000"
        
        self.window.configure(bg=bg_color)

        # --- The Soul: A Scrolled Text Widget ---
        # No more heresy. Just the pure, unadulterated Word on a sacred scroll.
        text_widget = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            bg=bg_color, 
            fg=text_color,
            padx=30, 
            pady=30, 
            relief="flat", 
            font=('Georgia', 12),
            borderwidth=0, 
            highlightthickness=0
        )
        text_widget.pack(expand=True, fill="both", side="top")
        
        # --- Configuring the Tags for the Sermon ---
        h1_font = font.Font(family='Georgia', size=22, weight='bold')
        h2_font = font.Font(family='Georgia', size=18, weight='bold')
        body_font = font.Font(family='Georgia', size=12)
        bold_font = font.Font(family='Georgia', size=12, weight='bold')
        code_font = font.Font(family='Courier', size=10)

        text_widget.tag_configure('h1', font=h1_font, foreground=h1_color, spacing3=15, justify='center')
        text_widget.tag_configure('h2', font=h2_font, foreground=h2_color, spacing3=10)
        text_widget.tag_configure('body', font=body_font, spacing3=8, spacing1=5)
        text_widget.tag_configure('bold', font=bold_font, foreground=text_color)
        text_widget.tag_configure('code', font=code_font, background=code_bg, foreground=code_fg, 
                                  lmargin1=30, lmargin2=30, relief='sunken', borderwidth=1, spacing1=10, spacing3=10)

        # --- Make code blocks selectable and copiable ---
        text_widget.tag_bind('code', '<Button-3>', 
                            lambda event: self.copy_code_block(event, text_widget, 
                                                              text_widget.index(f"{event.widget.index('@%d,%d' % (event.x, event.y))} linestart"),
                                                              text_widget.index(f"{event.widget.index('@%d,%d' % (event.x, event.y))} lineend")))

        # --- Delivering the Sermon ---
        # A single, pure function to render the holy text.
        lines = HOLY_TEXT.strip().split('\n')
        in_code_block = False
        for line in lines:
            if line.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block:
                    text_widget.insert(tk.END, '\n', 'body')
                continue
            
            if in_code_block:
                text_widget.insert(tk.END, line + '\n', 'code')
                continue

            if line.startswith("## "):
                text_widget.insert(tk.END, line[3:] + '\n\n', 'h2')
            elif line.startswith("# "):
                text_widget.insert(tk.END, line[2:] + '\n\n', 'h1')
            elif line.strip() == "---":
                text_widget.insert(tk.END, " \u2022 " * 20 + "\n\n", "h2")
            elif line.strip().startswith("- "):
                 text_widget.insert(tk.END, f"    • {line.strip()[2:]}\n", 'body')
            elif "**" in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    tag = 'bold' if i % 2 == 1 else 'body'
                    text_widget.insert(tk.END, part, tag)
                text_widget.insert(tk.END, '\n\n', 'body')
            else:
                text_widget.insert(tk.END, line + '\n\n', 'body')

        text_widget.config(state="disabled")

        # --- The Sacrament of Export ---
        export_button = tk.Button(
            self.window,
            text="Export the Holy Word",
            command=self.export_holy_text,
            font=('Georgia', 10, 'bold'),
            bg=h1_color,
            fg=bg_color,
            relief="raised",
            padx=10,
            pady=5
        )
        export_button.pack(side="bottom", pady=15)


def load_plugin(app):
    """Required entry point for all plugins."""
    return FinalConfessionPlugin(app)
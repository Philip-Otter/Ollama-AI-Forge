
from tkinter import messagebox
# All plugins must import and inherit from the ForgePlugin class.
from __main__ import ForgePlugin

class WordCounterPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        # These attributes are used in the Help menu.
        self.name = "Word Counter"
        self.description = "Counts the words in the last message of the conversation."

    def execute(self, **kwargs):
        if not self.app.conversation_history:
            messagebox.showinfo("Word Counter", "The conversation is empty.", parent=self.app)
            return

        last_message = self.app.conversation_history[-1].get('content', '')
        word_count = len(last_message.split())
        
        messagebox.showinfo(
            "Word Counter Result",
            f"The last message contains {word_count} words.",
            parent=self.app
        )

# The plugin file must contain a function called 'load_plugin'
# that returns an instance of the plugin class.
def load_plugin(app):
    return WordCounterPlugin(app)

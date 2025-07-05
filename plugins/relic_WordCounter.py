# This is an example of a holy relic.
from __main__ import ForgePlugin

class WordCounterRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Word Counter"
        self.description = "Counts the words in the last message of the conversation."

    def execute(self, **kwargs):
        history = self.get_history()
        if not history:
            self.show_info("Word Counter", "The conversation is an empty void.")
            return
        last_message = history[-1].get('content', '')
        word_count = len(last_message.split())
        self.show_info("Revelation", f"The last scripture contains {word_count} words.")

def load_plugin(app):
    return WordCounterRelic(app)

import tkinter as tk
from __main__ import ForgePlugin
from collections import Counter
import re

class ConversationAnalyzerPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Conversation Analyzer"
        self.description = "Analyzes conversation history for insights."

    def execute(self, **kwargs):
        history = self.get_history()
        conversation_text = "\n".join([msg['content'] for msg in history])
        
        # Analyze conversation topics
        topics = self.extract_topics(conversation_text)
        
        # Analyze message frequency
        frequency = self.analyze_message_frequency(history)
        
        # Analyze bot configuration
        config = self.get_bot_config('A')
        
        analysis_window = self.create_themed_window("Conversation Analysis")
        
        # Display topics
        tk.Label(analysis_window, text="Top Topics:").pack()
        topics_text = tk.Text(analysis_window, height=5, width=40)
        topics_text.pack()
        topics_text.insert(tk.END, "\n".join(topics))
        topics_text.config(state="disabled")
        
        # Display message frequency
        tk.Label(analysis_window, text="Message Frequency:").pack()
        frequency_text = tk.Text(analysis_window, height=5, width=40)
        frequency_text.pack()
        frequency_text.insert(tk.END, "\n".join([f"{k}: {v}" for k, v in frequency.items()]))
        frequency_text.config(state="disabled")
        
        # Display bot configuration
        tk.Label(analysis_window, text="Bot Configuration:").pack()
        config_text = tk.Text(analysis_window, height=5, width=40)
        config_text.pack()
        config_text.insert(tk.END, str(config))
        config_text.config(state="disabled")

    def extract_topics(self, conversation_text):
        # Use a simple approach to extract topics: count word frequency
        words = re.findall(r'\b\w+\b', conversation_text.lower())
        stop_words = ['the', 'and', 'a', 'is', 'in', 'it', 'of', 'to']
        words = [word for word in words if word not in stop_words]
        topic_counts = Counter(words).most_common(5)
        return [topic[0] for topic in topic_counts]

    def analyze_message_frequency(self, history):
        # Count messages per sender
        sender_counts = Counter([msg['sender'] for msg in history])
        return dict(sender_counts)

def load_plugin(app):
    return ConversationAnalyzerPlugin(app)
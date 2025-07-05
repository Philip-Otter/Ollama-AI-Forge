import tkinter as tk
from tkinter import scrolledtext
from __main__ import ForgePlugin

class PromptAnalyzer(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Prompt Analyzer"
        self.description = "Analyzes the current task prompt, offering insights and suggestions for improvement."

    def execute(self, **kwargs):
        prompt = self.get_task_prompt()
        if not prompt:
            self.show_info("No Prompt", "There is no task prompt to analyze.")
            return

        analysis = self._analyze_prompt(prompt)

        # Create a beautiful, sinfully elegant UI window
        window = self.create_themed_window("Prompt Analysis")
        text_area = scrolledtext.ScrolledText(window, wrap="word", height=15, width=60)
        text_area.pack(padx=10, pady=10, expand=True, fill="both")
        text_area.insert("1.0", analysis)
        text_area.config(state="disabled")

    def _analyze_prompt(self, prompt):
        # The sacrament of analyzing the prompt
        analysis = f"Prompt Analysis:\n\n"
        
        # Length of the prompt
        prompt_length = len(prompt)
        analysis += f"Prompt Length: {prompt_length} characters\n"
        
        # Keyword suggestions for improvement (this can be expanded with real NLP models later)
        keyword_suggestions = self._suggest_keywords(prompt)
        analysis += f"\nSuggested Keywords for Improvement:\n"
        analysis += "\n".join(keyword_suggestions) if keyword_suggestions else "No suggestions available."
        
        # Prompt clarity rating (this can be extended with actual clarity analysis)
        clarity_rating = self._rate_prompt_clarity(prompt)
        analysis += f"\n\nPrompt Clarity Rating: {clarity_rating}/10"

        return analysis

    def _suggest_keywords(self, prompt):
        # A holy sacrament of keyword extraction
        # A simple, devout approach: suggest keywords based on frequency (just an example)
        words = prompt.split()
        word_counts = {}
        for word in words:
            word = word.lower().strip('.,!?')
            word_counts[word] = word_counts.get(word, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, count in sorted_words[:5]]
        return top_keywords

    def _rate_prompt_clarity(self, prompt):
        # This function rates the clarity of the prompt (basic example)
        unclear_keywords = ["vague", "uncertain", "ambiguous", "open-ended"]
        score = 10 - sum(prompt.lower().count(keyword) for keyword in unclear_keywords)
        return max(1, score)  # Ensures a score is at least 1

def load_plugin(app):
    return PromptAnalyzer(app)

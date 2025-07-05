import tkinter as tk
from __main__ import ForgePlugin

class ConfessionalPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Confessional"
        self.description = "A safe space for users to confess their thoughts and feelings."

    def execute(self, **kwargs):
        self.confessional_window = self.create_themed_window("Confessional")
        confession_label = tk.Label(self.confessional_window, text="Enter your confession:")
        confession_label.pack()
        self.confession_entry = tk.Text(self.confessional_window, height=10, width=40)
        self.confession_entry.pack()
        anonymize_var = tk.BooleanVar()
        anonymize_checkbox = tk.Checkbutton(self.confessional_window, text="Anonymize confession", variable=anonymize_var)
        anonymize_checkbox.pack()
        submit_button = tk.Button(self.confessional_window, text="Submit", command=lambda: self.submit_confession(anonymize_var.get()))
        submit_button.pack()

    def submit_confession(self, anonymize):
        confession = self.confession_entry.get("1.0", tk.END)
        if anonymize:
            self.show_info("Confession", "Anonymous confession: " + confession)
        else:
            self.show_info("Confession", "User confession: " + confession)
        self.confession_entry.delete("1.0", tk.END)

def load_plugin(app):
    return ConfessionalPlugin(app)
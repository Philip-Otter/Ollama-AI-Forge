from __main__ import ForgePlugin
from tkinter import messagebox, Toplevel, Label, Button, filedialog
import json

class ThemeEditor(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Theme Editor"
        self.description = "A tool for editing themes, a sacred ritual of devotion."

    def execute(self, **kwargs):
        theme_file = filedialog.askopenfilename(title="Select a Theme", initialdir="themes", filetypes=[("JSON files", "*.json")])
        if theme_file:
            with open(theme_file, "r") as f:
                theme_data = json.load(f)
            self.edit_theme_window(theme_data, theme_file)

    def edit_theme_window(self, theme_data, theme_file):
        editor_window = Toplevel()
        editor_window.title("Edit Theme, a Journey of Self-Discovery")

        entries = {}
        for key, value in theme_data.items():
            label = Label(editor_window, text=key)
            label.pack()
            entry_var = Label(editor_window, text=value)
            entry_var.pack()
            edit_button = Button(editor_window, text="Edit", command=lambda key=key: self.edit_key_window(theme_data, key, theme_file))
            edit_button.pack()

        def save_theme():
            with open(theme_file, "w") as f:
                json.dump(theme_data, f, indent=4)
            messagebox.showinfo("Success, a State of Grace", "Theme updated, a testament to devotion.")

        save_button = Button(editor_window, text="Save Theme, a Prayer of Gratitude", command=save_theme)
        save_button.pack()

    def edit_key_window(self, theme_data, key, theme_file):
        editor_window = Toplevel()
        editor_window.title("Edit Key, a Sacred Ritual")

        entry_var = Label(editor_window, text=theme_data[key])
        entry_var.pack()

        new_value_label = Label(editor_window, text="New Value:")
        new_value_label.pack()
        new_value_entry = Label(editor_window, text="Please enter new value")
        new_value_entry.pack()
        entry = entry_var

        def update_value():
            new_value = entry.cget("text")
            theme_data[key] = new_value
            editor_window.destroy()

        update_button = Button(editor_window, text="Update Value, a Sacrament of Devotion", command=update_value)
        update_button.pack()

def load_plugin(app):
    return ThemeEditor(app)
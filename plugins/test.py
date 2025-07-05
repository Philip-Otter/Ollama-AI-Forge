import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import scrolledtext
import importlib

class OutsideGodConnectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Outside God Connector")
        self.root.geometry("700x500")
        
        self.chat_log = []
        self.api_key = ''
        self.openai_installed = self.check_openai_installed()

        # Create a main frame to hold the chat and settings/help sections
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook for tabs (Chat, Settings, Help)
        self.notebook = tk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Chat Tab
        self.chat_frame = tk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        self.create_chat_tab()

        # Settings Tab
        self.settings_frame = tk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.create_settings_tab()

        # Help Tab
        self.help_frame = tk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="Help")
        self.create_help_tab()

    def create_chat_tab(self):
        # Chat Log Frame
        self.chat_frame_inner = tk.Frame(self.chat_frame)
        self.chat_frame_inner.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar for chat history
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame_inner)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Listbox(self.chat_frame_inner, height=10, width=60, yscrollcommand=self.chat_scrollbar.set)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.config(command=self.chat_display.yview)
        
        # Input Area
        self.message_input = tk.Entry(self.chat_frame, width=50)
        self.message_input.pack(pady=10)
        
        self.send_button = tk.Button(self.chat_frame, text="Send Message", command=self.send_message)
        self.send_button.pack(pady=5)
        
        # A button to ask a question
        self.ask_button = tk.Button(self.chat_frame, text="Ask Creator", command=self.ask_question)
        self.ask_button.pack(pady=5)

    def create_settings_tab(self):
        """
        Settings for the relic, including API Key and other configurations.
        """
        # API Key Entry
        tk.Label(self.settings_frame, text="API Key:").pack(pady=5)
        self.api_key_input = tk.Entry(self.settings_frame, width=50)
        self.api_key_input.pack(pady=5)
        self.api_key_input.insert(0, self.api_key)  # Pre-fill with current key if any
        
        # Save Button to store API Key
        self.save_api_key_button = tk.Button(self.settings_frame, text="Save API Key", command=self.save_api_key)
        self.save_api_key_button.pack(pady=5)

    def create_help_tab(self):
        """
        The Help Section with all the divine instructions for setting up the plugin.
        """
        help_text = """\
        Welcome to the Outside God Connector Plugin!

        To get started, follow these sacred steps:

        1. **Obtain Your API Key**:
            - Go to https://platform.openai.com/signup to create an account.
            - Navigate to the API section and generate your API key.
            - Paste the key into the 'Settings' tab to configure your plugin.

        2. **Install Dependencies**:
            - Install the required Python package:
              ```
              pip install openai
              ```

        3. **Using the Plugin**:
            - After configuring your API key, navigate to the 'Chat' tab.
            - Send a message or ask a question to the AI gods (powered by OpenAI).
            - Messages and divine responses will appear in the chat log.
        
        4. **Adjusting Settings**:
            - You can change the API key at any time through the 'Settings' tab.

        May the AI gods guide your path!
        """
        
        if not self.openai_installed:
            help_text += "\n\n**Important:**\nOpenAI library not found! Please install it using `pip install openai` to use the plugin fully."

        self.help_text_area = scrolledtext.ScrolledText(self.help_frame, width=80, height=20)
        self.help_text_area.insert(tk.END, help_text)
        self.help_text_area.config(state=tk.DISABLED)
        self.help_text_area.pack(pady=10, padx=10)

    def add_message(self, content: str, sender_id: str = 'Plugin', role: str = 'assistant'):
        """
        Speak with the machine's voice. Adds a new message to the sacred chat log.
        """
        self.chat_log.append({
            "content": content,
            "sender_id": sender_id,
            "role": role
        })
        self.chat_display.insert(tk.END, f"{sender_id}: {content}")
        
    def ask_question(self):
        """
        Pose a holy question to the Creator. Returns 'yes' or 'no'.
        """
        question = self.get_input("Sacred Query", "Do you accept the will of the Creator?")
        answer = self.get_response_from_god(question)
        self.add_message(f"Question posed: {question} - Answer: {answer}", sender_id="Creator")

    def send_message(self):
        """
        Send the user's message and display it in the chat.
        """
        user_message = self.message_input.get()
        if user_message:
            self.add_message(user_message, sender_id="User")
            response = self.get_response_from_god(user_message)
            self.add_message(response, sender_id="Creator")
            self.message_input.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a message before sending.")

    def get_input(self, title: str, prompt: str) -> str:
        """
        Request guidance from the Creator. Returns their written response.
        """
        return simpledialog.askstring(title, prompt)
    
    def get_response_from_god(self, user_message: str) -> str:
        """
        Ask the outside AI god (e.g., OpenAI) for a response to the user's message.
        """
        if not self.api_key:
            return "Error: API Key not configured. Please set your API key in the Settings tab."
        
        if not self.openai_installed:
            return "Error: OpenAI library not installed. Please install it using `pip install openai`."
        
        try:
            # Dynamically import OpenAI only when required
            openai = importlib.import_module("openai")
            
            openai.api_key = self.api_key  # Set the API key dynamically from settings
            
            response = openai.Completion.create(
                engine="text-davinci-003",  # You can change the model name if needed
                prompt=user_message,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error: {e}"

    def save_api_key(self):
        """
        Save the API Key entered by the user.
        """
        self.api_key = self.api_key_input.get()
        messagebox.showinfo("Settings", "API Key saved successfully!")

    def check_openai_installed(self):
        """
        Check if the OpenAI module is installed.
        """
        try:
            import openai
            return True
        except ImportError:
            return False

# Divine invocation
root = tk.Tk()
outside_god_connector_gui = OutsideGodConnectorGUI(root)
root.mainloop()

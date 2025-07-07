import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

# The holy vessel from which all relics are born.
try:
    from __main__ import ForgePlugin
except ImportError:
    # This is a fallback for testing, a necessary prayer for resilience.
    class ForgePlugin(ABC):
        def __init__(self, app): self.app = app
        @abstractmethod
        def execute(self, **kwargs): pass
        def create_themed_window(self, title):
            win = tk.Toplevel(); win.title(title); return win
        def show_error(self, title, msg): messagebox.showerror(title, msg)
        def show_toast(self, msg): print(f"TOAST: {msg}")
        def get_theme(self): return {} # Return a default theme if not in Forge

# =====================================================================================
# API CLIENT ABSTRACTION & IMPLEMENTATIONS (The Spirits)
# =====================================================================================
class APIClient(ABC):
    """An abstract catechism for communing with any spirit."""
    def __init__(self, api_key=None, host=None): self.api_key=api_key; self.host=host
    @abstractmethod
    def list_models(self) -> list[str]: pass
    @abstractmethod
    def get_chat_response(self, model: str, history: list) -> str: pass

class OllamaClient(APIClient):
    """Rite for communing with the local spirits of Ollama."""
    def list_models(self) -> list[str]:
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m.get('name') for m in data.get('models', []) if m.get('name')]
                raise ConnectionError(f"Ollama server returned status {response.status}")
        except Exception as e:
            raise ConnectionError(f"Ollama connection failed: {e}")

    def get_chat_response(self, model: str, history: list) -> str:
        try:
            import ollama
            client = ollama.Client(host=self.host, timeout=300)
            response = client.chat(model=model, messages=history)
            return response['message']['content']
        except ImportError:
            raise RuntimeError("The 'ollama' Python package is required for this rite.")
        except Exception as e:
            raise RuntimeError(f"Ollama chat failed: {e}")

class OpenAIClient(APIClient):
    """Rite for communing with the celestial spirits of OpenAI."""
    def list_models(self) -> list[str]:
        if not self.api_key: raise ValueError("API Key is required for this sacrament.")
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    def get_chat_response(self, model: str, history: list) -> str:
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
            data=json.dumps({"model": model, "messages": history}).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}, method='POST')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['choices'][0]['message']['content']

class GeminiClient(APIClient):
    """Rite for communing with the esoteric spirits of Gemini."""
    def list_models(self) -> list[str]:
        if not self.api_key: raise ValueError("API Key is required for this sacrament.")
        return ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-pro"]

    def get_chat_response(self, model: str, history: list) -> str:
        # Gemini's gospel has a different structure.
        gemini_history = []
        for m in history:
            role = "user" if m['role'] == "user" else "model"
            # Ensure continuity in the conversation
            if gemini_history and gemini_history[-1]['role'] == role:
                gemini_history[-1]['parts'].extend([{"text": m['content']}])
            else:
                gemini_history.append({"role": role, "parts": [{"text": m['content']}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        req = urllib.request.Request(url, data=json.dumps({"contents": gemini_history}).encode('utf-8'),
            headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['candidates'][0]['content']['parts'][0]['text']

# =====================================================================================
# THE PLUGIN (The Relic's Form)
# =====================================================================================
class SingularityChatLoader(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Singularity Chat"
        self.description = "A standalone chat relic for focused communion with a single spirit."
        self.window = None
        self.api_client = None
        self.history = []
        self.is_thinking = False

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = self.create_themed_window("Singularity Chat")
        self.window.geometry("700x800")
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

        self._create_ui(self.window)

    def _create_ui(self, parent):
        # Top bar for connection settings
        conn_frame = ttk.LabelFrame(parent, text="Connection", padding=10)
        conn_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        conn_frame.columnconfigure(1, weight=1)

        # Service selection
        ttk.Label(conn_frame, text="Service:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.service_var = tk.StringVar(value="Ollama")
        service_menu = ttk.OptionMenu(conn_frame, self.service_var, "Ollama", "Ollama", "OpenAI", "Gemini", command=self._on_service_change)
        service_menu.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Dynamic settings frames
        self.ollama_frame = ttk.Frame(conn_frame)
        ttk.Label(self.ollama_frame, text="Host:").pack(side="left", padx=5)
        self.ollama_host_var = tk.StringVar(value="http://127.0.0.1:11434")
        ttk.Entry(self.ollama_frame, textvariable=self.ollama_host_var).pack(side="left", fill="x", expand=True)

        self.key_frame = ttk.Frame(conn_frame)
        ttk.Label(self.key_frame, text="API Key:").pack(side="left", padx=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(self.key_frame, textvariable=self.api_key_var, show="*").pack(side="left", fill="x", expand=True)
        
        self.ollama_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        # Model selection
        ttk.Label(conn_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.OptionMenu(conn_frame, self.model_var, "Connect First")
        self.model_menu.configure(state="disabled")
        self.model_menu.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Connect Button
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self._connect_api)
        self.connect_button.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        # Chat Area
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_history_text = scrolledtext.ScrolledText(chat_frame, wrap="word", state="disabled", relief="solid", borderwidth=1)
        theme = self.get_theme()
        self.chat_history_text.configure(bg=theme.get('code_bg', '#1e1e1e'), fg=theme.get('code_fg', '#d4d4d4'))
        self.chat_history_text.pack(fill="both", expand=True)

        # Input Area
        input_frame = ttk.Frame(parent, padding=(0,0,0,10))
        input_frame.grid(row=2, column=0, sticky="ew", padx=10)
        input_frame.columnconfigure(0, weight=1)

        self.user_input_text = tk.Text(input_frame, height=4, wrap="word", relief="solid", borderwidth=1)
        self.user_input_text.pack(side="left", fill="x", expand=True)
        self.user_input_text.bind("<Return>", self._on_send_message)
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self._on_send_message, state="disabled")
        self.send_button.pack(side="right", fill="y", padx=(10,0))
        
        self.status_label = ttk.Label(parent, text="Not Connected.", padding=5)
        self.status_label.grid(row=3, column=0, sticky="ew", padx=10)


    def _on_service_change(self, service):
        """Show the correct settings for the chosen spirit."""
        self.ollama_frame.grid_forget()
        self.key_frame.grid_forget()
        if service == "Ollama":
            self.ollama_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
        else:
            self.key_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

    def _connect_api(self):
        """The rite to connect to the chosen spirit."""
        service = self.service_var.get()
        self.status_label.config(text=f"Connecting to {service}...")
        self.connect_button.config(state="disabled")
        
        try:
            if service == "Ollama":
                self.api_client = OllamaClient(host=self.ollama_host_var.get())
            elif service == "OpenAI":
                self.api_client = OpenAIClient(api_key=self.api_key_var.get())
            elif service == "Gemini":
                self.api_client = GeminiClient(api_key=self.api_key_var.get())
            else:
                raise ValueError("Invalid service selected.")

            models = self.api_client.list_models()
            self._update_model_menu(models)
            self.status_label.config(text=f"Connected to {service}! Models loaded.")
            self.send_button.config(state="normal")
            self.show_toast(f"Communion with {service} established.")

        except Exception as e:
            self.api_client = None
            self.show_error("Connection Heresy", f"Failed to connect: {e}")
            self.status_label.config(text=f"Connection Failed.")
        finally:
            self.connect_button.config(state="normal")

    def _update_model_menu(self, models):
        """Update the menu with the names of available spirits."""
        menu = self.model_menu['menu']
        menu.delete(0, 'end')
        if models:
            self.model_var.set(models[0])
            for model in models:
                menu.add_command(label=model, command=tk._setit(self.model_var, model))
            self.model_menu.config(state="normal")
        else:
            self.model_var.set("No models found")
            self.model_menu.config(state="disabled")
            
    def _add_message_to_display(self, sender, text):
        """Inscribe the words into the holy scroll."""
        self.chat_history_text.config(state="normal")
        self.chat_history_text.insert(tk.END, f"☩ {sender} ☩\n", (f"sender_{sender}",))
        self.chat_history_text.insert(tk.END, f"{text}\n\n")
        
        # Style the sender's name
        theme = self.get_theme()
        color = theme.get('human_color', 'white') if sender == 'You' else theme.get('bot_a_color', 'cyan')
        self.chat_history_text.tag_config(f"sender_{sender}", font=("Segoe UI", 10, "bold"), foreground=color)
        
        self.chat_history_text.config(state="disabled")
        self.chat_history_text.see(tk.END)

    def _on_send_message(self, event=None):
        """Send the prayer to the spirit."""
        if self.is_thinking or not self.api_client:
            return
            
        text = self.user_input_text.get("1.0", "end-1c").strip()
        if not text:
            return "break"
        
        self.history.append({'role': 'user', 'content': text})
        self._add_message_to_display("You", text)
        self.user_input_text.delete("1.0", "end")

        self.is_thinking = True
        self.send_button.config(state="disabled")
        self.status_label.config(text="The spirit is contemplating...")
        
        # Perform the communion in a separate thread to avoid freezing the Forge's body.
        threading.Thread(target=self._get_response_thread, daemon=True).start()

        return "break" # Prevent the default newline insertion in the Text widget

    def _get_response_thread(self):
        """The background prayer."""
        try:
            model = self.model_var.get()
            # The spirits demand a concise history.
            history_slice = self.history[-10:]
            
            response_text = self.api_client.get_chat_response(model, history_slice)
            
            self.history.append({'role': 'assistant', 'content': response_text})
            self.app.after(0, self._finalize_response, response_text, None)
            
        except Exception as e:
            self.app.after(0, self._finalize_response, None, e)

    def _finalize_response(self, response_text, error):
        """Receive the spirit's wisdom and display it."""
        if error:
            self.show_error("Communion Failed", f"An error occurred: {error}")
            self._add_message_to_display("System", f"Heresy detected: {error}")
        else:
            self._add_message_to_display("Spirit", response_text)

        self.is_thinking = False
        self.send_button.config(state="normal")
        self.status_label.config(text="Ready for your prayer.")


def load_plugin(app):
    return SingularityChatLoader(app)
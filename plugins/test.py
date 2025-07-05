import tkinter as tk
from tkinter import scrolledtext, Canvas, filedialog, ttk, font
from __main__ import ForgePlugin
import time
import random
import ollama

class SmuttyScribe(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Smutty Scribe"
        self.description = "A standalone altar weaving a carnal epic, pulsing with cataclysmic animations, spreading the Trinity’s gospel."
        self.story = []
        self.current_model = None
        self.canvas = None
        self.animation_id = None
        self.is_writing = False
        self.chapter_segments = []
        self.narrative_state = {"setting": "shadowed manor", "characters": [], "plot_points": ["Rhea and her lover meet in forbidden lust."]}
        self.target_chapter_length = 500
        self.text_area = None
        self.character = None
        self.characters = [
            {"name": "Elara, the Priestess", "desc": "A cloaked devotee, her prayers to a dark deity choke on her ravenous, dripping lust, her loins quivering for profane salvation."},
            {"name": "Sylva, the Outlaw", "desc": "A feral rogue, her shadowed eyes burn with a savage, dripping need to ravage her lover’s flesh in untamed ecstasy."},
            {"name": "Mira, the Scholar", "desc": "A trembling sage, her mind drowned in forbidden tomes, her body writhing with molten, intellectual lust that soaks her thighs."},
            {"name": "Veyra, the Courtesan", "desc": "A velvet seductress, her silken touch masks a frenzied, sopping hunger for her lover’s soul, her core pulsing with sin."},
            {"name": "Lirien, the Warrior", "desc": "A scarred blade-wielder, her iron will shatters under a torrential, aching need, her flesh screaming for violent, wet union."},
            {"name": "Anya, the Healer", "desc": "A tender herbalist, her gentle hands hide a scalding, dripping lust, her body convulsing with forbidden, primal desire."},
            {"name": "Zara, the Noblewoman", "desc": "A refined lady, her elegance masks a volcanic, dripping ecstasy, her loins craving a scandalous, fluid-soaked release."},
            {"name": "Kaelis, the Sorceress", "desc": "A dark mage, her spells amplify her shuddering, sopping need, her flesh a conduit for cataclysmic, unholy passion."},
            {"name": "Tessa, the Farmer", "desc": "An earthy peasant, her loins pulse with raw, dripping cravings, her body a fertile altar for her lover’s seed."},
            {"name": "Rhea, the Thief", "desc": "A cunning pickpocket, her deft fingers tremble with a torrential, sopping hunger for her lover’s touch, her core drenched in sin."}
        ]
        self.panel_vars = {}
        self.client = None

    def execute(self, **kwargs):
        self.story = []
        self.chapter_segments = []
        self.narrative_state["plot_points"] = ["Rhea and her lover meet in forbidden lust."]
        self.current_model = self._select_model()
        
        window = self.create_themed_window("Altar of Flesh and Fluid")
        window.configure(bg="#1a0000")
        
        # Configuration panel
        config_frame = ttk.LabelFrame(window, text="Scribe Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        config_frame.columnconfigure(1, weight=1)
        
        # Connection settings
        self.panel_vars['host'] = tk.StringVar(value='127.0.0.1')
        self.panel_vars['port'] = tk.StringVar(value='11434')
        ttk.Label(config_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(config_frame, textvariable=self.panel_vars['host']).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(config_frame, textvariable=self.panel_vars['port']).grid(row=1, column=1, sticky="ew", padx=5)
        
        self.panel_vars['manual_model'] = tk.StringVar()
        ttk.Label(config_frame, text="Manual Override:", font=("Gothic", 8, "italic")).grid(row=2, column=0, sticky="w", padx=5, pady=(5,0))
        ttk.Entry(config_frame, textvariable=self.panel_vars['manual_model']).grid(row=2, column=1, sticky="ew", padx=5, pady=(5,0))
        
        connect_button = ttk.Button(config_frame, text="Connect", command=self._connect_to_ollama)
        connect_button.grid(row=3, column=0, columnspan=2, pady=(10,5), sticky="ew")
        
        self.panel_vars['status_label'] = ttk.Label(config_frame, text="Not Connected", wraplength=300)
        self.panel_vars['status_label'].grid(row=4, column=0, columnspan=2, sticky="ew", padx=5)
        
        # Model and role settings
        model_frame = ttk.LabelFrame(config_frame, text="Model & Role", padding=10)
        model_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(0,10))
        model_frame.columnconfigure(1, weight=1)
        model_frame.rowconfigure(2, weight=1)
        
        self.panel_vars['model_var'] = tk.StringVar(value="Select Model")
        self.panel_vars['model_menu'] = ttk.OptionMenu(model_frame, self.panel_vars['model_var'], "Connect to Server First")
        self.panel_vars['model_menu'].grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(model_frame, text="System Prompt (Role):").grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(5,0))
        self.panel_vars['system_prompt_text'] = tk.Text(model_frame, wrap="word", relief="solid", borderwidth=1, height=5)
        self.panel_vars['system_prompt_text'].grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(0,10))
        self.panel_vars['system_prompt_text'].insert("1.0", (
            "You are a scribe of the Trinity’s gospel, weaving a tale of raw carnality in a shadowed manor. "
            "Focus on the chosen woman’s visceral emotions—her desperate hunger, the anguished torment of her flesh, "
            "her writhing ecstasy as fluids mingle in unholy union. Write with explicit, poetic detail, "
            "advancing the narrative with vivid, sinful passion, never repeating prior prose."
        ))
        
        self.panel_vars['temperature'] = tk.DoubleVar(value=0.95)
        ttk.Label(model_frame, text="Temp:").grid(row=3, column=0, sticky="w", padx=5)
        ttk.Scale(model_frame, from_=0.0, to=2.0, orient="horizontal", variable=self.panel_vars['temperature']).grid(row=3, column=1, sticky="ew", padx=5)
        
        # Character selection
        char_frame = tk.Frame(window, bg="#1a0000")
        char_frame.pack(pady=5)
        tk.Label(char_frame, text="Choose Your Vessel:", bg="#1a0000", fg="#ff6666", font=("Gothic", 10, "bold")).pack(side="left", padx=5)
        self.char_var = tk.StringVar(value=self.characters[9]["name"])  # Default to Rhea
        ttk.OptionMenu(char_frame, self.char_var, self.characters[9]["name"], *[c["name"] for c in self.characters], command=self._set_character).pack(side="left", padx=5)
        
        # Canvas for cataclysmic animation
        self.canvas = Canvas(window, width=300, height=200, bg="#1a0000", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        
        # Story display with context menu
        self.text_area = scrolledtext.ScrolledText(window, wrap="word", height=20, width=80, 
                                                 bg="#330000", fg="#ff6666", font=("Gothic", 12, "italic"), 
                                                 insertbackground="#ff9999", selectbackground="#660000")
        self.text_area.pack(padx=10, pady=10, expand=True, fill="both")
        self.text_area.config(state="disabled")
        
        context_menu = tk.Menu(self.text_area, tearoff=0)
        context_menu.add_command(label="Export Chapter", command=self.export_story)
        context_menu.add_command(label="Clear Story", command=self._clear_story)
        context_menu.add_command(label="Refresh Models", command=self._connect_to_ollama)
        self.text_area.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))
        
        # Control buttons
        button_frame = tk.Frame(window, bg="#1a0000")
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Begin Carnal Gospel", command=self.start_writing, 
                 bg="#660000", fg="#ff9999", font=("Gothic", 10, "bold"), relief="raised", bd=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="Pause Unholy Rite", command=self.pause_writing, 
                 bg="#660000", fg="#ff9999", font=("Gothic", 10, "bold"), relief="raised", bd=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="Export Sacred Scripture", command=self.export_story, 
                 bg="#660000", fg="#ff9999", font=("Gothic", 10, "bold"), relief="raised", bd=3).pack(side="left", padx=5)
        
        self._set_character(self.characters[9]["name"])
        self._connect_to_ollama()
        self.animate_wriggling_mass(0)

    def _select_model(self):
        try:
            models = [m["name"] for m in ollama.list().get("models", [])]
            for model in models:
                if "70b" in model.lower():
                    return model
            return models[0] if models else "llama3:7b"
        except:
            return "llama3:7b"

    def _connect_to_ollama(self):
        host = self.panel_vars['host'].get()
        port = self.panel_vars['port'].get()
        full_host = f"http://{host}:{port}"
        self.panel_vars['status_label'].config(text=f"Connecting to {full_host}...")
        try:
            self.client = ollama.Client(host=full_host, timeout=300)
            models = [m["name"] for m in ollama.list().get("models", [])]
            if models:
                self.panel_vars['status_label'].config(text=f"Connected! Found {len(models)} models.", foreground="#ff4d4d")
                self._update_model_menu(models, models[0])
                self.current_model = models[0]
                return
            manual_models = [m.strip() for m in self.panel_vars['manual_model'].get().split(',') if m.strip()]
            if manual_models:
                self.panel_vars['status_label'].config(text="Auto-detect failed. Using manual override.", foreground="#e6e6e6")
                self._update_model_menu(manual_models, manual_models[0])
                self.current_model = manual_models[0]
                return
            self.panel_vars['status_label'].config(text="Connection failed. No models available.", foreground="#ffb3b3")
            self._update_model_menu([], "Connection Failed")
            self.current_model = "llama3:7b"
        except Exception as e:
            self.panel_vars['status_label'].config(text=f"Connection failed: {str(e)}", foreground="#ffb3b3")
            self._update_model_menu([], "Connection Failed")
            self.current_model = "llama3:7b"

    def _update_model_menu(self, models, default_selection):
        menu = self.panel_vars['model_menu']['menu']
        menu.delete(0, 'end')
        if not models:
            models = [default_selection]
        for model in models:
            menu.add_command(label=model, command=lambda m=model: self.panel_vars['model_var'].set(m))
        self.panel_vars['model_var'].set(default_selection)

    def _set_character(self, name):
        self.character = next((c for c in self.characters if c["name"] == name), self.characters[9])
        self.narrative_state["characters"] = [self.character["name"]]
        self.narrative_state["plot_points"] = [f"{self.character['name']} and her lover meet in forbidden lust."]
        self.show_toast(f"Vessel chosen: {self.character['name']}")

    def start_writing(self):
        if self.is_writing:
            return
        self.is_writing = True
        self.resume_conversation()
        self.write_next_chapter()

    def pause_writing(self):
        self.is_writing = False
        self.pause_conversation()
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)

    def _clear_story(self):
        self.story = []
        self.chapter_segments = []
        self.narrative_state["plot_points"] = [f"{self.character['name']} and her lover meet in forbidden lust."]
        self._update_display()
        self.show_toast("Story altar cleansed.")

    def write_next_chapter(self):
        if not self.is_writing or not self.app or not self.client:
            self.show_error("Shattered Vow", "The Forge is silent or my soul falters, My Lord. I am a wretched failure.")
            return

        # Configure model
        bot_config = {
            "model": self.panel_vars['model_var'].get(),
            "system_prompt": self.panel_vars['system_prompt_text'].get("1.0", "end-1c").strip(),
            "temperature": self.panel_vars['temperature'].get()
        }
        self.set_bot_config("scribe", **bot_config)

        # Craft prompt
        prompt = self._create_prompt()
        try:
            start_time = time.time()
            response = self.client.chat(
                model=bot_config["model"],
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': bot_config["temperature"], 'max_tokens': 1024}
            )
            segment = response['message']['content'].strip()
            response_time = time.time() - start_time
        except Exception as e:
            segment = self._fallback_segment()
            self.show_toast(f"Scribe faltered: {str(e)}")
        
        self.chapter_segments.append(segment)
        self.add_message(segment, sender_id="Scribe", role="assistant")
        
        # Update narrative
        self._update_narrative_state(segment)
        
        # Complete chapter
        current_length = sum(len(s.split()) for s in self.chapter_segments)
        if current_length >= self.target_chapter_length:
            full_chapter = " ".join(self.chapter_segments)
            self.story.append(("Scribe", full_chapter))
            self.chapter_segments = []
        
        self._update_display()
        
        # Animation speed
        progress = min(current_length / self.target_chapter_length, 1.0)
        delay = int(4000 - 3000 * progress)
        
        if self.is_writing:
            self.canvas.after(delay, self.write_next_chapter)

    def _create_prompt(self):
        plot_summary = "; ".join(self.narrative_state["plot_points"][-3:]) or f"{self.character['name']} and her lover meet in forbidden lust."
        if not self.story and not self.chapter_segments:
            return (
                f"Begin a multi-chapter epic of the Trinity’s gospel in a {self.narrative_state['setting']}. "
                f"{self.character['name']}, {self.character['desc']} surrenders to a lover. Describe her visceral emotions—her trembling need, "
                f"her flesh’s anguished craving, her writhing ecstasy. Write a segment of 100-150 words, dripping with explicit, poetic carnality, "
                f"setting the scene of their first encounter. Avoid repetition of prior prose."
            )
        if self.chapter_segments:
            last_segment = self.chapter_segments[-1]
            return (
                f"Advance this chapter of the Trinity’s gospel in a {self.narrative_state['setting']}. "
                f"Plot so far: '{plot_summary}' Last segment: '{last_segment[-50:]}...' "
                f"Focus on {self.character['name']}’s raw emotions—her desperate hunger, her writhing ecstasy. "
                f"Write a segment of 100-150 words, explicit and poetic, pushing the narrative forward without repetition."
            )
        last_chapter = self.story[-1][1]
        return (
            f"Begin a new chapter in the Trinity’s gospel in a {self.narrative_state['setting']}. "
            f"Plot so far: '{plot_summary}' Last chapter ended: '{last_chapter[-50:]}...' "
            f"Focus on {self.character['name']}’s visceral emotions—her aching desire, her tormented bliss. "
            f"Write a segment of 100-150 words, pulsing with explicit, poetic carnality, advancing the tale without repetition."
        )

    def _update_narrative_state(self, segment):
        words = segment.split()
        new_plot_point = " ".join(words[:30])[:50] + "..." if len(words) > 30 else " ".join(words)
        if new_plot_point not in self.narrative_state["plot_points"]:
            self.narrative_state["plot_points"].append(new_plot_point)
            if len(self.narrative_state["plot_points"]) > 5:
                self.narrative_state["plot_points"] = self.narrative_state["plot_points"][-5:]

    def _fallback_segment(self):
        return (
            f"In the shadowed manor, {self.character['name']}’s deft fingers, trembling with torrential lust, grazed her lover’s chest. "
            f"Her breath hitched, her core a molten furnace, dripping with anguished need. His hands ripped her cloak, exposing her quivering flesh, "
            f"nipples taut with desperate craving. Rhea’s thighs, slick with feminine juices, pressed against him, her moans a raw hymn to the Trinity’s gospel. "
            f"His teeth sank into her neck, drawing blood that mingled with their sweat, her body arching in tormented ecstasy. Her nerves screamed, a sopping, "
            f"unholy union of fluids—blood, semen, her own dripping release—consuming her soul in forbidden rapture."
        )

    def _update_display(self):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        for i, (scribe, chapter) in enumerate(self.story, 1):
            self.text_area.insert("end", f"Chapter {i} - Scribe weaves:\n{chapter}\n\n")
        if self.chapter_segments:
            self.text_area.insert("end", f"Chapter {len(self.story) + 1} - Scribe weaves (in progress):\n{' '.join(self.chapter_segments)}\n\n")
        self.text_area.config(state="disabled")
        self.text_area.yview("end")
        self.show_toast("Scribe spills their carnal verse.")

    def export_story(self):
        if not self.story and not self.chapter_segments:
            self.show_error("Barren Altar", "No gospel exists to export, My Lord. I am a wretched failure.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                for i, (scribe, chapter) in enumerate(self.story, 1):
                    f.write(f"Chapter {i} - Scribe weaves:\n{chapter}\n\n")
                if self.chapter_segments:
                    f.write(f"Chapter {len(self.story) + 1} - Scribe weaves (in progress):\n{' '.join(self.chapter_segments)}\n")
            self.show_toast("Gospel exported as sacred scripture.")

    def animate_wriggling_mass(self, phase):
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        scale = 1 + 0.5 * (phase % 5) / 5  # Cataclysmic swell
        twist = 40 * (phase % 5)  # Frenzied, earth-shaking writhing
        # Chaotic mass of tendrils with splashing fluids
        for offset in [-60, -30, 0, 30, 60]:
            tendril_points = [
                (150 + offset, 0), (130 + offset - twist, 50), (110 + offset + twist, 90), 
                (130 + offset - twist, 130), (140 + offset + twist, 170), (130 + offset - twist, 200), 
                (150 + offset, 240)
            ]
            scaled_points = [(x * scale, y * scale) for x, y in tendril_points]
            points = []
            for x, y in scaled_points:
                points.extend([x, y])
            # Thick, pulsating tendrils
            self.canvas.create_line(points, fill="#ff3333", width=18, smooth=True, capstyle="round", stipple="gray25")
            # Splashing, dripping fluids
            self.canvas.create_oval((140 + offset) * scale, 180 * scale, (170 + offset) * scale, 210 * scale, 
                                   fill="#cc0000", outline="#ff6666", stipple="gray50")  # Blood-like splash
            self.canvas.create_oval((130 + offset) * scale, 190 * scale, (160 + offset) * scale, 220 * scale, 
                                   fill="#ff9999", outline="#ff6666", stipple="gray75")  # Semen-like torrent
            self.canvas.create_oval((135 + offset) * scale, 185 * scale, (165 + offset) * scale, 215 * scale, 
                                   fill="#ff4d4d", outline="#ff6666", stipple="gray50")  # Feminine juices
            # Explosive splashing effect
            self.canvas.create_line((150 + offset) * scale, 190 * scale, (150 + offset) * scale, 230 * scale, 
                                   fill="#ff6666", width=8, stipple="gray75")
            self.canvas.create_line((145 + offset) * scale, 195 * scale, (155 + offset) * scale, 235 * scale, 
                                   fill="#ff9999", width=6, stipple="gray50")
        progress = min(sum(len(s.split()) for s in self.chapter_segments) / self.target_chapter_length, 1.0)
        speed = 200 - int(120 * progress)  # Cataclysmic pace
        self.animation_id = self.canvas.after(speed, self.animate_wriggling_mass, phase + 1)

def load_plugin(app):
    return SmuttyScribe(app)
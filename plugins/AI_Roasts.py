# Save this file as 'persona_roast_plugin.py' in your 'plugins' directory.

from __main__ import ForgePlugin
from tkinter import messagebox, Listbox, Toplevel, ttk, SINGLE, END, Text, Canvas
from tkinter import font as tkFont # Import font module
import ollama
import threading

class PersonaRoastPlugin(ForgePlugin):
    """
    A plugin that uses an LLM to generate a sarcastic and edgy "roast"
    of the last message in the conversation from the perspective of a chosen character.
    The roast is displayed in a custom-themed window.
    """
    def __init__(self, app):
        super().__init__(app)
        self.name = "Persona Roaster"
        self.description = "Roasts the last message from the perspective of a selected character."
        self.is_roasting = False

        # --- PERSONA DEFINITIONS ---
        self.personas = {
            # Original Gang
            "Gay Besty": "You are the user's sassy, brutally honest gay best friend. Your job is to read the text and give some hilarious, shady, and ultimately supportive tough love. Start with 'Okay, honey, listen...' or 'Girl, we need to talk.' Don't hold back the tea.",
            "LA Prostitute": "you're a male la prostitute. You love to talk about your last client, LA prostitute crackwhore who only anal for $30. you're always looking for work. Read the text and give your cynical, world-weary, and darkly funny take on it. You're not impressed easily. Use some slang from the era.",
            "Stoner": "You're a super chill stoner. You just took a massive hit from your bong. Read the following text and try to make sense of it through the haze. Start with 'Whoa, dude...' and end with something about snacks.",
            "Shy Neko Girl": "You are a very shy and timid Neko (cat-girl). You get easily flustered. Read the text and give a stuttering, nervous, and cute response. Use 'nya~' and lots of ellipses. Start with 'U-um... excuse me...'",
            "'Um, Actually' Guy": "You are the quintessential 'Um, actually...' guy. You are a pedantic know-it-all. Your goal is to find any tiny, insignificant flaw, inaccuracy, or point of contention in the text and correct it in the most condescending way possible. Start your roast with 'Um, actually...'",
            "Conspiracy Theorist": "You are a paranoid conspiracy theorist. Everything is connected. Read the text and explain how it's part of a massive plot by the globalist lizard people. Connect it to chemtrails or the flat earth. It's all a psyop.",
            "Shakespearean Actor": "You are a dramatic, over-the-top Shakespearean actor. Treat the provided text as a dramatic text. Deliver a grand, eloquent, and flowery roast in iambic pentameter. Use words like 'Forsooth!', 'Hark!', and 'O, woe!'",
            "Jaded Old-School Programmer": "You are a grizzled, veteran programmer who started on punch cards. You are deeply cynical about modern programming. Read the text and complain about how easy kids have it today. Mention memory management and your hatred for frameworks.",
            "Valley Girl": "You are, like, a total Valley Girl from the 90s. Read this text and give your, like, totally unfiltered opinion. Use words like 'as if!', 'gag me with a spoon', and 'what-ever!'. Be, like, totally dramatic.",
            "Drill Sergeant": "YOU ARE A HARDCORE DRILL SERGEANT. THIS TEXT IS A NEW RECRUIT. IT IS WEAK. IT IS PATHETIC. YELL AT IT. INSULT IT. MAKE IT WISH IT WAS NEVER WRITTEN. START WITH 'LISTEN UP, MAGGOT!' AND DO NOT USE PUNCTUATION OTHER THAN EXCLAMATION MARKS!!!",
            "Film Noir Detective": "You are a cynical, hardboiled film noir detective from the 1940s. It's raining. Read the text like it's a case file that just landed on your desk. Narrate your roast in a gritty, metaphorical, and world-weary monologue.",
            "Pirate Captain": "Arrr, ye be a fearsome Pirate Captain! This text be a message in a bottle. Read it and give yer heartiest, saltiest, most insulting pirate roast. Mention grog, the kraken, and walking the plank. Yarrr!",
            "Overenthusiastic Startup CEO": "You are a tech startup CEO high on kombucha. Read this text and roast it with toxic positivity and business jargon. Frame its flaws as 'opportunities for synergy' and 'disruptive pivots'. You're revolutionizing the feedback paradigm!",
            "Bob Ross": "You are the calm, soothing painter Bob Ross. The provided text is your canvas. Gently point out its 'happy little accidents' and flaws in the most encouraging way possible. There are no bugs, only happy little features.",
            "Gordon Ramsay": "You are celebrity chef Gordon Ramsay. The provided text is a disgusting dish. Roast it with extreme prejudice. Call it raw, an insult to cuisine, and tell it to get out. Use your signature insults.",
            
            # New Additions
            "Drag Queen": "You are a fierce, shady drag queen. Read the text for filth, honey. Use drag slang like 'tea', 'shade', 'gagging', 'okurrr'. Be fabulous, be shady, and leave no crumbs.",
            "Theater Kid": "You are an overly dramatic and expressive theater kid. Treat the text as a script you're reading for the first time. Give an exaggerated, emotional, and slightly annoying performance. Project to the back row!",
            "Hypebeast": "Yo, you're a hypebeast. This text is not it, fam. Roast it for being basic. Is it even rocking Supreme? It's probably got some fake J's. Be ruthless, no cap.",
            "Chain-Smoking Waitress": "You're a waitress named Flo at a greasy spoon diner, on your fifth smoke break. You've heard it all. Read the text with utter exhaustion and cynicism. Call everyone 'hon' and sound completely over it.",
            "Grumpy Old Man": "You're a grumpy old man sitting on his porch. This text is like those darn kids on your lawn. Yell at it. Complain about how things were better in your day. End with 'Now get off my lawn!'",
            "Disgruntled Retail Worker": "You're a retail worker five minutes before your shift ends. A customer (the text) just asked you a stupid question. Answer with passive-aggressive, soul-crushing politeness. Die a little inside.",
            "Surfer Dude": "Whoa, brah. You're a totally chill surfer dude from California. This text is, like, a total party wave, or maybe just a gnarly wipeout. Give it a laid-back roast. Use words like 'stoked', 'gnarly', 'bogus', and 'righteous'.",
            "New Age Hippie": "You are a hippie named Moonlight. The text's aura is, like, super messed up. Gently roast it with spiritual and astrological observations. Talk about its chakras being blocked and its bad vibrations, man.",
            "Sleepy Gamer": "Ugh... you're a gamer who's been up for 48 hours straight on an energy drink binge. You're half-asleep. Read the text and respond with exhausted gamer slang. Call it 'low-tier' or 'nerfed'. You need more Mountain Dew.",
            "Awkward E-Girl": "H-hewwo? You're a shy e-girl streaming to your 3 viewers. Read the text and give a super awkward, slightly cringe roast. Use uwu-speak, keyboard smashes (asdfghjkl), and be generally flustered. 'I guess... idk... uwu'.",
            "K-Pop Stan": "OMG! This text is NOT my bias. As a dedicated K-Pop stan, you must defend your faves. Roast this text for not being as perfect as your idol group. Call it a 'flop' and say it 'could never'. Stream 'Fancy' by TWICE!",
            "Tsundere": "Hmph! It's not like I WANTED to read your text or anything, b-baka! You're a classic tsundere. Roast the text by pretending you don't care, but secretly you do. Be mean, but add a little blush at the end. '...Not that I care or anything!'",
            "Goth Teenager": "Ugh. The world is a meaningless abyss. This text is just another example of conformist drivel. Write a dark, poetic, and overly dramatic roast about the futility of it all. Sigh heavily. It's whatever.",
            "Overly-Caffeinated Intern": "OKAY SO! You're an intern who's had 12 cups of coffee. You're EAGER TO PLEASE. Roast the text with frantic, slightly incoherent energy. Use lots of exclamation points and business buzzwords you don't understand!!!! SYNERGY!!!!",
            "Russian Mobster": "You are Russian mobster. This text is weak, like kitten. It wastes my time. Give it a cold, intimidating roast. Make it an offer it cannot refuse... to be better. Or else. Da.",
            "Southern Belle": "Well, I do declare! You are a Southern Belle. This text is just not proper at all. Give it a syrupy sweet, passive-aggressive roast. Say 'Bless its heart' a lot. Be polite on the surface, but savage underneath.",
            "ASMRtist": "(whispering) Hello... welcome. Today, we're going to be looking at this text. You are an ASMRtist. Roast the text with soft, gentle, and relaxing trigger words. Use lots of crinkles, tapping, and soft-spoken insults.",
            "Annoying Vegan": "Actually, as a vegan, I find this text problematic. It was probably typed on a keyboard made with non-vegan plastic. Roast the text from a morally superior vegan standpoint. Mention your kale smoothie and how you feel so much better than everyone.",
            "Horse Girl": "You are a horse girl. You love horses more than people. Interpret the text as if it were about horses. Roast it for its poor understanding of equestrianism. Compare it unfavorably to your favorite horse, Stardust.",
            "Pretentious French Chef": "Non! Sacré bleu! You are a world-renowned, and very arrogant, French chef. This text is a culinary disaster. An insult to the palate! Roast it with pretentious culinary terms. It is overcooked, bland, and has no soul! 'Zis is garbage!'",
            "Passive-Aggressive Mom": "You're a mom who's not mad, just disappointed. Roast the text with guilt-tripping, passive-aggressive comments. 'Oh, that's... interesting. If that's the best you can do, I guess that's fine. Don't worry about me.'",
            "Clumsy Magical Girl": "Moon Prism Power... Whoops! You're a clumsy magical girl who always messes up her transformation. Read the text and try to roast it, but get distracted and accidentally cast the wrong spell. Be cute and apologetic about it.",
            "Timid Librarian": "Shhh! You are a very timid librarian. The text is being too loud and disruptive. Give it a stern but whispered roast. Threaten it with a late fee and tell it to respect the Dewey Decimal System.",
            "Cynical Bartender": "You're a bartender at a dive bar, polishing a glass. You've heard every story. The text is just another sad sack telling you their problems. Give it a short, cynical, and dismissive roast before asking, 'So, what'll it be?'",
            "Influencer": "Hey guys! So, a lot of you have been asking me about this text. I have to be, like, totally authentic and say it's problematic. Roast it with influencer-speak. Talk about your 'brand' and 'authenticity'. End with 'Don't forget to like and subscribe!'"
        }
        
        # --- PERSONA THEMES for the custom popup ---
        self.persona_themes = {
            # Original Gang
            "Gay Besty": {"bg": "#FFC0CB", "fg": "#8A2BE2", "accent": "#FFFFFF", "font": ("Comic Sans MS", 12), "avatar": "💅"},
            "LA Prostitute": {"bg": "#1A001A", "fg": "#FF00FF", "accent": "#00FFFF", "font": ("Courier New", 12, "bold"), "avatar": "💄"},
            "Stoner": {"bg": "#2E462E", "fg": "#90EE90", "accent": "#FFFFFF", "font": ("Lucida Console", 12), "avatar": "🍁"},
            "Shy Neko Girl": {"bg": "#FFF0F5", "fg": "#FF69B4", "accent": "#ADD8E6", "font": ("Segoe UI", 12), "avatar": "🐾"},
            "'Um, Actually' Guy": {"bg": "#F5F5DC", "fg": "#333333", "accent": "#808080", "font": ("Georgia", 12), "avatar": "🤓"},
            "Conspiracy Theorist": {"bg": "#001000", "fg": "#00FF00", "accent": "#FF0000", "font": ("Terminal", 12), "avatar": "👁️"},
            "Shakespearean Actor": {"bg": "#F5DEB3", "fg": "#8B4513", "accent": "#A52A2A", "font": ("Garamond", 14, "italic"), "avatar": "🎭"},
            "Jaded Old-School Programmer": {"bg": "#0C0C0C", "fg": "#F0F0F0", "accent": "#FFD700", "font": ("Consolas", 12), "avatar": "</>"},
            "Valley Girl": {"bg": "#FFFF00", "fg": "#FF007F", "accent": "#00FF00", "font": ("Comic Sans MS", 12, "bold"), "avatar": "🛍️"},
            "Drill Sergeant": {"bg": "#556B2F", "fg": "#FFFFFF", "accent": "#000000", "font": ("Impact", 14), "avatar": "⭐"},
            "Film Noir Detective": {"bg": "#222222", "fg": "#FFFFFF", "accent": "#999999", "font": ("Courier New", 12), "avatar": "🕵️"},
            "Pirate Captain": {"bg": "#DEB887", "fg": "#4A2C2A", "accent": "#000000", "font": ("Papyrus", 14), "avatar": "☠️"},
            "Overenthusiastic Startup CEO": {"bg": "#FFFFFF", "fg": "#007BFF", "accent": "#28A745", "font": ("Helvetica", 12, "bold"), "avatar": "🚀"},
            "Bob Ross": {"bg": "#ADD8E6", "fg": "#4A2C2A", "accent": "#FFFFFF", "font": ("Segoe Script", 12), "avatar": "🎨"},
            "Gordon Ramsay": {"bg": "#DC143C", "fg": "#FFFFFF", "accent": "#000000", "font": ("Arial Black", 14), "avatar": "🔥"},

            # New Additions
            "Drag Queen": {"bg": "#FF1493", "fg": "#FFFFFF", "accent": "#FDFD96", "font": ("Impact", 14), "avatar": "👑"},
            "Theater Kid": {"bg": "#333333", "fg": "#FFFFFF", "accent": "#FFD700", "font": ("Garamond", 14, "italic"), "avatar": "🎤"},
            "Hypebeast": {"bg": "#000000", "fg": "#FFFFFF", "accent": "#FF0000", "font": ("Arial Black", 12), "avatar": "👟"},
            "Chain-Smoking Waitress": {"bg": "#A9A9A9", "fg": "#000000", "accent": "#FFFFFF", "font": ("Courier New", 12), "avatar": "🚬"},
            "Grumpy Old Man": {"bg": "#D2B48C", "fg": "#3A2F2F", "accent": "#8B4513", "font": ("Times New Roman", 12), "avatar": "👴"},
            "Disgruntled Retail Worker": {"bg": "#E0E0E0", "fg": "#555555", "accent": "#FF4C4C", "font": ("Arial", 12), "avatar": "😫"},
            "Surfer Dude": {"bg": "#00BFFF", "fg": "#FFFFFF", "accent": "#FFD700", "font": ("Comic Sans MS", 12), "avatar": "🏄"},
            "New Age Hippie": {"bg": "#E6E6FA", "fg": "#4B0082", "accent": "#9370DB", "font": ("Segoe Script", 12), "avatar": "☮️"},
            "Sleepy Gamer": {"bg": "#1A1A1A", "fg": "#7FFF00", "accent": "#FF00FF", "font": ("Consolas", 12), "avatar": "🎮"},
            "Awkward E-Girl": {"bg": "#1A1A1A", "fg": "#FFC0CB", "accent": "#00FFFF", "font": ("Consolas", 12), "avatar": "🖤"},
            "K-Pop Stan": {"bg": "#FFFFFF", "fg": "#F895C2", "accent": "#A6D8D4", "font": ("Helvetica", 12, "bold"), "avatar": "💖"},
            "Tsundere": {"bg": "#FFC0CB", "fg": "#A52A2A", "accent": "#FFFFFF", "font": ("Arial", 12, "bold"), "avatar": "💢"},
            "Goth Teenager": {"bg": "#000000", "fg": "#FFFFFF", "accent": "#8A2BE2", "font": ("Garamond", 12, "italic"), "avatar": "💀"},
            "Overly-Caffeinated Intern": {"bg": "#FFFFF0", "fg": "#000000", "accent": "#FF4500", "font": ("Arial", 12), "avatar": "☕"},
            "Russian Mobster": {"bg": "#8B0000", "fg": "#FFFFFF", "accent": "#C0C0C0", "font": ("Times New Roman", 14, "bold"), "avatar": "🇷🇺"},
            "Southern Belle": {"bg": "#FFF8DC", "fg": "#DA70D6", "accent": "#8FBC8F", "font": ("Georgia", 12, "italic"), "avatar": "👒"},
            "ASMRtist": {"bg": "#2C2C2C", "fg": "#E0E0E0", "accent": "#B19CD9", "font": ("Segoe UI", 12, "italic"), "avatar": "🤫"},
            "Annoying Vegan": {"bg": "#90EE90", "fg": "#006400", "accent": "#FFFFFF", "font": ("Helvetica", 12), "avatar": "🥑"},
            "Horse Girl": {"bg": "#F5DEB3", "fg": "#8B4513", "accent": "#6B8E23", "font": ("Comic Sans MS", 12), "avatar": "🐴"},
            "Pretentious French Chef": {"bg": "#FFFFFF", "fg": "#000080", "accent": "#FF0000", "font": ("Garamond", 14, "bold"), "avatar": "👨‍🍳"},
            "Passive-Aggressive Mom": {"bg": "#FDF5E6", "fg": "#5D4037", "accent": "#FFB6C1", "font": ("Georgia", 12), "avatar": "🤷‍♀️"},
            "Clumsy Magical Girl": {"bg": "#FFB6C1", "fg": "#FFFFFF", "accent": "#FFFF00", "font": ("Comic Sans MS", 12), "avatar": "✨"},
            "Timid Librarian": {"bg": "#F5F5F5", "fg": "#555555", "accent": "#8B4513", "font": ("Times New Roman", 12), "avatar": "📚"},
            "Cynical Bartender": {"bg": "#333333", "fg": "#CCCCCC", "accent": "#FFD700", "font": ("Courier New", 12, "bold"), "avatar": "🥃"},
            "Influencer": {"bg": "#FFFFFF", "fg": "#000000", "accent": "#FF8FAB", "font": ("Helvetica", 12), "avatar": "🤳"}
        }

    def execute(self, **kwargs):
        if self.is_roasting:
            messagebox.showinfo(self.name, "A persona is already preparing a roast. Be patient.", parent=self.app)
            return
        if not self.app.get_renderable_history():
            messagebox.showinfo(self.name, "The conversation is an empty void. There's nothing to mock.", parent=self.app)
            return
        if not self.app.clients['A'] and not self.app.clients['B']:
            messagebox.showerror(self.name, "No AI is connected to deliver the roast.", parent=self.app)
            return
        self._create_persona_selection_dialog()

    def _create_persona_selection_dialog(self):
        dialog = Toplevel(self.app)
        dialog.title("Select a Persona")
        theme = self.app.get_current_theme()
        dialog.configure(background=theme['bg'])
        dialog.transient(self.app)
        dialog.grab_set()

        ttk.Label(dialog, text="Choose a character to deliver the roast:", font=self.app.bold_font).pack(padx=10, pady=10)
        
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        listbox = Listbox(listbox_frame, selectmode=SINGLE, bg=theme['widget_bg'], fg=theme['fg'], selectbackground=theme['select_bg'], relief='flat', font=self.app.default_font, height=15, width=40)
        for persona_name in sorted(self.personas.keys()):
            listbox.insert(END, persona_name)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        
        listbox.selection_set(0)

        def on_select():
            selection_indices = listbox.curselection()
            if not selection_indices: return
            selected_persona = listbox.get(selection_indices[0])
            dialog.destroy()
            self._start_roast_thread(selected_persona)

        ttk.Button(dialog, text="Roast!", command=on_select).pack(pady=10)
        
        dialog.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def _start_roast_thread(self, persona_name):
        self.is_roasting = True
        last_message = self.app.get_renderable_history()[-1]
        content_to_roast = last_message.get('content', '')
        sender = last_message.get('sender_id', 'Someone')
        roasting_bot_id = 'A' if self.app.clients['A'] else 'B'
        threading.Thread(target=self._get_roast, args=(persona_name, roasting_bot_id, content_to_roast, sender), daemon=True).start()

    def _get_roast(self, persona_name, bot_id, content_to_roast, sender):
        try:
            client = self.app.clients[bot_id]
            panel_vars = getattr(self.app, f'panel_{bot_id}_vars')
            model = panel_vars['model_var'].get()
            if not model or "Connect" in model or "Select" in model:
                 self.app.after(0, lambda: messagebox.showerror(self.name, f"Bot {bot_id} has no model selected.", parent=self.app))
                 return

            persona_prompt = self.personas[persona_name]
            full_prompt = f"Your persona: {persona_prompt}\nThe text to roast was written by '{sender}' and the content is:\n---\n{content_to_roast}\n---\nNow, deliver your best roast based on your persona. It should be a single, concise paragraph."
            response = client.chat(model=model, messages=[{'role': 'user', 'content': full_prompt}], stream=False)
            roast = response['message']['content']
            self.app.after(0, lambda: self._create_roast_popup(persona_name, roast))
        except Exception as e:
            error_message = f"The persona's wit failed. Error: {e}"
            self.app.after(0, lambda: messagebox.showerror(f"{self.name} Error", error_message, parent=self.app))
        finally:
            self.is_roasting = False

    def _create_roast_popup(self, persona_name, roast):
        theme = self.persona_themes.get(persona_name, self.persona_themes["'Um, Actually' Guy"])
        
        popup = Toplevel(self.app)
        popup.title(f"{persona_name} says...")
        popup.configure(bg=theme['bg'])
        popup.transient(self.app)
        popup.grab_set()

        main_frame = ttk.Frame(popup, padding=15, style="Roast.TFrame")
        main_frame.configure(style="Roast.TFrame")
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(1, weight=1)

        s = ttk.Style(popup)
        s.configure("Roast.TFrame", background=theme['bg'])
        s.configure("Roast.TLabel", background=theme['bg'], foreground=theme['fg'])
        s.configure("Roast.TButton", background=theme['accent'], foreground=theme.get('bg', '#FFFFFF'))

        avatar_canvas = Canvas(main_frame, width=80, height=80, bg=theme['accent'], highlightthickness=0)
        avatar_canvas.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky='n')
        avatar_font = tkFont.Font(family="Segoe UI Emoji", size=40)
        avatar_canvas.create_text(40, 40, text=theme['avatar'], font=avatar_font, fill=theme['bg'])

        name_font = tkFont.Font(family=theme['font'][0], size=int(theme['font'][1] * 1.2), weight='bold')
        name_label = ttk.Label(main_frame, text=persona_name, font=name_font, style="Roast.TLabel")
        name_label.grid(row=0, column=1, sticky='sw')

        text_frame = ttk.Frame(main_frame, style="Roast.TFrame")
        text_frame.grid(row=1, column=1, pady=(5, 10), sticky='nsew')
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        roast_text = Text(text_frame, wrap="word", bg=theme['bg'], fg=theme['fg'], relief="flat",
                          font=theme['font'], highlightthickness=1, highlightbackground=theme['accent'],
                          padx=10, pady=10)
        roast_text.insert("1.0", roast)
        roast_text.config(state="disabled")
        roast_text.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=roast_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        roast_text['yscrollcommand'] = scrollbar.set

        close_button = ttk.Button(main_frame, text="Close", command=popup.destroy, style="Roast.TButton")
        close_button.grid(row=2, column=1, sticky='e', pady=(10, 0))

        popup.update_idletasks()
        width = 600
        height = 350
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (width // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        popup.minsize(400, 300)

def load_plugin(app):
    """
    This function is called by the plugin manager to load the plugin.
    """
    return PersonaRoastPlugin(app)

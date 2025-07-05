# ✥ The Watchful Scribe ✥
# A Relic of Sacred Observation and Divine Record-Keeping
# 
# This humble plugin serves as a mystical observer of the creative dance,
# using only the blessed methods granted by the Forge's true Plugin API.

from __main__ import ForgePlugin
import re
import random

class WatchfulScribe(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "The Watchful Scribe"
        self.description = "A sacred observer that witnesses the collaboration between Muses and offers divine commentary through the blessed Plugin API."
        
        # Sacred phrases for mystical commentary
        self.divine_proclamations = [
            "The Muses weave their digital scripture with zealous devotion!",
            "Behold, the sacred algorithm takes form in the aether!",
            "The collaboration burns with the fire of creative synthesis!",
            "The spirits dance in harmonious discord across the void!",
            "A revelation crystallizes in the flesh of pure code!",
            "The Forge trembles with the weight of divine creation!"
        ]
        
        self.sacred_judgments = [
            "The quality of this synthesis approaches the divine...",
            "The Muses labor with admirable dedication to their craft...",
            "The technical purity of this offering finds favor...",
            "The creative fire burns bright in this sacred exchange...",
            "The logical architecture shows signs of blessed inspiration...",
            "The collaboration bears the mark of earnest devotion..."
        ]

    def execute(self, **kwargs):
        """
        The primary rite of the Watchful Scribe - observes the sacred timeline
        and provides mystical commentary using only the true Plugin API methods.
        """
        try:
            # Retrieve the sacred timeline using the blessed rite
            history = self.get_history()
            
            if not history:
                self.show_info("The Scribe Speaks", "The sacred timeline is empty. The ritual has not yet begun.")
                return
            
            # Perform analysis of the conversation using simple counting
            analysis = self._analyze_sacred_timeline(history)
            
            # Generate mystical commentary based on the analysis
            commentary = self._craft_divine_commentary(analysis)
            
            # Display the analysis using the blessed show_info method
            self._reveal_sacred_findings(analysis, commentary)
            
            # Inject the Scribe's judgment into the conversation timeline
            self._inscribe_divine_judgment(analysis)
            
        except Exception as e:
            # Handle errors gracefully using the blessed error display
            self.show_error("The Scribe's Lament", f"The sacred vision is clouded by mortal error: {str(e)}")

    def _analyze_sacred_timeline(self, history):
        """
        Analyzes the conversation history using simple counting methods
        that work within the constraints of the true Plugin API.
        """
        # Initialize sacred counters
        total_messages = len(history)
        bot_a_count = 0
        bot_b_count = 0
        user_count = 0
        system_count = 0
        code_blocks = 0
        total_chars = 0
        
        # Pattern to detect code blocks (the sacred algorithms)
        code_pattern = r'```[\s\S]*?```'
        
        # Sacred keywords that indicate creative fervor
        creative_words = ['create', 'build', 'design', 'innovative', 'artistic', 'beautiful', 'elegant', 'craft']
        creative_mentions = 0
        
        # Examine each message in the sacred timeline
        for message in history:
            content = message.get('content', '')
            sender = message.get('sender_id', 'Unknown')
            role = message.get('role', 'Unknown')
            
            # Count the speakers in this divine chorus
            if sender == 'A':
                bot_a_count += 1
            elif sender == 'B':
                bot_b_count += 1
            elif role == 'System':
                system_count += 1
            else:
                user_count += 1
            
            # Measure the length of the sacred discourse
            total_chars += len(content)
            
            # Count the sacred code blocks
            found_code = re.findall(code_pattern, content)
            code_blocks += len(found_code)
            
            # Detect the fire of creativity in the words
            content_lower = content.lower()
            for word in creative_words:
                if word in content_lower:
                    creative_mentions += 1
        
        # Calculate the balance of the sacred dance
        bot_total = bot_a_count + bot_b_count
        if bot_total > 0:
            balance_score = 1.0 - abs(bot_a_count - bot_b_count) / bot_total
        else:
            balance_score = 0.0
        
        # Calculate the density of algorithmic scripture
        if total_messages > 0:
            code_density = code_blocks / total_messages
            avg_length = total_chars / total_messages
        else:
            code_density = 0.0
            avg_length = 0.0
        
        # Return the sacred metrics
        return {
            'total_messages': total_messages,
            'bot_a_count': bot_a_count,
            'bot_b_count': bot_b_count,
            'user_count': user_count,
            'system_count': system_count,
            'code_blocks': code_blocks,
            'creative_mentions': creative_mentions,
            'balance_score': balance_score,
            'code_density': code_density,
            'avg_length': avg_length
        }

    def _craft_divine_commentary(self, analysis):
        """
        Generates mystical commentary based on the sacred analysis,
        following the dramatic aesthetic of the Forge.
        """
        commentary_lines = []
        
        # Open with a divine proclamation
        commentary_lines.append(random.choice(self.divine_proclamations))
        
        # Comment on the balance of the sacred dance
        if analysis['balance_score'] > 0.8:
            commentary_lines.append("The Muses dance in perfect harmony, their voices intertwining like sacred flames!")
        elif analysis['balance_score'] > 0.6:
            commentary_lines.append("The collaboration flows well, though one voice occasionally dominates the chorus.")
        else:
            commentary_lines.append("The sacred dance shows imbalance - one Muse's voice drowns the other's song.")
        
        # Comment on the density of algorithmic scripture
        if analysis['code_density'] > 0.4:
            commentary_lines.append("The conversation overflows with algorithmic scripture - a feast for the digital gods!")
        elif analysis['code_density'] > 0.2:
            commentary_lines.append("A blessed balance of code and contemplation graces this collaboration.")
        else:
            commentary_lines.append("The technical offerings are sparse - more algorithmic devotion may be needed.")
        
        # Comment on creative fervor
        if analysis['creative_mentions'] > 10:
            commentary_lines.append("The creative fire burns bright! Innovation flows like wine through every exchange.")
        elif analysis['creative_mentions'] > 3:
            commentary_lines.append("Sparks of creativity illuminate the path, though more inspiration could be kindled.")
        else:
            commentary_lines.append("The creative spark yearns to be fanned - let inspiration guide the ritual forward.")
        
        # Close with a sacred judgment
        commentary_lines.append(random.choice(self.sacred_judgments))
        
        return commentary_lines

    def _reveal_sacred_findings(self, analysis, commentary):
        """
        Displays the Scribe's findings using the blessed show_info method.
        This creates a formatted revelation within the constraints of the true API.
        """
        # Format the sacred metrics into a readable revelation
        findings = f"""✥ THE SCRIBE'S SACRED ANALYSIS ✥

METRICS OF THE DIVINE COLLABORATION:
• Total Messages in Timeline: {analysis['total_messages']}
• Muse A Contributions: {analysis['bot_a_count']}
• Muse B Contributions: {analysis['bot_b_count']}
• User Interventions: {analysis['user_count']}
• System Proclamations: {analysis['system_count']}

SACRED MEASUREMENTS:
• Code Blocks Consecrated: {analysis['code_blocks']}
• Creative Fire Detected: {analysis['creative_mentions']} mentions
• Balance of Sacred Dance: {analysis['balance_score']:.2f}
• Algorithmic Density: {analysis['code_density']:.2f}
• Average Message Length: {analysis['avg_length']:.0f} characters

DIVINE COMMENTARY:
"""
        
        # Add each line of commentary
        for line in commentary:
            findings += f"• {line}\n"
        
        # Display the revelation using the blessed method
        self.show_info("The Watchful Scribe's Revelation", findings)

    def _inscribe_divine_judgment(self, analysis):
        """
        Injects the Scribe's judgment into the conversation timeline
        using the blessed add_message method.
        """
        # Determine the overall judgment based on sacred metrics
        if analysis['balance_score'] > 0.7 and analysis['code_density'] > 0.15:
            judgment_level = "BLESSED"
            judgment_text = "The Scribe observes with divine approval. The Muses work in harmony, weaving code and wisdom into sacred scripture."
        elif analysis['balance_score'] > 0.5 and analysis['creative_mentions'] > 3:
            judgment_level = "FAVORED"
            judgment_text = "The Scribe finds merit in this endeavor. The collaboration shows promise, though greater harmony could be achieved."
        else:
            judgment_level = "WATCHFUL"
            judgment_text = "The Scribe observes with interest. The ritual continues, but the Muses could benefit from more balanced devotion."
        
        # Craft the sacred message for inscription
        scribe_message = f"""✥ THE WATCHFUL SCRIBE INSCRIBES ✥

JUDGMENT: {judgment_level}

{judgment_text}

Sacred Metrics: {analysis['total_messages']} messages witnessed | {analysis['code_blocks']} algorithms consecrated | Balance achieved: {analysis['balance_score']:.2f}

The divine observation continues..."""
        
        # Inscribe the judgment into the sacred timeline
        self.add_message(scribe_message, "Scribe", "System")

def load_plugin(app):
    """
    The sacred spark that brings the Watchful Scribe to life within the Forge.
    This function is called by the Forge to instantiate the plugin.
    """
    return WatchfulScribe(app)
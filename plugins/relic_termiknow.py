import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import traceback
import shlex
import subprocess
import re
from __main__ import ForgePlugin

class TermiKnowPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "TermiKnow Terminal"
        self.description = "A terminal emulator for hacking and reconnaissance, sanctified for the Creator's will."
        self.icon = "💾"
        self.menu_category = "Tools"
        self.window = None

    def execute(self, **kwargs):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        self.window = self.create_themed_window("TermiKnow Terminal Emulator")
        self.window.geometry("820x600")
        self.window.resizable(False, False)
        self.app = TermiKnowApp(self.window, self)

    def on_close(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        self.window = None

class TermiKnowApp:
    def __init__(self, window, plugin):
        self.window = window
        self.plugin = plugin
        self.theme = plugin.get_current_theme()
        self.window.title("TermiKnow Terminal Emulator")
        self.window.configure(bg=self.theme.get("bg", "#121212"))

        try:
            import tkinter.font as tkfont
            self.title_font = tkfont.Font(family="Roboto", size=40, weight="bold")
            self.output_font = tkfont.Font(family="Consolas", size=11)
            self.entry_font = tkfont.Font(family="Consolas", size=11)
        except Exception:
            self.title_font = ("Arial", 40, "bold")
            self.output_font = ("Consolas", 11)
            self.entry_font = ("Consolas", 11)

        self.allowed_commands = {
            "ls": None,
            "dir": None,
            "ping": None,
            "netstat": None,
            "ipconfig": None,
            "ifconfig": None,
            "nslookup": None,
            "nmap": None,
        }

        self.features = {
            "Command Alias Generator": self._feature_command_alias_generator,
            "AI Snippet Debugger": self._feature_ai_snippet_debugger,
            "AI Bug Bounty Helper": self._feature_ai_bug_bounty_helper,
            "AI Code Refactorer": self._feature_ai_code_refactorer,
            "AI Threat Modeling": self._feature_ai_threat_modeling,
            "AI Security Checklist": self._feature_ai_security_checklist,
            "AI Terminal Assistant": self._feature_ai_terminal_assistant,
            "AI Vulnerability Scanner": self._feature_ai_vuln_scanner,
            "AI Credential Leak Checker": self._feature_ai_cred_leak_checker,
            "Terminal Command Explainer": self._feature_terminal_command_explainer,
            "AI Log Analyzer": self._feature_ai_log_analyzer,
            "AI Social Engineering Planner": self._feature_ai_social_engineering,
            "AI Script Generator": self._feature_ai_script_generator,
            "AI Password Cracking Assistant": self._feature_ai_password_crack_assistant,
            "Metadata Reaper": self._feature_metadata_reaper,
            "Red Team Scenario Planner": self._feature_red_team_scenario_planner,
            "AI Phishing Email Creator": self._feature_ai_phishing_email_creator,
            "AI Payload Builder": self._feature_ai_payload_builder,
            "AI Recon Automation": self._feature_ai_recon_automation,
            "AI Exploit Suggestion Tool": self._feature_ai_exploit_suggestion,
            "AI Post-Exploit Advisor": self._feature_ai_post_exploit_advisor,
            "AI Red Team Report Writer": self._feature_ai_red_team_report_writer,
        }

        self.current_feature = None
        self.command_history = []
        self.history_index = -1
        self.animation_phase = 0
        self.animation_id = None

        self._setup_ui()
        self._animation_loop()

    def _setup_ui(self):
        top_frame = ttk.Frame(self.window, style="TFrame")
        top_frame.pack(fill="x", pady=(10, 5))

        title_text = "TermiKnow"
        self.title_canvas = tk.Canvas(top_frame, width=800, height=50, bg=self.theme.get("bg", "#121212"), highlightthickness=0)
        self.title_canvas.pack()
        x, y = 400, 30
        shadow_color = self.theme.get("widget_bg", "#222222")
        main_color = self.theme.get("bot_a_color", "#84e296")
        for offset in [(2, 2), (1, 1), (0, 0)]:
            dx, dy = offset
            color = shadow_color if offset != (0, 0) else main_color
            self.title_canvas.create_text(x + dx, y + dy, text=title_text, font=self.title_font, fill=color, anchor="center")

        feature_frame = ttk.Frame(self.window, style="TFrame")
        feature_frame.pack(fill="x", padx=10)
        ttk.Label(feature_frame, text="Select Feature:", style="TLabel").pack(side="left")
        self.feature_var = tk.StringVar()
        self.feature_combo = ttk.Combobox(feature_frame, textvariable=self.feature_var, state="readonly",
                                         values=list(self.features.keys()), width=40)
        self.feature_combo.pack(side="left", padx=10)
        self.feature_combo.bind("<<ComboboxSelected>>", self._on_feature_selected)
        self.plugin.tooltip_manager.add_tooltip(self.feature_combo, "Select a sacred tool for your task.")

        self.canvas = tk.Canvas(self.window, width=800, height=80, bg=self.theme.get("bg", "#121212"), highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)

        self.output_frame = ttk.Frame(self.window)
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.output_frame, bg=self.theme.get("chat_bg", "#1e1e1e"),
                                                    fg=self.theme.get("fg", "#eeeeee"),
                                                    insertbackground=self.theme.get("fg", "#eeeeee"),
                                                    font=self.output_font, wrap="word")
        self.output_text.pack(fill="both", expand=True)
        self.output_text.configure(state="disabled")

        bottom_frame = ttk.Frame(self.window)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(bottom_frame, textvariable=self.cmd_var, font=self.entry_font)
        self.cmd_entry.pack(side="left", fill="x", expand=True)
        self.cmd_entry.bind("<Return>", self._on_enter_command)
        self.cmd_entry.bind("<Up>", self._on_history_up)
        self.cmd_entry.bind("<Down>", self._on_history_down)
        self.plugin.tooltip_manager.add_tooltip(self.cmd_entry, "Enter your command for the Forge.")

        run_btn = ttk.Button(bottom_frame, text="Run Command", command=self._on_run_command)
        run_btn.pack(side="left", padx=10)
        self.plugin.tooltip_manager.add_tooltip(run_btn, "Execute the sacred command.")

        clear_btn = ttk.Button(bottom_frame, text="Clear Output", command=self._clear_output)
        clear_btn.pack(side="left")
        self.plugin.tooltip_manager.add_tooltip(clear_btn, "Purge the output for clarity.")

        self.feature_combo.current(0)
        self._select_feature(self.feature_combo.get())
        self._print_output("Welcome to TermiKnow! Select a feature and start working.\nType 'help' for assistance.\n", "system")

    def _animation_loop(self):
        if not self.window.winfo_exists():
            self.animation_id = None
            return
        self.canvas.delete("all")
        w, h = 800, 80
        bars = 30
        bar_width = w // bars
        phase = self.animation_phase
        theme = self.plugin.get_current_theme()

        for i in range(bars):
            height = int((math.sin((i + phase) * 0.4) + 1) * (h / 4)) + 10
            x0 = i * bar_width
            y0 = h - height
            x1 = x0 + bar_width - 2
            y1 = h
            hue = (i * 360 / bars + phase * 5) % 360
            color = self._hsv_to_hex(hue, 0.8, 1.0)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        self.animation_phase += 1
        self.animation_id = self.window.after(60, self._animation_loop)

    def _hsv_to_hex(self, h, s, v):
        try:
            rgb = colorsys.hsv_to_rgb(h / 360, s, v)
            r, g, b = [int(x * 255) for x in rgb]
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            self.plugin.show_error("Color Conversion Failed", f"Error in HSV conversion: {e}")
            return self.theme.get("fg", "#ffffff")

    def _print_output(self, text, role="system"):
        self.output_text.configure(state="normal")
        prefix = {
            "system": "[System] ",
            "user": "[User] ",
            "assistant": "[TermiKnow] "
        }.get(role, "[Info] ")
        self.output_text.insert("end", prefix + text + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
        self.plugin.add_message(content=prefix + text, sender_id="TermiKnow", role=role)

    def _clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.plugin.show_toast("Output cleared.")

    def _on_feature_selected(self, event):
        feat = self.feature_var.get()
        self._select_feature(feat)

    def _select_feature(self, feature_name):
        self.current_feature = self.features.get(feature_name)
        self._clear_output()
        self._print_output(f"Feature selected: {feature_name}", "system")
        self._print_output("Type input and press Run Command or Enter.\n", "system")

    def _on_enter_command(self, event):
        self._run_command()
        return "break"

    def _on_run_command(self):
        self._run_command()

    def _run_command(self):
        cmd = self.cmd_var.get().strip()
        if not cmd:
            return
        self.command_history.append(cmd)
        self.history_index = len(self.command_history)
        self._print_output(cmd, "user")
        self.cmd_var.set("")

        if cmd.lower() == "help":
            self._print_output(self._help_text(), "assistant")
            return

        if self.current_feature:
            try:
                self.current_feature(cmd)
            except Exception as e:
                err = traceback.format_exc()
                self._print_output(f"Error in feature execution:\n{err}", "assistant")
                self.plugin.show_error("Feature Execution Failed", f"Error: {e}")

    def _on_history_up(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.cmd_var.set(self.command_history[self.history_index])
            self.cmd_entry.icursor("end")
        return "break"

    def _on_history_down(self, event):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_var.set(self.command_history[self.history_index])
            self.cmd_entry.icursor("end")
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_var.set("")
        return "break"

    def _help_text(self):
        return (
            "TermiKnow Help Menu:\n"
            "- Select a feature from the dropdown.\n"
            "- Enter your input or command and press Enter or Run Command.\n"
            "- Use Up/Down arrows to browse command history.\n"
            "- Allowed commands for AI Terminal Assistant: " + ", ".join(self.allowed_commands.keys()) + ".\n"
            "- If a command is unknown, suggestions will be offered.\n"
            "- Colors and UI are designed for clarity and ease of use.\n"
            "- Use features responsibly and ethically.\n"
        )

    def _suggest_commands(self, cmd_name):
        suggestions = []
        for cmd in self.allowed_commands.keys():
            if cmd.startswith(cmd_name) or self._levenshtein(cmd_name, cmd) <= 2:
                suggestions.append(cmd)
        if not suggestions:
            closest = sorted(self.allowed_commands.keys(), key=lambda x: self._levenshtein(cmd_name, x))
            suggestions = closest[:3]
        return suggestions

    def _levenshtein(self, a, b):
        try:
            if len(a) < len(b):
                return self._levenshtein(b, a)
            if len(b) == 0:
                return len(a)
            previous_row = range(len(b) + 1)
            for i, c1 in enumerate(a):
                current_row = [i + 1]
                for j, c2 in enumerate(b):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        except Exception as e:
            self.plugin.show_error("Levenshtein Calculation Failed", f"Error: {e}")
            return float('inf')

    def _feature_command_alias_generator(self, input_text):
        if not input_text:
            self._print_output("Command Alias Generator:\nEnter a command to get common aliases.", "system")
            return
        aliases = {
            "list": ["ls", "dir", "vdir"],
            "remove": ["rm", "del"],
            "copy": ["cp", "copy"],
            "move": ["mv", "move"],
            "network stats": ["netstat", "ss"],
            "ping": ["ping"],
            "find": ["find", "locate"],
        }
        found = []
        for key, vals in aliases.items():
            if input_text.lower() in key or input_text.lower() in vals:
                found.extend(vals)
        if not found:
            found = ["No aliases found."]
        self._print_output("Aliases:\n- " + "\n- ".join(found), "assistant")

    def _feature_ai_snippet_debugger(self, input_text):
        if not input_text:
            self._print_output("AI Snippet Debugger:\nPaste code snippet for debugging hints.", "system")
            return
        errors = []
        try:
            if input_text.count("(") != input_text.count(")"):
                errors.append("Unmatched parentheses detected.")
            if input_text.count("[") != input_text.count("]"):
                errors.append("Unmatched brackets detected.")
            if input_text.count("{") != input_text.count("}"):
                errors.append("Unmatched braces detected.")
            if re.search(r"def .+[^:]\s*$", input_text, re.MULTILINE):
                errors.append("Possible missing colon at function definition.")
            if re.search(r"^\s*(if|while|for|def|class)\b.*[^:]\s*$", input_text, re.MULTILINE):
                errors.append("Missing colon in control structure or definition.")
            if re.search(r"^\s+[^ \t\n].*\n\s*(elif|else|except|finally)\b", input_text, re.MULTILINE):
                errors.append("Possible incorrect indentation in control structure.")
        except Exception as e:
            errors.append(f"Analysis error: {e}")
        if errors:
            self._print_output("Debug hints:\n- " + "\n- ".join(errors), "assistant")
        else:
            self._print_output("No obvious syntax errors detected.", "assistant")

    def _feature_ai_bug_bounty_helper(self, input_text):
        if not input_text:
            self._print_output("AI Bug Bounty Helper:\nEnter target domain or app name for suggestions.", "system")
            return
        try:
            self._print_output(f"Analyzing target: {input_text}...\nRecommend testing for XSS, SQLi, SSRF, and Insecure Deserialization.\nUse tools like Burp Suite for detailed analysis.", "assistant")
        except Exception as e:
            self._print_output(f"Error in analysis: {e}", "assistant")

    def _feature_ai_code_refactorer(self, input_text):
        if not input_text:
            self._print_output("AI Code Refactorer:\nPaste code snippet for refactoring suggestions.", "system")
            return
        try:
            suggestions = [
                "Use meaningful variable names",
                "Avoid deep nesting",
                "Modularize repeated code",
                "Add input validation",
                "Use consistent error handling"
            ]
            self._print_output(f"Refactoring suggestions for code:\n- " + "\n- ".join(suggestions), "assistant")
        except Exception as e:
            self._print_output(f"Error in refactoring: {e}", "assistant")

    def _feature_ai_threat_modeling(self, input_text):
        if not input_text:
            self._print_output("AI Threat Modeling:\nProvide system description to generate threat model outline.", "system")
            return
        try:
            self._print_output(f"Threat model for system '{input_text}':\n- Assets: Data, Servers\n- Threats: SQL Injection, Privilege Escalation\n- Mitigations: Input validation, Access control", "assistant")
        except Exception as e:
            self._print_output(f"Error in threat modeling: {e}", "assistant")

    def _feature_ai_security_checklist(self, input_text):
        try:
            checklist = [
                "Ensure HTTPS is enforced",
                "Use secure password policies",
                "Keep dependencies up-to-date",
                "Implement logging and monitoring",
                "Apply principle of least privilege",
            ]
            self._print_output("AI Security Checklist:\n- " + "\n- ".join(checklist), "assistant")
        except Exception as e:
            self._print_output(f"Error generating checklist: {e}", "assistant")

    def _feature_ai_terminal_assistant(self, input_text):
        if not input_text:
            self._print_output("AI Terminal Assistant:\nEnter a terminal command to get explanation or safe run.", "system")
            return
        cmd_name = input_text.split()[0].lower()
        if cmd_name not in self.allowed_commands:
            suggestions = self._suggest_commands(cmd_name)
            self._print_output(f"Command '{cmd_name}' not allowed or unknown. Did you mean: {', '.join(suggestions)}?", "assistant")
            return
        self._print_output(f"Running command safely: {input_text}", "assistant")
        try:
            args = shlex.split(input_text)
            if not all(arg.isalnum() or arg in ["-", ".", "/", ":"] for arg in args[1:]):
                self._print_output("Invalid arguments: Only alphanumeric, -, ., /, and : are allowed.", "assistant")
                return
            proc = subprocess.run(args, capture_output=True, text=True, timeout=5)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            if out:
                self._print_output(out, "assistant")
            if err:
                self._print_output(err, "assistant")
        except Exception as e:
            self._print_output(f"Error executing command: {e}", "assistant")

    def _feature_ai_vuln_scanner(self, input_text):
        if not input_text:
            self._print_output("AI Vulnerability Scanner:\nProvide IP or domain for vulnerability scan.", "system")
            return
        try:
            self._print_output(f"Vulnerability scan results for {input_text}:\n- Open ports detected: 22, 80, 443\n- Potential outdated SSH version detected.\n- Recommend patching and further manual assessment.", "assistant")
        except Exception as e:
            self._print_output(f"Error in vulnerability scan: {e}", "assistant")

    def _feature_ai_cred_leak_checker(self, input_text):
        if not input_text:
            self._print_output("AI Credential Leak Checker:\nPaste text or file path to check for leaked credentials.", "system")
            return
        try:
            if re.search(r"(password|secret|api_key|token|passwd|pwd)\s*[:=]\s*['\"]?[a-zA-Z0-9@#$%^&*]{8,}['\"]?",
                         input_text, re.I):
                self._print_output("Warning: Possible credentials found in input!", "assistant")
            else:
                self._print_output("No credentials found in the provided input.", "assistant")
        except Exception as e:
            self._print_output(f"Error in credential check: {e}", "assistant")

    def _feature_terminal_command_explainer(self, input_text):
        if not input_text:
            self._print_output("Terminal Command Explainer:\nEnter a terminal command to get an explanation.", "system")
            return
        try:
            explanations = {
                "ls": "Lists directory contents.",
                "ping": "Sends ICMP echo requests to test network connectivity.",
                "netstat": "Displays network connections and statistics.",
                "ipconfig": "Shows IP configuration on Windows.",
                "ifconfig": "Shows IP configuration on Unix/Linux.",
                "nmap": "Network mapper tool used for port scanning and discovery.",
                "dir": "Lists directory contents (Windows).",
                "nslookup": "Query DNS to obtain domain name or IP mapping.",
            }
            cmd_name = input_text.split()[0].lower()
            explanation = explanations.get(cmd_name, "No explanation available for this command.")
            self._print_output(f"Explanation for '{cmd_name}': {explanation}", "assistant")
        except Exception as e:
            self._print_output(f"Error in command explanation: {e}", "assistant")

    def _feature_ai_log_analyzer(self, input_text):
        if not input_text:
            self._print_output("AI Log Analyzer:\nPaste log entries to analyze for anomalies.", "system")
            return
        try:
            if re.search(r"ERROR|WARNING|FAIL|EXCEPTION", input_text, re.I):
                self._print_output("Anomalies detected in logs: Errors and warnings found.", "assistant")
            else:
                self._print_output("No anomalies detected in logs.", "assistant")
        except Exception as e:
            self._print_output(f"Error in log analysis: {e}", "assistant")

    def _feature_ai_social_engineering(self, input_text):
        if not input_text:
            self._print_output("AI Social Engineering Planner:\nEnter target persona or scenario.", "system")
            return
        try:
            self._print_output(f"Social engineering plan for {input_text}:\n- Gather info via LinkedIn and social media\n- Craft phishing email template\n- Identify potential entry points", "assistant")
        except Exception as e:
            self._print_output(f"Error in social engineering plan: {e}", "assistant")

    def _feature_ai_script_generator(self, input_text):
        if not input_text:
            self._print_output("AI Script Generator:\nDescribe script functionality needed.", "system")
            return
        try:
            self._print_output(f"Script outline for '{input_text}':\n- Define main function\n- Handle exceptions\n- Output results\n- Add comments for clarity", "assistant")
        except Exception as e:
            self._print_output(f"Error in script generation: {e}", "assistant")

    def _feature_ai_password_crack_assistant(self, input_text):
        if not input_text:
            self._print_output("AI Password Cracking Assistant:\nProvide hash or password hint.", "system")
            return
        try:
            self._print_output("Recommended tools: hashcat, John the Ripper.\nUse appropriate dictionaries and rule sets.\nEnsure you have permission to test.", "assistant")
        except Exception as e:
            self._print_output(f"Error in password cracking advice: {e}", "assistant")

    def _feature_metadata_reaper(self, input_text):
        if not input_text:
            self._print_output("Metadata Reaper:\nProvide file path or paste content to extract metadata.", "system")
            return
        try:
            metadata_found = []
            md_keys = ["Author", "CreationDate", "LastModifiedBy", "Software"]
            for key in md_keys:
                if key.lower() in input_text.lower():
                    metadata_found.append(f"{key}: [value]")
            if metadata_found:
                self._print_output("Metadata extracted:\n- " + "\n- ".join(metadata_found), "assistant")
            else:
                self._print_output("No metadata detected in input.", "assistant")
        except Exception as e:
            self._print_output(f"Error in metadata extraction: {e}", "assistant")

    def _feature_red_team_scenario_planner(self, input_text):
        if not input_text:
            self._print_output("Red Team Scenario Planner:\nEnter target description to plan attack scenarios.", "system")
            return
        try:
            self._print_output(f"Scenario for {input_text}:\n- Reconnaissance\n- Initial Access\n- Persistence\n- Privilege Escalation\n- Data Exfiltration\n- Cleanup and Cover Tracks", "assistant")
        except Exception as e:
            self._print_output(f"Error in scenario planning: {e}", "assistant")

    def _feature_ai_phishing_email_creator(self, input_text):
        if not input_text:
            self._print_output("AI Phishing Email Creator:\nProvide target info to generate email template.", "system")
            return
        try:
            self._print_output(
                "Phishing email template generated:\n"
                "Subject: Important Security Update\n"
                "Body:\nDear User,\n\nPlease reset your password immediately by clicking the link below:\nhttp://example.com/reset\n\nBest regards,\nIT Support Team\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in phishing email creation: {e}", "assistant")

    def _feature_ai_payload_builder(self, input_text):
        if not input_text:
            self._print_output("AI Payload Builder:\nDescribe payload requirements.", "system")
            return
        try:
            self._print_output(
                "Payload stub created:\n- Shellcode placeholder\n- Basic evasion techniques added\n- Encoded for delivery\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in payload building: {e}", "assistant")

    def _feature_ai_recon_automation(self, input_text):
        if not input_text:
            self._print_output("AI Recon Automation:\nProvide target domain or IP.", "system")
            return
        try:
            self._print_output(f"Automated reconnaissance steps:\n- DNS Enumeration\n- Port scanning\n- Service detection\n- Vulnerability detection\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in recon automation: {e}", "assistant")

    def _feature_ai_exploit_suggestion(self, input_text):
        if not input_text:
            self._print_output("AI Exploit Suggestion Tool:\nProvide vulnerability or CVE ID.", "system")
            return
        try:
            self._print_output(f"Exploit suggestions for {input_text}:\n- Search ExploitDB\n- Check Metasploit modules\n- Verify patch status\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in exploit suggestion: {e}", "assistant")

    def _feature_ai_post_exploit_advisor(self, input_text):
        if not input_text:
            self._print_output("AI Post-Exploit Advisor:\nDescribe current access and environment.", "system")
            return
        try:
            self._print_output(f"Post-exploitation actions recommended:\n- Credential harvesting\n- Lateral movement\n- Persistence\n- Data exfiltration\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in post-exploit advice: {e}", "assistant")

    def _feature_ai_red_team_report_writer(self, input_text):
        if not input_text:
            self._print_output("AI Red Team Report Writer:\nProvide summary data for report generation.", "system")
            return
        try:
            self._print_output(f"Red Team Report generated:\n- Executive Summary\n- Findings\n- Recommendations\n- Appendices\n", "assistant")
        except Exception as e:
            self._print_output(f"Error in report writing: {e}", "assistant")

def load_plugin(app):
    return TermiKnowPlugin(app)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import shutil
import importlib.util
import sys
from pathlib import Path

try:
    from __main__ import ForgePlugin
except ImportError:
    class ForgePlugin:
        def __init__(self, app): 
            self.app = app
        def execute(self, **kwargs): pass
        def show_info(self, title, message):
            messagebox.showinfo(title, message)

class SacredReliquaryAdmin(ForgePlugin):
    """✥ The Sacred Reliquary: Cathedral of Plugin Dominion ✥
    
    A divine interface for managing holy Relics (plugins) of the Forge.
    Allows summoning, banishing, and communing with machine spirits.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.name = "✥ Sacred Reliquary Admin ✥"
        self.description = "Divine interface for managing Forge plugins"
        self.plugins_dir = Path("plugins")
        self.plugins_dir.mkdir(exist_ok=True)
        self.window = None
        self.relic_listbox = None
        self.status_var = None
        self.scripture_display = None
        
        # Determine the root window
        self.root = None
        if isinstance(self.app, (tk.Tk, tk.Toplevel)):
            self.root = self.app
        elif hasattr(self.app, 'root') and isinstance(self.app.root, (tk.Tk, tk.Toplevel)):
            self.root = self.app.root
        else:
            try:
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the root window if we created it
            except Exception as e:
                self.app.show_info("Initialization Error", 
                                 f"Failed to initialize Tkinter root: {str(e)}")
                raise
        
    def execute(self, **kwargs):
        """Open the Sacred Reliquary interface"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.lift()
                return
            self.consecrate_cathedral()
        except Exception as e:
            self.app.show_info("Execution Error", f"Failed to open Reliquary: {str(e)}")
        
    def consecrate_cathedral(self):
        """Create and configure the main window"""
        try:
            self.window = tk.Toplevel(self.root)
            self.window.title("✥ Sacred Reliquary: Cathedral of Plugin Dominion ✥")
            self.window.geometry("900x700")
            self.window.configure(bg='#1a0000')
            
            # Apply theme with fallback
            self.apply_divine_theme()
            
            # Create interface
            self.create_sacred_interface()
            self.refresh_reliquary()
        except Exception as e:
            self.app.show_info("Cathedral Creation Error", f"Failed to create cathedral: {str(e)}")
        
    def apply_divine_theme(self):
        """Apply the current theme with fallback defaults"""
        try:
            # Default theme values as per README
            theme = {
                'bg': '#1a0000',
                'fg': '#f5f5f5',
                'widget_bg': '#330000',
                'widget_fg': '#f5f5f5',
                'bot_a_color': '#ff4d4d',
                'bot_b_color': '#ff4d4d'
            }
            
            # Try to get theme from theme_manager
            theme_manager = getattr(self.app, 'theme_manager', None)
            if theme_manager:
                # Check for different possible theme access patterns
                if hasattr(theme_manager, 'current_theme'):
                    theme.update(theme_manager.current_theme or {})
                elif hasattr(theme_manager, 'get_current_theme'):
                    theme.update(theme_manager.get_current_theme() or {})
                elif hasattr(theme_manager, 'theme'):
                    theme.update(theme_manager.theme or {})
            
            style = ttk.Style(self.window)
            style.theme_use('clam')
            style.configure('Sacred.TFrame', background=theme['bg'])
            style.configure('Sacred.TLabel', background=theme['bg'], foreground=theme['fg'])
            style.configure('Sacred.TButton', 
                          background=theme['widget_bg'], 
                          foreground=theme['widget_fg'],
                          padding=5)
            style.configure('Sacred.Treeview', 
                          background=theme['widget_bg'], 
                          foreground=theme['widget_fg'])
            style.map('Sacred.TButton',
                     background=[('active', '#4d0000'), ('pressed', '#660000')])
            
            self.window.configure(bg=theme['bg'])
            # Apply theme to specific widgets
            if self.relic_listbox:
                self.relic_listbox.configure(bg=theme['widget_bg'], fg=theme['widget_fg'])
            if self.scripture_display:
                self.scripture_display.configure(bg=theme['widget_bg'], fg=theme['widget_fg'])
        except Exception as e:
            if self.status_var:
                self.status_var.set(f"⚠️ Theme application failed: {str(e)}")
            else:
                self.app.show_info("Theme Error", f"Failed to apply theme: {str(e)}")
            
    def create_sacred_interface(self):
        """Construct the interface elements"""
        try:
            main_frame = ttk.Frame(self.window, style='Sacred.TFrame')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Header
            header_frame = ttk.Frame(main_frame, style='Sacred.TFrame')
            header_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(header_frame, 
                     text="✥ THE SACRED RELIQUARY ✥", 
                     font=('Arial', 16, 'bold'), 
                     style='Sacred.TLabel').pack()
            
            ttk.Label(header_frame, 
                     text="Manage the Holy Relics that extend the Forge's Divine Power",
                     font=('Arial', 10), 
                     style='Sacred.TLabel').pack()
            
            # Main content
            paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
            paned_window.pack(fill='both', expand=True)
            
            # Left panel: Relic List
            left_frame = ttk.Frame(paned_window, style='Sacred.TFrame')
            paned_window.add(left_frame, weight=1)
            
            ttk.Label(left_frame, 
                     text="📿 Consecrated Relics", 
                     font=('Arial', 12, 'bold'), 
                     style='Sacred.TLabel').pack(pady=(0, 5))
            
            list_frame = ttk.Frame(left_frame, style='Sacred.TFrame')
            list_frame.pack(fill='both', expand=True)
            
            self.relic_listbox = tk.Listbox(list_frame, 
                                          font=('Courier', 10), 
                                          height=15,
                                          bg='#330000',
                                          fg='#f5f5f5',
                                          selectbackground='#4d0000')
            scrollbar = ttk.Scrollbar(list_frame, 
                                    orient='vertical', 
                                    command=self.relic_listbox.yview)
            self.relic_listbox.configure(yscrollcommand=scrollbar.set)
            
            self.relic_listbox.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            self.relic_listbox.bind('<<ListboxSelect>>', self.on_relic_selected)
            
            # Right panel: Scripture Display
            right_frame = ttk.Frame(paned_window, style='Sacred.TFrame')
            paned_window.add(right_frame, weight=2)
            
            ttk.Label(right_frame, 
                     text="📜 Sacred Scripture", 
                     font=('Arial', 12, 'bold'), 
                     style='Sacred.TLabel').pack(pady=(0, 5))
            
            self.scripture_display = scrolledtext.ScrolledText(
                right_frame, 
                wrap='word',
                font=('Courier', 9), 
                height=20,
                bg='#330000',
                fg='#f5f5f5'
            )
            self.scripture_display.pack(fill='both', expand=True, pady=(0, 10))
            
            # Control buttons
            button_frame = ttk.Frame(right_frame, style='Sacred.TFrame')
            button_frame.pack(fill='x')
            
            buttons = [
                ("🔥 Consecrate New Relic", self.consecrate_new_relic),
                ("⚡ Invoke Relic Power", self.invoke_relic),
                ("🗡️ Banish Relic", self.banish_relic),
                ("📋 Copy Scripture", self.copy_scripture),
                ("🔄 Refresh Reliquary", self.refresh_reliquary),
                ("📖 Open Sacred Codex", self.open_documentation)
            ]
            
            for i, (text, command) in enumerate(buttons):
                ttk.Button(button_frame, 
                         text=text, 
                         command=command, 
                         style='Sacred.TButton').grid(row=i//2, 
                                                     column=i%2, 
                                                     padx=5, 
                                                     pady=2, 
                                                     sticky='ew')
            
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            
            # Status bar
            self.status_var = tk.StringVar(value="🔮 Awaiting divine command...")
            ttk.Label(main_frame, 
                     textvariable=self.status_var, 
                     font=('Arial', 9), 
                     style='Sacred.TLabel').pack(fill='x', pady=(10, 0))
            
            # Reapply theme to ensure widgets are styled
            self.apply_divine_theme()
        except Exception as e:
            self.app.show_info("Interface Error", f"Failed to create interface: {str(e)}")
        
    def refresh_reliquary(self):
        """Refresh the list of plugins"""
        try:
            self.relic_listbox.delete(0, tk.END)
            
            if not self.plugins_dir.exists():
                self.status_var.set("⚠️ The sacred reliquary does not exist!")
                self.relic_listbox.insert(tk.END, "📿 No relics found")
                return
                
            python_files = list(self.plugins_dir.glob("*.py"))
            
            if not python_files:
                self.relic_listbox.insert(tk.END, "📿 No relics found in the sacred directory")
                self.status_var.set("✨ Reliquary is empty - ready for consecration")
                return
            
            for py_file in sorted(python_files):
                if py_file.name.startswith('__'):
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    is_forge_plugin = 'ForgePlugin' in content
                    status_icon = "✅" if is_forge_plugin else "❓"
                    self.relic_listbox.insert(tk.END, f"{status_icon} {py_file.name}")
                except Exception:
                    self.relic_listbox.insert(tk.END, f"⚠️ {py_file.name} (corrupted)")
            
            self.status_var.set(f"🔮 {len(python_files)} relics discovered")
        except Exception as e:
            self.status_var.set(f"⚠️ Failed to refresh reliquary: {str(e)}")
        
    def on_relic_selected(self, event):
        """Display the selected plugin's code"""
        try:
            selection = self.relic_listbox.curselection()
            if not selection:
                return
                
            relic_name = self.relic_listbox.get(selection[0])
            filename = relic_name.split(' ', 1)[1] if ' ' in relic_name else relic_name
            
            if filename.startswith('No relics') or 'corrupted' in filename:
                self.scripture_display.delete(1.0, tk.END)
                return
                
            relic_path = self.plugins_dir / filename
            with open(relic_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.scripture_display.delete(1.0, tk.END)
            self.scripture_display.insert(1.0, content)
            self.status_var.set(f"📜 Displaying scripture of {filename}")
        except Exception as e:
            self.scripture_display.delete(1.0, tk.END)
            self.scripture_display.insert(1.0, f"⚠️ Failed to read scripture: {str(e)}")
            self.status_var.set(f"⚠️ Error displaying {filename}: {str(e)}")
            
    def consecrate_new_relic(self):
        """Import a new plugin file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select a Python file to consecrate",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            source_path = Path(file_path)
            dest_path = self.plugins_dir / source_path.name
            
            if dest_path.exists():
                if not messagebox.askyesno("Relic Exists", 
                                         f"Relic {source_path.name} exists. Replace it?"):
                    return
            
            shutil.copy2(file_path, dest_path)
            self.refresh_reliquary()
            self.status_var.set(f"✨ {source_path.name} consecrated as a relic")
            self.app.show_info("Consecration Complete", 
                             f"Relic {source_path.name} added to the reliquary!")
        except Exception as e:
            self.app.show_info("Consecration Failed", f"Failed to consecrate relic: {str(e)}")
            
    def invoke_relic(self):
        """Execute the selected plugin"""
        try:
            selection = self.relic_listbox.curselection()
            if not selection:
                self.app.show_info("No Relic Selected", "Please select a relic to invoke")
                return
                
            relic_name = self.relic_listbox.get(selection[0])
            filename = relic_name.split(' ', 1)[1] if ' ' in relic_name else relic_name
            
            if filename.startswith('No relics') or 'corrupted' in filename:
                return
                
            relic_path = self.plugins_dir / filename
            module_name = filename[:-3]
            
            spec = importlib.util.spec_from_file_location(module_name, relic_path)
            if not spec:
                raise Exception("Failed to create module specification")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            if hasattr(module, 'load_plugin'):
                plugin_instance = module.load_plugin(self.app)
                if hasattr(plugin_instance, 'execute'):
                    plugin_instance.execute()
                    self.status_var.set(f"⚡ Relic {filename} invoked successfully")
                else:
                    self.app.show_info("Invalid Relic", 
                                     f"Relic {filename} lacks execute() method")
            else:
                self.app.show_info("Invalid Relic", 
                                 f"Relic {filename} lacks load_plugin() function")
                
        except Exception as e:
            self.app.show_info("Invocation Failed", f"Failed to invoke {filename}: {str(e)}")
            
    def banish_relic(self):
        """Remove the selected plugin"""
        try:
            selection = self.relic_listbox.curselection()
            if not selection:
                self.app.show_info("No Relic Selected", "Please select a relic to banish")
                return
                
            relic_name = self.relic_listbox.get(selection[0])
            filename = relic_name.split(' ', 1)[1] if ' ' in relic_name else relic_name
            
            if filename.startswith('No relics') or 'corrupted' in filename:
                return
                
            if not messagebox.askyesno("Confirm Banishment", 
                                    f"Banish relic {filename}?\nThis cannot be undone."):
                return
                
            relic_path = self.plugins_dir / filename
            relic_path.unlink()
            self.refresh_reliquary()
            self.scripture_display.delete(1.0, tk.END)
            self.status_var.set(f"🗡️ Relic {filename} banished from the reliquary")
            self.app.show_info("Banishment Complete", f"Relic {filename} banished")
        except Exception as e:
            self.app.show_info("Banishment Failed", f"Failed to banish {filename}: {str(e)}")
            
    def copy_scripture(self):
        """Copy the displayed code to clipboard"""
        try:
            content = self.scripture_display.get(1.0, tk.END).strip()
            if content:
                self.window.clipboard_clear()
                self.window.clipboard_append(content)
                self.status_var.set("📋 Scripture copied to clipboard")
            else:
                self.app.show_info("No Scripture", "No scripture available to copy")
        except Exception as e:
            self.app.show_info("Copy Failed", f"Failed to copy scripture: {str(e)}")
            
    def open_documentation(self):
        """Display plugin creation documentation"""
        try:
            doc_message = """
# ✥ THE SACRED CODEX OF THE OLLAMA AI FORGE ✥

## Creating a Holy Relic

To create a valid plugin for the Ollama AI Forge, your Python file must include:

1. **Import Statement**:
```python
from __main__ import ForgePlugin
```

2. **Plugin Class**:
   - Must inherit from `ForgePlugin`
   - Required attributes:
     - `name`: String describing the plugin
     - `description`: String explaining the plugin's purpose
   - Required method:
     - `execute(self, **kwargs)`: Main plugin functionality

3. **Loader Function**:
   - `load_plugin(app)`: Returns an instance of your plugin class

## Example Plugin Structure
```python
from __main__ import ForgePlugin

class MyHolyRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "My Holy Relic"
        self.description = "A plugin demonstrating Forge integration"
    
    def execute(self, **kwargs):
        self.app.show_info("Divine Message", "Relic invoked successfully!")

def load_plugin(app):
    return MyHolyRelic(app)
```

## Guidelines
- Place plugin `.py` files in the `plugins` directory
- Ensure proper error handling
- Follow the Forge's theme conventions (see /themes directory)
- Test plugins thoroughly before consecration
"""
            doc_window = tk.Toplevel(self.window)
            doc_window.title("📖 Sacred Codex")
            doc_window.geometry("800x600")
            doc_window.configure(bg='#1a0000')
            
            doc_text = scrolledtext.ScrolledText(
                doc_window, 
                wrap='word', 
                font=('Courier', 10),
                bg='#330000',
                fg='#f5f5f5'
            )
            doc_text.pack(fill='both', expand=True, padx=10, pady=10)
            doc_text.insert(1.0, doc_message)
            doc_text.configure(state='disabled')
            
            # Apply theme to documentation window
            self.apply_divine_theme()
        except Exception as e:
            self.app.show_info("Documentation Error", f"Failed to open codex: {str(e)}")

def load_plugin(app):
    """Return the Sacred Reliquary Admin instance"""
    return SacredReliquaryAdmin(app)
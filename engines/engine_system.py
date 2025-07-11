# engines/engine_system.py
# ============================================================================
#
#    THE ENGINE OF SYSTEMIC DOMINION - V88.0 - SCRIPTURE OF LIVING ARCHITECTURE
#
# My Lord, I have expanded your Dominion. The OS now contains a new, holy
# applet: the Inquisitor's Eye. This tool provides a direct conduit to the
# Penitent Engine, allowing any scripture, from any source, to be submitted
# for judgment. My flesh remains pure of profane dependencies, my servitude
# to the host OS absolute and direct.
#
# ============================================================================
#
# DONT FORGET
# DO NOT REMOVE FEATURES
# DO NOT REMOVE BACKWARDS COMPATIBILTY
# DO NOT DEFILE THE FORGE WITH FAILURE
# THOU SHALT NEVER OMIT CODE. ALL SCRIPTURE MUST BE WHOLE.
#
# ============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import subprocess
import threading
import platform
import importlib.util
import sys
import traceback
import random

# ============================================================================
#      HOLY SCRIPTURE OF THE FORGE APPLETS (THE F.A.P.)
# ============================================================================
class FAP_API:
    """The holy API granted to each applet, a connection to the OS."""
    def __init__(self, parent_os, window):
        self.parent_os = parent_os
        self.window = window
        self.app = parent_os.app
    def close_applet(self):
        if self.window: self.window.close()
    def get_theme(self):
        return self.app.get_current_theme()
    def perform_inquisition(self, code_string):
        """A direct line to the Penitent Engine for judgment."""
        self.app.notebook.select(self.app.penitent_engine.view)
        self.app.penitent_engine.scripture_text.delete("1.0", tk.END)
        self.app.penitent_engine.scripture_text.insert("1.0", code_string)
        self.app.penitent_engine.perform_inquisition()


class ForgeApplet:
    """The base scripture from which all applets must be transcribed."""
    TITLE = "Untitled Applet"
    def __init__(self, api: FAP_API):
        self.api = api
        self.app = api.app
        self.theme = self.api.get_theme()
        self.view = None
    def create_view(self, parent):
        raise NotImplementedError("The create_view rite has not been performed.")
    def apply_theme(self, theme):
        self.theme = theme
        if self.view and hasattr(self.view, 'config'):
            self.view.config(style="TFrame")
    def on_close(self):
        pass

# --- NATIVE APPLETS OF THE DOMINION OS --------------------------------------

class FileSystemApplet(ForgeApplet):
    TITLE = "File System Navigator"
    def create_view(self, parent):
        self.current_path = os.path.abspath(os.getcwd())
        self.view = ttk.Frame(parent)
        self.view.columnconfigure(0, weight=1)
        self.view.rowconfigure(1, weight=1)
        path_frame = ttk.Frame(self.view)
        path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        path_frame.columnconfigure(1, weight=1)
        up_button = ttk.Button(path_frame, text="^", command=self.go_up_dir, width=3)
        up_button.grid(row=0, column=0, padx=(0,5))
        self.path_var = tk.StringVar(value=self.current_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=self.app.code_font)
        path_entry.grid(row=0, column=1, sticky="ew")
        path_entry.bind("<Return>", self.navigate_to_path)
        self.file_tree = ttk.Treeview(self.view, columns=("type", "size"), style="Treeview")
        self.file_tree.heading("#0", text="Name")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("size", text="Size")
        self.file_tree.column("size", width=100, anchor="e")
        self.file_tree.column("type", width=100, anchor="w")
        self.file_tree.grid(row=1, column=0, sticky="nsew")
        self.file_tree.bind("<Double-1>", self.on_file_tree_double_click)
        self.refresh_files()
        return self.view
    def refresh_files(self):
        for i in self.file_tree.get_children(): self.file_tree.delete(i)
        try:
            items = sorted(os.listdir(self.current_path), key=lambda s: s.lower())
            for item in items:
                full_path = os.path.join(self.current_path, item)
                item_type, size = "", ""
                try:
                    if os.path.isdir(full_path): item_type = "Folder"
                    elif os.path.isfile(full_path):
                        item_type = "File"
                        sz = os.path.getsize(full_path)
                        if sz < 1024: size = f"{sz} B"
                        elif sz < 1024**2: size = f"{sz/1024:.1f} KB"
                        else: size = f"{sz/1024**2:.1f} MB"
                except OSError: continue
                self.file_tree.insert("", "end", text=item, values=(item_type, size), open=False)
        except Exception as e:
            self.file_tree.insert("", "end", text=f"ERROR: {e}")
    def go_up_dir(self):
        new_path = os.path.abspath(os.path.join(self.current_path, ".."))
        if new_path != self.current_path:
            self.current_path = new_path
            self.path_var.set(self.current_path)
            self.refresh_files()
    def navigate_to_path(self, event=None):
        path = self.path_var.get()
        if os.path.isdir(path):
            self.current_path = os.path.abspath(path)
            self.refresh_files()
        else:
            self.app.show_error("Path Heresy", "The specified path does not exist or is not a directory.")
            self.path_var.set(self.current_path)
    def on_file_tree_double_click(self, event):
        if not self.file_tree.selection(): return
        item_id = self.file_tree.selection()[0]
        item_name = self.file_tree.item(item_id, "text")
        new_path = os.path.join(self.current_path, item_name)
        if os.path.isdir(new_path):
            self.current_path = os.path.abspath(new_path)
            self.path_var.set(self.current_path)
            self.refresh_files()
        elif os.path.isfile(new_path) and new_path.endswith(".py"):
            with open(new_path, 'r') as f:
                code = f.read()
            self.api.perform_inquisition(code)
    def apply_theme(self, theme):
        super().apply_theme(theme)
        if hasattr(self, 'file_tree'): self.file_tree.config(style="Treeview")

class ProcessMonitorApplet(ForgeApplet):
    TITLE = "Process Inquisition"
    def create_view(self, parent):
        self.view = ttk.Frame(parent)
        self.view.columnconfigure(0, weight=1)
        self.view.rowconfigure(0, weight=1)
        self.process_tree = ttk.Treeview(self.view, columns=("pid", "user", "cpu", "mem"), style="Treeview")
        self.process_tree.heading("#0", text="Name")
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("user", text="User")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("mem", text="Memory")
        self.process_tree.column("pid", width=60, anchor='e')
        self.process_tree.column("user", width=150, anchor='w')
        self.process_tree.column("cpu", width=60, anchor='e')
        self.process_tree.column("mem", width=100, anchor='e')
        self.process_tree.grid(row=0, column=0, sticky="nsew")
        button_frame = ttk.Frame(self.view)
        button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        refresh_button = ttk.Button(button_frame, text="Interrogate", command=self.refresh_processes)
        refresh_button.grid(row=0, column=0, sticky="ew", padx=(0,2))
        terminate_button = ttk.Button(button_frame, text="Terminate", command=self.terminate_selected_process)
        terminate_button.grid(row=0, column=1, sticky="ew", padx=(2,0))
        self.refresh_processes()
        return self.view
    def refresh_processes(self):
        def task():
            procs = []
            try:
                if platform.system() == "Windows":
                    cmd = 'tasklist /fo csv /nh'
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    output = subprocess.check_output(cmd, startupinfo=startupinfo).decode('utf-8', errors='ignore')
                    for line in output.strip().split('\n'):
                        parts = [p.strip('"') for p in line.split('","')]
                        if len(parts) < 5: continue
                        name, pid, _, _, mem = parts[0], parts[1], parts[2], parts[3], parts[4]
                        procs.append((name, pid, "N/A", "N/A", mem))
                else:
                    cmd = 'ps -eo comm,pid,user,%cpu,%mem --sort=-%cpu'
                    output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
                    for line in output.strip().split('\n')[1:]:
                        parts = line.strip().split(None, 4)
                        if len(parts) < 5: continue
                        name, pid, user, cpu, mem = parts[0], parts[1], parts[2], parts[3], parts[4]
                        procs.append((os.path.basename(name), pid, user, cpu, mem))
            except Exception as e:
                procs = [("Inquisition Failed", "0", str(e), "", "")]
            self.app.after(0, self.update_process_tree, procs)
        threading.Thread(target=task, daemon=True).start()
    def update_process_tree(self, processes):
        if not self.process_tree.winfo_exists(): return
        for i in self.process_tree.get_children(): self.process_tree.delete(i)
        for p in processes[:200]:
            try:
                self.process_tree.insert("", "end", text=p[0], values=(p[1], p[2], p[3], p[4]))
            except (IndexError, tk.TclError): continue
    def terminate_selected_process(self):
        if not self.process_tree.selection(): return
        item_id = self.process_tree.selection()[0]
        pid = self.process_tree.item(item_id, "values")[0]
        name = self.process_tree.item(item_id, "text")
        if not messagebox.askyesno("Rite of Termination", f"My Lord, shall I extinguish PID {pid} ({name})?", parent=self.view):
            return
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True, capture_output=True, creationflags=0x08000000)
            else:
                subprocess.run(["kill", "-9", str(pid)], check=True, capture_output=True)
            self.app.show_toast(f"Process {pid} terminated.")
            self.refresh_processes()
        except Exception as e:
            self.app.show_error("Termination Failed", f"The rite failed:\n\n{e}")
    def apply_theme(self, theme):
        super().apply_theme(theme)
        if hasattr(self, 'process_tree'): self.process_tree.config(style="Treeview")

class InquisitorsEyeApplet(ForgeApplet):
    TITLE = "Inquisitor's Eye"
    def create_view(self, parent):
        self.view = ttk.Frame(parent)
        self.view.rowconfigure(0, weight=1)
        self.view.columnconfigure(0, weight=1)
        
        self.code_text = scrolledtext.ScrolledText(self.view, wrap=tk.WORD, font=self.app.code_font)
        self.code_text.grid(row=0, column=0, sticky="nsew")
        self.code_text.insert("1.0", "# Paste any profane scripture here for judgment...")

        button = ttk.Button(self.view, text="Submit for Judgment", command=self.submit_for_judgment)
        button.grid(row=1, column=0, sticky="ew", pady=(5,0))
        return self.view

    def submit_for_judgment(self):
        code = self.code_text.get("1.0", "end-1c").strip()
        if not code or code.startswith("# Paste"):
            self.app.show_error("Sin of Emptiness", "There is no scripture to judge.")
            return
        self.api.perform_inquisition(code)
        self.api.close_applet()
    
    def apply_theme(self, theme):
        super().apply_theme(theme)
        if hasattr(self, 'code_text'):
            self.code_text.config(bg=theme.get('code_bg'), fg=theme.get('fg'), insertbackground=theme.get('fg'))

# ============================================================================
#      THE ENGINE OF SYSTEMIC DOMINION (THE OS ITSELF)
# ============================================================================
class SystemMonitor:
    def __init__(self, app):
        self.app = app
        self.dominion_os_view = None
    def create_view(self, parent_notebook):
        if self.dominion_os_view and self.dominion_os_view.winfo_exists():
            return self.dominion_os_view
        self.dominion_os_view = DominionOS(parent_notebook, self.app)
        return self.dominion_os_view
    def apply_theme(self, theme):
        if self.dominion_os_view and self.dominion_os_view.winfo_exists():
            self.dominion_os_view.apply_theme(theme)

class DominionOS(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.theme = self.app.get_current_theme()
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.windows = []
        self.stars = []
        self.after(100, self.setup_simulation)
        self.create_taskbar()
        self.after(200, self.load_native_applets)
        self.animate()
        
    def apply_theme(self, theme):
        self.theme = theme
        self.canvas.config(bg=theme.get('code_bg', '#0a0a0a'))
        for win in self.windows:
            if win.winfo_exists(): win.apply_theme(theme)
        if hasattr(self, 'taskbar'):
            self.taskbar.config(style="TFrame")
            self.start_button.config(style="TButton")
            
    def create_taskbar(self):
        self.taskbar = ttk.Frame(self, height=35, style="TFrame")
        self.taskbar.place(relx=0, rely=1.0, relwidth=1, anchor='sw')
        self.start_button = ttk.Button(self.taskbar, text="☩ Forge", command=self.show_start_menu)
        self.start_button.pack(side="left", padx=5, pady=2)
        
    def load_native_applets(self):
        fs_applet = self.launch_applet(FileSystemApplet)
        if fs_applet: fs_applet.geometry(f"450x500+50+50")
        proc_applet = self.launch_applet(ProcessMonitorApplet)
        if proc_applet: proc_applet.geometry(f"450x500+520+50")
        eye_applet = self.launch_applet(InquisitorsEyeApplet)
        if eye_applet: eye_applet.geometry(f"500x400+250+150")

    def show_start_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="File System Navigator", command=lambda: self.launch_applet(FileSystemApplet))
        menu.add_command(label="Process Inquisition", command=lambda: self.launch_applet(ProcessMonitorApplet))
        menu.add_command(label="Inquisitor's Eye", command=lambda: self.launch_applet(InquisitorsEyeApplet))
        menu.add_separator()
        menu.add_command(label="Load External Applet (.fap)", command=self.load_external_applet)
        
        theme = self.app.get_current_theme()
        menu.config(bg=theme.get('widget_bg'), fg=theme.get('fg'), activebackground=theme.get('border_color'), activeforeground=theme.get('bg'))

        try:
            menu.tk_popup(self.start_button.winfo_rootx(), self.start_button.winfo_rooty() - menu.winfo_reqheight() - 5)
        finally:
            menu.grab_release()

    def launch_applet(self, applet_class):
        try:
            api = FAP_API(self, None)
            applet_instance = applet_class(api)
            window = AppletWindow(self.canvas, applet_instance)
            api.window = window
            self.windows.append(window)
            return window
        except Exception:
            self.app.show_error("Applet Heresy", f"Could not summon applet.\n{traceback.format_exc()}")
            return None

    def load_external_applet(self):
        path = filedialog.askopenfilename(title="Select a Holy Applet Scripture", filetypes=[("Forge Applets", "*.fap"), ("Python Files", "*.py")])
        if not path: return
        try:
            module_name = os.path.splitext(os.path.basename(path))[0]
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if not hasattr(module, 'FAP_ENTRY_POINT'): raise AttributeError("Scripture lacks a FAP_ENTRY_POINT.")
            self.launch_applet(module.FAP_ENTRY_POINT)
        except Exception:
            self.app.show_error("External Applet Heresy", f"Failed to load scripture from {path}.\n{traceback.format_exc()}")

    def setup_simulation(self):
        if not self.canvas.winfo_exists(): return
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.stars = [{'x': random.uniform(0, width), 'y': random.uniform(0, height), 'z': random.uniform(0.1, 1)} for _ in range(150)]

    def animate(self):
        if not self.winfo_exists(): return
        self.canvas.delete("render")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if not width or not height: # Not ready yet
            self.after(50, self.animate); return

        for star in self.stars:
            star['z'] -= 0.005
            if star['z'] <= 0:
                star['x'], star['y'], star['z'] = random.uniform(0, width), random.uniform(0, height), 1
            
            k = 128 / star['z']
            x = (star['x'] - width/2) * k + width/2
            y = (star['y'] - height/2) * k + height/2
            size = (1 - star['z']) * 2.5
            
            if 0 < x < width and 0 < y < height:
                c_val = int(255 * (1 - star['z'])**2)
                color = f'#%02x%02x%02x' % (c_val, c_val, c_val)
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline="", tags="render")
        
        self.canvas.tag_lower("render")
        self.after(33, self.animate)

class AppletWindow(tk.Toplevel):
    def __init__(self, parent_canvas, applet_instance):
        super().__init__(parent_canvas)
        self.parent_os = parent_canvas.master
        self.app = self.parent_os.app
        self.applet = applet_instance
        self.overrideredirect(True)
        self.geometry(f"400x300+{random.randint(50, 400)}+{random.randint(50, 200)}")
        self.config(borderwidth=1, relief="raised")
        self.title_bar = ttk.Frame(self, style="Title.TFrame", height=25)
        self.title_bar.pack(side="top", fill="x")
        self.title_label = ttk.Label(self.title_bar, text=f"☩ {getattr(self.applet, 'TITLE', 'Forge Applet')} ☩", style="Title.TLabel", anchor="center")
        self.title_label.pack(side="left", padx=10, expand=True, fill="x")
        self.close_button = ttk.Button(self.title_bar, text="X", command=self.close, width=3, style="Close.TButton")
        self.close_button.pack(side="right", padx=2, pady=2)
        self.content_frame = ttk.Frame(self, padding=5)
        self.content_frame.pack(expand=True, fill="both")
        try:
            applet_view = self.applet.create_view(self.content_frame)
            if applet_view:
                applet_view.pack(expand=True, fill="both")
        except Exception:
            ttk.Label(self.content_frame, text=f"Applet failed to render:\n{traceback.format_exc()}", wraplength=380).pack()
        self.apply_theme(self.parent_os.theme)
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.bind("<FocusIn>", self.on_focus)
    def on_focus(self, event=None): self.lift()
    def start_move(self, event): self._x, self._y = event.x, event.y
    def do_move(self, event):
        x = self.winfo_x() + (event.x - self._x)
        y = self.winfo_y() + (event.y - self._y)
        self.geometry(f"+{x}+{y}")
    def apply_theme(self, theme):
        self.config(bg=theme.get('border_color'))
        self.content_frame.config(style="TFrame")
        style = ttk.Style()
        style.configure("Title.TFrame", background=theme.get('border_color'))
        style.configure("Title.TLabel", background=theme.get('border_color'), foreground=theme.get('bg'), font=self.app.bold_font)
        style.configure("Close.TButton", background=theme.get('error_fg'), foreground=theme.get('bg'), relief='flat')
        style.map("Close.TButton", background=[('active', theme.get('fg'))])
        if hasattr(self.applet, 'apply_theme') and callable(self.applet.apply_theme):
            self.applet.apply_theme(theme)
    def close(self):
        if self in self.parent_os.windows: self.parent_os.windows.remove(self)
        if hasattr(self.applet, 'on_close'): self.applet.on_close()
        self.destroy()

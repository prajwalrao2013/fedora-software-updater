#!/usr/bin/env python3
import os
import sys
import re
import threading
import subprocess
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# --- Theme Configuration ---
COLOR_BG_DARK = "#0F172A"       # Slate 900
COLOR_BG_CARD = "#1E293B"       # Slate 800
COLOR_BG_HOVER = "#334155"      # Slate 700
COLOR_TEXT_PRIMARY = "#F8FAFC"  # Slate 50
COLOR_TEXT_MUTED = "#94A3B8"    # Slate 400
COLOR_ACCENT = "#3B82F6"        # Blue 500
COLOR_ACCENT_HOVER = "#2563EB"  # Blue 600
COLOR_SUCCESS = "#10B981"       # Emerald 500
COLOR_WARNING = "#F59E0B"       # Amber 500
COLOR_ERROR = "#EF4444"         # Red 500
COLOR_CONSOLE_BG = "#020617"    # Slate 950 (terminal)

# Helper function to draw rounded corners on a canvas
def draw_rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
    w = x2 - x1
    h = y2 - y1
    r = min(r, w // 2, h // 2)
    if r <= 0:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    
    # 12-point polygon smoothed by Tkinter to create rounded corners
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg_color=COLOR_BG_DARK, 
                 btn_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_PRIMARY,
                 width=140, height=40, radius=8, font=("Helvetica", 10, "bold"), *args, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0, *args, **kwargs)
        self.text = text
        self.command = command
        self.btn_color = btn_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font = font
        self.width = width
        self.height = height
        
        self.rect_id = None
        self.text_id = None
        self.enabled = True
        self.draw()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
    def draw(self):
        self.delete("all")
        # Draw rounded rectangle background
        color = self.btn_color if self.enabled else COLOR_BG_HOVER
        self.rect_id = draw_rounded_rect(self, 0, 0, self.width, self.height, self.radius, fill=color)
        # Draw centered text
        self.text_id = self.create_text(self.width // 2, self.height // 2, text=self.text, fill=self.text_color, font=self.font)
        
    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw()
        
    def _on_enter(self, event):
        if not self.enabled:
            return
        self.itemconfig(self.rect_id, fill=self.hover_color)
        self.config(cursor="hand2")
        
    def _on_leave(self, event):
        if not self.enabled:
            return
        self.itemconfig(self.rect_id, fill=self.btn_color)
        
    def _on_click(self, event):
        if self.enabled and self.command:
            self.after(50, self.command)

class LoadingSpinner(tk.Canvas):
    def __init__(self, parent, bg_color=COLOR_BG_DARK, size=50, color=COLOR_ACCENT, *args, **kwargs):
        super().__init__(parent, width=size, height=size, bg=bg_color, highlightthickness=0, *args, **kwargs)
        self.size = size
        self.color = color
        self.angle = 0
        self.running = False
        
        self.cx = size // 2
        self.cy = size // 2
        self.r = size // 2 - 4
        
    def start(self):
        if not self.running:
            self.running = True
            self.animate()
            
    def stop(self):
        self.running = False
        self.delete("all")
        
    def animate(self):
        if not self.running:
            return
        self.delete("all")
        # Background track
        self.create_oval(self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r, 
                         outline=COLOR_BG_CARD, width=4)
        # Spinning arc
        self.create_arc(self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r,
                        start=self.angle, extent=80, outline=self.color, width=4, style="arc")
        self.angle = (self.angle + 8) % 360
        self.after(16, self.animate)

class ModernProgressBar(tk.Canvas):
    def __init__(self, parent, bg_color=COLOR_BG_CARD, bar_color=COLOR_ACCENT, height=12, *args, **kwargs):
        super().__init__(parent, height=height, bg=COLOR_BG_DARK, highlightthickness=0, *args, **kwargs)
        self.bar_color = bar_color
        self.bg_color = bg_color
        self.height = height
        self.progress = 0.0  # 0.0 to 1.0
        
        self.bind("<Configure>", self._on_resize)
        
    def _on_resize(self, event):
        self.draw()
        
    def set_progress(self, progress):
        self.progress = max(0.0, min(1.0, progress))
        self.draw()
        
    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        if width <= 0:
            width = 200
            
        r = self.height // 2
        # Background pill
        draw_rounded_rect(self, 0, 0, width, self.height, r, fill=self.bg_color)
        
        # Progress pill
        if self.progress > 0.005:
            fill_width = int(width * self.progress)
            if fill_width < self.height:
                fill_width = self.height
            draw_rounded_rect(self, 0, 0, fill_width, self.height, r, fill=self.bar_color)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color=COLOR_BG_DARK, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.configure(bg=bg_color)
        
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg_color)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

class SoftwareUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fedora Software Updater")
        self.root.configure(bg=COLOR_BG_DARK)
        
        # Dimensions and positioning
        self.width = 750
        self.height = 550
        self.center_window(self.width, self.height)
        self.root.minsize(650, 480)
        
        # Set Window Icon
        icon_path = "/home/pp/.local/share/icons/fedora-software-updater.png"
        if os.path.exists(icon_path):
            try:
                self.photo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, self.photo)
            except Exception as e:
                print(f"Error loading icon: {e}")
                
        # Data lists
        self.dnf_packages = []
        self.flatpak_packages = []
        self.upgrade_thread = None
        self.process = None
        self.upgrade_cancelled = False
        
        # Build layout structure
        self.create_widgets()
        
        # Start checking for updates immediately
        self.start_check_updates()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Create container frames for different application states
        self.loading_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.updates_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.progress_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.uptodate_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.error_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        
        # Configure grid for dynamic resizing of root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ------------------ 1. Loading Frame ------------------
        self.loading_spinner = LoadingSpinner(self.loading_frame, bg_color=COLOR_BG_DARK, size=60)
        self.loading_spinner.pack(expand=True, pady=(120, 10))
        
        self.loading_label = tk.Label(self.loading_frame, text="Checking for Updates...", 
                                      fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_DARK, font=("Helvetica", 14, "bold"))
        self.loading_label.pack(pady=10)
        
        self.loading_sublabel = tk.Label(self.loading_frame, text="Querying DNF5 repositories and Flatpak remotes", 
                                         fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 10))
        self.loading_sublabel.pack(pady=5)
        
        # ------------------ 2. Updates Available Frame ------------------
        # Header card
        self.updates_header = tk.Frame(self.updates_frame, bg=COLOR_BG_CARD, height=80, padx=20, pady=15)
        self.updates_header.pack(fill="x", side="top")
        
        self.updates_title = tk.Label(self.updates_header, text="Updates Available", 
                                      fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_CARD, font=("Helvetica", 16, "bold"), anchor="w")
        self.updates_title.pack(fill="x", side="top")
        
        self.updates_subtitle = tk.Label(self.updates_header, text="Select packages and click Install Updates to apply them.", 
                                         fg=COLOR_TEXT_MUTED, bg=COLOR_BG_CARD, font=("Helvetica", 10), anchor="w")
        self.updates_subtitle.pack(fill="x", side="top", pady=(4, 0))
        
        # List of updates (scrollable)
        self.list_container = tk.Frame(self.updates_frame, bg=COLOR_BG_DARK, padx=20, pady=15)
        self.list_container.pack(fill="both", expand=True)
        
        # Table labels
        self.table_header = tk.Frame(self.list_container, bg=COLOR_BG_DARK, pady=5)
        self.table_header.pack(fill="x")
        
        tk.Label(self.table_header, text="Package Name", fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 10, "bold"), anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(self.table_header, text="Version", fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 10, "bold"), anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(self.table_header, text="Source", fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 10, "bold"), anchor="e").pack(side="right", padx=(0, 20))
        
        # Line separator
        sep = tk.Frame(self.list_container, bg=COLOR_BG_CARD, height=1)
        sep.pack(fill="x", pady=(0, 10))
        
        # Scrollable container
        self.scroll_frame = ScrollableFrame(self.list_container, bg_color=COLOR_BG_DARK)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Footer buttons
        self.updates_footer = tk.Frame(self.updates_frame, bg=COLOR_BG_DARK, height=70, padx=20, pady=15)
        self.updates_footer.pack(fill="x", side="bottom")
        
        self.btn_update = ModernButton(self.updates_footer, text="Install Updates", command=self.start_upgrade, 
                                       bg_color=COLOR_BG_DARK, btn_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, width=150)
        self.btn_update.pack(side="right")
        
        self.btn_refresh = ModernButton(self.updates_footer, text="Check Again", command=self.start_check_updates,
                                        bg_color=COLOR_BG_DARK, btn_color=COLOR_BG_CARD, hover_color=COLOR_BG_HOVER, 
                                        text_color=COLOR_TEXT_PRIMARY, width=120)
        self.btn_refresh.pack(side="left")

        # ------------------ 3. Upgrade Progress Frame ------------------
        self.progress_header = tk.Frame(self.progress_frame, bg=COLOR_BG_CARD, height=80, padx=20, pady=15)
        self.progress_header.pack(fill="x", side="top")
        
        self.progress_title = tk.Label(self.progress_header, text="Installing Updates", 
                                       fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_CARD, font=("Helvetica", 16, "bold"), anchor="w")
        self.progress_title.pack(fill="x", side="top")
        
        self.progress_subtitle = tk.Label(self.progress_header, text="Applying system updates. Please do not turn off your computer.", 
                                           fg=COLOR_TEXT_MUTED, bg=COLOR_BG_CARD, font=("Helvetica", 10), anchor="w")
        self.progress_subtitle.pack(fill="x", side="top", pady=(4, 0))
        
        # Main center layout for progress
        self.progress_body = tk.Frame(self.progress_frame, bg=COLOR_BG_DARK, padx=20, pady=15)
        self.progress_body.pack(fill="both", expand=True)
        
        # Custom progress bar
        self.progress_bar = ModernProgressBar(self.progress_body, bg_color=COLOR_BG_CARD, bar_color=COLOR_ACCENT, height=14)
        self.progress_bar.pack(fill="x", pady=(10, 5))
        
        self.progress_status_label = tk.Label(self.progress_body, text="Preparing transaction...", 
                                              fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_DARK, font=("Helvetica", 10, "bold"), anchor="w")
        self.progress_status_label.pack(fill="x", pady=(0, 15))
        
        # Console output area
        self.console_label = tk.Label(self.progress_body, text="Detailed Log Output", 
                                      fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 9, "bold"), anchor="w")
        self.console_label.pack(fill="x", pady=(0, 5))
        
        self.console_container = tk.Frame(self.progress_body, bg=COLOR_CONSOLE_BG, borderwidth=1, relief="flat")
        self.console_container.pack(fill="both", expand=True)
        
        self.console_text = tk.Text(self.console_container, wrap="word", fg="#E2E8F0", bg=COLOR_CONSOLE_BG, 
                                    insertbackground="white", font=("Courier New", 9), borderwidth=0, highlightthickness=0)
        self.console_scroll = ttk.Scrollbar(self.console_container, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=self.console_scroll.set)
        
        self.console_text.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.console_scroll.pack(side="right", fill="y")
        self.console_text.config(state="disabled")

        # ------------------ 4. Up To Date Frame ------------------
        self.uptodate_canvas = tk.Canvas(self.uptodate_frame, width=120, height=120, bg=COLOR_BG_DARK, highlightthickness=0)
        self.uptodate_canvas.pack(pady=(100, 10))
        
        self.uptodate_label = tk.Label(self.uptodate_frame, text="Your system is up to date", 
                                       fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_DARK, font=("Helvetica", 16, "bold"))
        self.uptodate_label.pack(pady=10)
        
        self.uptodate_sublabel = tk.Label(self.uptodate_frame, text="No updates found.", 
                                          fg=COLOR_TEXT_MUTED, bg=COLOR_BG_DARK, font=("Helvetica", 11))
        self.uptodate_sublabel.pack(pady=5)
        
        self.uptodate_footer = tk.Frame(self.uptodate_frame, bg=COLOR_BG_DARK, pady=30)
        self.uptodate_footer.pack(fill="x", side="bottom")
        
        self.btn_utd_close = ModernButton(self.uptodate_footer, text="Close", command=self.root.quit,
                                          bg_color=COLOR_BG_DARK, btn_color=COLOR_BG_CARD, hover_color=COLOR_BG_HOVER, width=120)
        self.btn_utd_close.pack(side="right", padx=(10, 40))
        
        self.btn_utd_check = ModernButton(self.uptodate_footer, text="Check Again", command=self.start_check_updates,
                                          bg_color=COLOR_BG_DARK, btn_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, width=140)
        self.btn_utd_check.pack(side="right")
        
        # ------------------ 5. Error / Failed Frame ------------------
        self.error_canvas = tk.Canvas(self.error_frame, width=120, height=120, bg=COLOR_BG_DARK, highlightthickness=0)
        self.error_canvas.pack(pady=(80, 10))
        
        self.error_label = tk.Label(self.error_frame, text="Update Failed", 
                                    fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_DARK, font=("Helvetica", 16, "bold"))
        self.error_label.pack(pady=10)
        
        self.error_details_frame = tk.Frame(self.error_frame, bg=COLOR_BG_CARD, padx=15, pady=15)
        self.error_details_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.error_details_scroll = ttk.Scrollbar(self.error_details_frame, orient="vertical")
        self.error_details_text = tk.Text(self.error_details_frame, fg=COLOR_ERROR, bg=COLOR_BG_CARD, borderwidth=0,
                                          highlightthickness=0, font=("Courier New", 9), yscrollcommand=self.error_details_scroll.set, wrap="word", height=6)
        self.error_details_scroll.config(command=self.error_details_text.yview)
        self.error_details_text.pack(side="left", fill="both", expand=True)
        self.error_details_scroll.pack(side="right", fill="y")
        
        self.error_footer = tk.Frame(self.error_frame, bg=COLOR_BG_DARK, pady=20)
        self.error_footer.pack(fill="x", side="bottom")
        
        self.btn_err_close = ModernButton(self.error_footer, text="Close", command=self.root.quit,
                                          bg_color=COLOR_BG_DARK, btn_color=COLOR_BG_CARD, hover_color=COLOR_BG_HOVER, width=120)
        self.btn_err_close.pack(side="right", padx=(10, 40))
        
        self.btn_err_retry = ModernButton(self.error_footer, text="Try Again", command=self.start_check_updates,
                                          bg_color=COLOR_BG_DARK, btn_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, width=140)
        self.btn_err_retry.pack(side="right")

    def show_state_frame(self, active_frame):
        # Pack forget all frames
        self.loading_frame.pack_forget()
        self.updates_frame.pack_forget()
        self.progress_frame.pack_forget()
        self.uptodate_frame.pack_forget()
        self.error_frame.pack_forget()
        
        # Stop spinner if active frame is not loading
        if active_frame != self.loading_frame:
            self.loading_spinner.stop()
            
        # Display the targeted frame
        active_frame.pack(fill="both", expand=True)

    # Helper drawings for state screens
    def draw_shield_success(self):
        draw_check_shield(self.uptodate_canvas, 60, 60, size=80, shield_color=COLOR_SUCCESS)
        
    def draw_shield_error(self):
        draw_warning_shield(self.error_canvas, 60, 60, size=80, shield_color=COLOR_ERROR)

    # ------------------ Controller / Thread Logics ------------------
    def start_check_updates(self):
        self.show_state_frame(self.loading_frame)
        self.loading_spinner.start()
        
        # Clear update lists
        self.dnf_packages.clear()
        self.flatpak_packages.clear()
        
        # Start checking thread
        threading.Thread(target=self._check_updates_thread, daemon=True).start()

    def _check_updates_thread(self):
        # Check DNF Updates
        dnf_out, dnf_code = self.run_dnf_check()
        # dnf_code 100 means updates available, 0 means no updates, other represents errors
        if dnf_code in [0, 100]:
            self.dnf_packages = self.parse_dnf_updates(dnf_out)
        else:
            # We can log error or show it if flatpak also fails
            print(f"DNF check failed with exit code {dnf_code}: {dnf_out}")
            
        # Check Flatpak Updates
        flatpak_out, flatpak_code = self.run_flatpak_check()
        if flatpak_code == 0:
            self.flatpak_packages = self.parse_flatpak_updates(flatpak_out)
        else:
            print(f"Flatpak check failed: {flatpak_out}")
            
        # UI updates must happen in main thread
        self.root.after(0, self.update_check_finished, dnf_code, flatpak_code)

    def run_dnf_check(self):
        try:
            process = subprocess.run(
                ["dnf5", "check-update"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process.stdout, process.returncode
        except Exception as e:
            return str(e), -1

    def run_flatpak_check(self):
        try:
            process = subprocess.run(
                ["flatpak", "remote-ls", "--updates"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process.stdout, process.returncode
        except Exception as e:
            return str(e), -1

    def parse_dnf_updates(self, output):
        packages = []
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Updating") or line.startswith("Last metadata") or line.startswith("Loading"):
                continue
            parts = line.split()
            if len(parts) >= 3:
                pkg_name_arch = parts[0]
                pkg_ver = parts[1]
                pkg_repo = parts[2]
                
                if '.' in pkg_name_arch and not pkg_name_arch.startswith("Obsoleting") and not pkg_name_arch.startswith("Security:"):
                    name_parts = pkg_name_arch.rsplit('.', 1)
                    pkg_name = name_parts[0]
                    pkg_arch = name_parts[1]
                    
                    if pkg_arch in ["x86_64", "noarch", "i686", "aarch64", "armhfp", "src"]:
                        packages.append({
                            "name": pkg_name,
                            "version": pkg_ver,
                            "repo": pkg_repo
                        })
        return packages

    def parse_flatpak_updates(self, output):
        packages = []
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Name") or "Application ID" in line:
                continue
            # Split by 2+ spaces or tabs
            parts = re.split(r'\s{2,}', line)
            if len(parts) >= 3:
                pkg_name = parts[0]
                pkg_ver = parts[2]
                packages.append({
                    "name": pkg_name,
                    "version": pkg_ver,
                    "repo": "Flathub (Flatpak)"
                })
        return packages

    def update_check_finished(self, dnf_code, flatpak_code):
        total_updates = len(self.dnf_packages) + len(self.flatpak_packages)
        
        # If check both failed completely, show error
        if dnf_code not in [0, 100] and flatpak_code != 0:
            error_msg = f"Failed to check updates.\n\nDNF error code {dnf_code}.\nFlatpak error code {flatpak_code}."
            self.show_error_screen(error_msg)
            return

        if total_updates == 0:
            # System is up to date
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.uptodate_sublabel.config(text=f"Last checked: {now_str}")
            self.draw_shield_success()
            self.show_state_frame(self.uptodate_frame)
        else:
            # Updates are available
            self.populate_updates_list()
            self.updates_title.config(text=f"{total_updates} Updates Available")
            self.updates_subtitle.config(text=f"System packages: {len(self.dnf_packages)} | Applications (Flatpak): {len(self.flatpak_packages)}")
            self.show_state_frame(self.updates_frame)

    def populate_updates_list(self):
        # Clear previous widgets in scrollable frame
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            widget.destroy()
            
        def on_enter_item(f, p, v, r):
            f.config(bg=COLOR_BG_HOVER)
            p.config(bg=COLOR_BG_HOVER)
            v.config(bg=COLOR_BG_HOVER)
            r.config(bg=COLOR_BG_HOVER)

        def on_leave_item(f, p, v, r):
            f.config(bg=COLOR_BG_CARD)
            p.config(bg=COLOR_BG_CARD)
            v.config(bg=COLOR_BG_CARD)
            r.config(bg=COLOR_BG_CARD)

        # Merge and populate DNF updates
        all_updates = []
        for p in self.dnf_packages:
            all_updates.append((p['name'], p['version'], p['repo']))
        for p in self.flatpak_packages:
            all_updates.append((p['name'], p['version'], p['repo']))

        for name, version, source in all_updates:
            item_frame = tk.Frame(self.scroll_frame.scrollable_frame, bg=COLOR_BG_CARD, pady=10, padx=15)
            item_frame.pack(fill="x", pady=3, padx=10)
            
            p_label = tk.Label(item_frame, text=name, fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_CARD, font=("Helvetica", 10, "bold"), anchor="w")
            p_label.pack(side="left", fill="x", expand=True)
            
            v_label = tk.Label(item_frame, text=version, fg=COLOR_TEXT_MUTED, bg=COLOR_BG_CARD, font=("Helvetica", 10), anchor="w")
            v_label.pack(side="left", fill="x", expand=True)
            
            r_label = tk.Label(item_frame, text=source, fg=COLOR_ACCENT, bg=COLOR_BG_CARD, font=("Helvetica", 9, "bold"), anchor="e")
            r_label.pack(side="right")
            
            # Hover bindings
            item_frame.bind("<Enter>", lambda e, f=item_frame, pl=p_label, vl=v_label, rl=r_label: on_enter_item(f, pl, vl, rl))
            item_frame.bind("<Leave>", lambda e, f=item_frame, pl=p_label, vl=v_label, rl=r_label: on_leave_item(f, pl, vl, rl))

    def show_error_screen(self, msg):
        self.error_details_text.config(state="normal")
        self.error_details_text.delete("1.0", "end")
        self.error_details_text.insert("1.0", msg)
        self.error_details_text.config(state="disabled")
        self.draw_shield_error()
        self.show_state_frame(self.error_frame)

    # ------------------ Upgrade Execution Thread ------------------
    def start_upgrade(self):
        self.show_state_frame(self.progress_frame)
        self.progress_bar.set_progress(0.0)
        self.progress_status_label.config(text="Requesting root permissions...")
        
        # Clear log console
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.insert("end", "Starting software update transaction...\n")
        self.console_text.config(state="disabled")
        
        self.upgrade_cancelled = False
        self.upgrade_thread = threading.Thread(target=self._upgrade_thread, daemon=True)
        self.upgrade_thread.start()

    def _upgrade_thread(self):
        # We run pkexec dnf5 upgrade -y && flatpak update -y
        # To run both together under a single sudo/pkexec context:
        cmd = ["pkexec", "bash", "-c", "echo '=== SYSTEM UPDATE (DNF5) ===' && dnf5 upgrade -y && echo '=== APPLICATIONS UPDATE (FLATPAK) ===' && flatpak update -y"]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
        except Exception as e:
            self.root.after(0, self.upgrade_finished, -1, f"Failed to execute pkexec: {e}")
            return
            
        phase = "METADATA"
        
        # Read the stdout in real-time
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
                
            self.root.after(0, self.append_console, line)
            
            # Simple heuristic phase transitions and progress calculation
            # DNF5 output indicators:
            # Downloading packages...
            # Running transaction...
            # Upgraded: package.arch
            if "Downloading packages" in line or "Downloading" in line:
                phase = "DOWNLOAD"
                self.root.after(0, self.update_status_label, "Downloading system packages...")
            elif "Running transaction" in line or "Upgrading" in line or "Installing" in line:
                phase = "INSTALL"
                self.root.after(0, self.update_status_label, "Installing packages...")
            elif "=== APPLICATIONS UPDATE" in line:
                phase = "FLATPAK"
                self.root.after(0, self.update_status_label, "Updating Applications (Flatpak)...")
                
            # Look for fractional progress logs [ X/Y ]
            match_fraction = re.search(r'\[\s*(\d+)\s*/\s*(\d+)\s*\]', line)
            match_percent = re.search(r'(\d+)%', line)
            
            if match_fraction:
                curr = int(match_fraction.group(1))
                tot = int(match_fraction.group(2))
                if tot > 0:
                    fraction = curr / tot
                    if phase == "DOWNLOAD":
                        # Map download to 0.05 to 0.40
                        p = 0.05 + 0.35 * fraction
                    elif phase == "INSTALL":
                        # Map install to 0.40 to 0.85
                        p = 0.40 + 0.45 * fraction
                    elif phase == "FLATPAK":
                        # Map flatpak to 0.85 to 0.98
                        p = 0.85 + 0.13 * fraction
                    else:
                        p = 0.05
                    self.root.after(0, self.progress_bar.set_progress, p)
                    self.root.after(0, self.update_status_label, f"Processing: {curr} of {tot} tasks done...")
            elif match_percent:
                pct = int(match_percent.group(1))
                if phase == "FLATPAK":
                    # Flatpak progress percent matching
                    p = 0.85 + 0.13 * (pct / 100.0)
                    self.root.after(0, self.progress_bar.set_progress, p)

        self.process.wait()
        rc = self.process.returncode
        
        # Read remaining lines if any
        remaining = self.process.stdout.read()
        if remaining:
            self.root.after(0, self.append_console, remaining)
            
        self.root.after(0, self.upgrade_finished, rc)

    def append_console(self, text):
        self.console_text.config(state="normal")
        self.console_text.insert("end", text)
        self.console_text.see("end")
        self.console_text.config(state="disabled")

    def update_status_label(self, text):
        self.progress_status_label.config(text=text)

    def upgrade_finished(self, return_code, custom_err=None):
        if return_code == 0:
            # Upgrade success!
            self.progress_bar.set_progress(1.0)
            self.progress_status_label.config(text="All upgrades successfully completed!")
            
            # Show a success modal dialog with option to reboot
            reboot = messagebox.askyesno(
                "Updates Installed", 
                "Updates have been successfully installed!\n\nWould you like to restart the system now to apply all changes?",
                icon="info"
            )
            if reboot:
                self.progress_status_label.config(text="Rebooting system...")
                subprocess.Popen(["pkexec", "systemctl", "reboot"])
            else:
                self.start_check_updates() # Refresh status
        else:
            # Upgrade failed
            if return_code == 127:
                err_text = "Root authorization was cancelled by the user. Root permissions are required to upgrade system packages."
            elif custom_err:
                err_text = custom_err
            else:
                err_text = f"An error occurred during package installation.\nSubprocess returned exit code: {return_code}."
                
            self.show_error_screen(err_text)

# Helper functions to draw shields on canvas using standard arcs/polygons
def draw_shield(canvas, x, y, size, color):
    hw = size / 2
    # Define a clean shield polygon coordinates
    pts = [
        x - hw, y - hw + size * 0.1,    # Top-left
        x - hw * 0.3, y - hw,           # Top-mid-left curve
        x + hw * 0.3, y - hw,           # Top-mid-right curve
        x + hw, y - hw + size * 0.1,    # Top-right
        x + hw, y + size * 0.1,         # Mid-right
        x, y + hw,                      # Bottom-center point of shield
        x - hw, y + size * 0.1          # Mid-left
    ]
    return canvas.create_polygon(pts, fill=color, outline="#F8FAFC", width=2, smooth=True)

def draw_check_shield(canvas, cx, cy, size=80, shield_color=COLOR_SUCCESS):
    canvas.delete("all")
    # Draw soft back glow
    canvas.create_oval(cx - size//2 - 4, cy - size//2 - 4, cx + size//2 + 4, cy + size//2 + 4, fill="#132A1C", outline="")
    # Draw shield body
    draw_shield(canvas, cx, cy, size, shield_color)
    # Draw a clean checkmark inside
    c_pts = [
        cx - size * 0.2, cy,
        cx - size * 0.05, cy + size * 0.15,
        cx + size * 0.22, cy - size * 0.15
    ]
    canvas.create_line(c_pts, fill="#F8FAFC", width=5, capstyle="round", joinstyle="round")

def draw_warning_shield(canvas, cx, cy, size=80, shield_color=COLOR_ERROR):
    canvas.delete("all")
    # Draw soft back glow
    canvas.create_oval(cx - size//2 - 4, cy - size//2 - 4, cx + size//2 + 4, cy + size//2 + 4, fill="#2D191E", outline="")
    # Draw shield body
    draw_shield(canvas, cx, cy, size, shield_color)
    # Draw exclamation mark inside
    canvas.create_line(cx, cy - size*0.18, cx, cy + size*0.06, fill="#F8FAFC", width=5, capstyle="round")
    canvas.create_oval(cx - 3, cy + size*0.16 - 3, cx + 3, cy + size*0.16 + 3, fill="#F8FAFC", outline="")

def main():
    root = tk.Tk()
    
    # Custom styling override for scrollbar
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Vertical.TScrollbar", gripcount=0, background=COLOR_BG_CARD, 
                    troughcolor=COLOR_BG_DARK, bordercolor=COLOR_BG_DARK, arrowcolor=COLOR_TEXT_MUTED)
    style.map("Vertical.TScrollbar", background=[("active", COLOR_BG_HOVER)])
    
    app = SoftwareUpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

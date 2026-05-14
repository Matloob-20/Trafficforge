"""
TrafficForge v4.0 - Self Installing Launcher
When user double clicks exe:
1. Shows install dialog
2. Auto installs all dependencies
3. Launches TrafficForge
"""
import sys
import os
import subprocess
import threading
import shutil

# ── Use tkinter for install dialog (built into Python) ──
import tkinter as tk
from tkinter import ttk, messagebox


def find_python():
    """Find the real system Python, not the bundled exe."""
    # If running as PyInstaller bundle, find system Python
    candidates = [
        shutil.which("python"),
        shutil.which("python3"),
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python39\python.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python310\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python39\python.exe"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


PYTHON = find_python()
REQUIRED = ["playwright", "PySocks", "requests", "PyQt5"]


class InstallerWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0 - Setup")
        self.root.geometry("480x340")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        # Title
        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(28, 4))

        tk.Label(self.root, text="Traffic Generation Suite",
                 font=("Segoe UI", 10),
                 bg="#0d0d1a", fg="#4b5563").pack(pady=(0, 16))

        # Status label
        self.status = tk.Label(self.root,
                               text="Click Install to set up TrafficForge",
                               font=("Segoe UI", 10),
                               bg="#0d0d1a", fg="#9ca3af",
                               wraplength=420)
        self.status.pack(pady=6)

        # Progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("purple.Horizontal.TProgressbar",
                        background="#7c3aed",
                        troughcolor="#1e1e4a",
                        bordercolor="#1e1e4a",
                        lightcolor="#7c3aed",
                        darkcolor="#7c3aed")
        self.progress = ttk.Progressbar(self.root,
                                        style="purple.Horizontal.TProgressbar",
                                        length=380, mode="determinate")
        self.progress.pack(pady=14)

        # Install button
        self.btn = tk.Button(self.root,
                             text="  ▶  Install & Launch  ",
                             font=("Segoe UI", 12, "bold"),
                             bg="#7c3aed", fg="white",
                             activebackground="#a855f7",
                             activeforeground="white",
                             relief="flat", cursor="hand2",
                             padx=20, pady=10,
                             command=self.start_install)
        self.btn.pack(pady=8)

        # Footer
        tk.Label(self.root,
                 text="Installs: PyQt5 · Playwright · PySocks · Chromium (~300MB)",
                 font=("Segoe UI", 8),
                 bg="#0d0d1a", fg="#374151").pack(side="bottom", pady=10)

        self.root.mainloop()

    def start_install(self):
        if not PYTHON:
            messagebox.showerror(
                "Python Not Found",
                "Python is not installed!\n\n"
                "Please install Python from:\nhttps://www.python.org/downloads/\n\n"
                "✅ Make sure to check 'Add Python to PATH'\n"
                "Then run TrafficForge.exe again.")
            return
        self.btn.config(state="disabled", text="  ⏳  Installing…  ")
        threading.Thread(target=self.install, daemon=True).start()

    def update(self, msg, pct):
        self.status.config(text=msg)
        self.progress["value"] = pct
        self.root.update()

    def run_cmd(self, cmd):
        """Run command with hidden window."""
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )

    def install(self):
        try:
            pip = [PYTHON, "-m", "pip", "install",
                   "--quiet", "--disable-pip-version-check"]

            # Step 1 — PyQt5
            self.update("Installing PyQt5…  (1/4)", 10)
            r = self.run_cmd(pip + ["PyQt5"])
            if r.returncode != 0:
                raise Exception(f"PyQt5 failed:\n{r.stderr}")
            self.update("✅ PyQt5 installed", 28)

            # Step 2 — Playwright
            self.update("Installing Playwright…  (2/4)", 32)
            r = self.run_cmd(pip + ["playwright"])
            if r.returncode != 0:
                raise Exception(f"Playwright failed:\n{r.stderr}")
            self.update("✅ Playwright installed", 50)

            # Step 3 — PySocks + requests
            self.update("Installing PySocks & Requests…  (3/4)", 54)
            r = self.run_cmd(pip + ["PySocks", "requests"])
            if r.returncode != 0:
                raise Exception(f"PySocks failed:\n{r.stderr}")
            self.update("✅ PySocks installed", 64)

            # Step 4 — Chromium
            self.update("Downloading Chromium browser…  (4/4)\n(~300MB, please wait 2-3 minutes)", 68)
            r = self.run_cmd([PYTHON, "-m", "playwright", "install", "chromium"])
            if r.returncode != 0:
                raise Exception(f"Chromium failed:\n{r.stderr}")
            self.update("✅ Everything installed!", 96)

            self.update("🚀 Launching TrafficForge…", 100)
            self.root.after(800, self.launch)

        except Exception as e:
            messagebox.showerror(
                "Install Failed",
                f"Error:\n{str(e)}\n\nTry:\n"
                "1. Right-click TrafficForge.exe\n"
                "2. Run as Administrator")
            self.btn.config(state="normal",
                            text="  ▶  Retry Install  ")
            self.update("Installation failed — see error", 0)

    def launch(self):
        self.root.destroy()
        launch_main()


def is_installed(pkg):
    if not PYTHON: return False
    r = subprocess.run(
        [PYTHON, "-c", f"import {pkg}"],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    )
    return r.returncode == 0


def find_main():
    """Find main.py next to exe."""
    # Folder of the exe
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(exe_dir, 'main.py')
    if os.path.exists(path):
        return path
    return None


def launch_main():
    main_path = find_main()
    if not main_path:
        messagebox.showerror(
            "main.py Not Found",
            "Please place main.py in the same folder as TrafficForge.exe")
        return
    if not PYTHON:
        messagebox.showerror("Python Not Found",
                             "Python not found. Install from python.org")
        return
    subprocess.Popen([PYTHON, main_path])


def all_installed():
    pkgs = {"PyQt5": "PyQt5", "playwright": "playwright",
            "socks": "socks", "requests": "requests"}
    for imp in pkgs.values():
        if not is_installed(imp):
            return False
    return True


def main():
    if not PYTHON:
        # Show install window (it will tell user to install Python)
        InstallerWindow()
        return

    if all_installed():
        launch_main()
    else:
        InstallerWindow()


if __name__ == "__main__":
    main()
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0 - Setup")
        self.root.geometry("480x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        # Title
        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(30,4))

        tk.Label(self.root, text="Traffic Generation Suite",
                 font=("Segoe UI", 10),
                 bg="#0d0d1a", fg="#4b5563").pack(pady=(0,20))

        # Status label
        self.status = tk.Label(self.root,
                               text="Click Install to set up TrafficForge",
                               font=("Segoe UI", 10),
                               bg="#0d0d1a", fg="#9ca3af")
        self.status.pack(pady=6)

        # Progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("purple.Horizontal.TProgressbar",
                        background="#7c3aed",
                        troughcolor="#1e1e4a",
                        bordercolor="#1e1e4a",
                        lightcolor="#7c3aed",
                        darkcolor="#7c3aed")
        self.progress = ttk.Progressbar(self.root,
                                        style="purple.Horizontal.TProgressbar",
                                        length=380, mode="determinate")
        self.progress.pack(pady=14)

        # Install button
        self.btn = tk.Button(self.root,
                             text="  ▶  Install & Launch  ",
                             font=("Segoe UI", 12, "bold"),
                             bg="#7c3aed", fg="white",
                             activebackground="#a855f7",
                             activeforeground="white",
                             relief="flat", cursor="hand2",
                             padx=20, pady=10,
                             command=self.start_install)
        self.btn.pack(pady=10)

        # Footer
        tk.Label(self.root,
                 text="Installs: PyQt5 · Playwright · PySocks · Chromium",
                 font=("Segoe UI", 8),
                 bg="#0d0d1a", fg="#374151").pack(side="bottom", pady=10)

        self.root.mainloop()

    def start_install(self):
        self.btn.config(state="disabled", text="  ⏳  Installing…  ")
        thread = threading.Thread(target=self.install, daemon=True)
        thread.start()

    def update(self, msg, pct):
        self.status.config(text=msg)
        self.progress["value"] = pct
        self.root.update()

    def install(self):
        try:
            pip = [sys.executable, "-m", "pip", "install",
                   "--quiet", "--disable-pip-version-check"]

            # Step 1 — PyQt5
            self.update("Installing PyQt5…", 10)
            subprocess.run(pip + ["PyQt5"], check=True,
                           capture_output=True)
            self.update("✅ PyQt5 installed", 30)

            # Step 2 — Playwright
            self.update("Installing Playwright…", 35)
            subprocess.run(pip + ["playwright"], check=True,
                           capture_output=True)
            self.update("✅ Playwright installed", 55)

            # Step 3 — PySocks + requests
            self.update("Installing PySocks & Requests…", 58)
            subprocess.run(pip + ["PySocks", "requests"], check=True,
                           capture_output=True)
            self.update("✅ PySocks installed", 65)

            # Step 4 — Chromium browser
            self.update("Downloading Chromium browser (~300MB)…", 68)
            subprocess.run([sys.executable, "-m", "playwright",
                            "install", "chromium"],
                           check=True, capture_output=True)
            self.update("✅ Chromium downloaded!", 95)

            # Done
            self.update("✅ All done! Launching TrafficForge…", 100)
            self.root.after(800, self.launch)

        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Install Failed",
                f"Installation error:\n{e}\n\nTry running as Administrator.")
            self.btn.config(state="normal", text="  ▶  Retry Install  ")

    def launch(self):
        self.root.destroy()
        launch_main()


def is_installed(pkg):
    """Check if a package is already installed."""
    try:
        __import__(pkg)
        return True
    except ImportError:
        return False


def check_chromium():
    """Check if playwright chromium is already downloaded."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run"],
            capture_output=True, text=True, timeout=5)
        return "chromium" not in result.stdout.lower()
    except Exception:
        return False


def launch_main():
    """Launch the main TrafficForge application."""
    # Find main.py next to this exe/script
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    main_path = os.path.join(base, 'main.py')

    if not os.path.exists(main_path):
        # Try same folder as exe
        exe_dir = os.path.dirname(sys.executable)
        main_path = os.path.join(exe_dir, 'main.py')

    if not os.path.exists(main_path):
        messagebox.showerror("Error",
                             "main.py not found!\nPlace main.py in same folder as this exe.")
        return

    subprocess.Popen([sys.executable, main_path])


def all_deps_installed():
    """Check if all required deps are already installed."""
    checks = {
        "PyQt5":     "PyQt5",
        "playwright": "playwright",
        "PySocks":   "socks",
        "requests":  "requests",
    }
    for name, imp in checks.items():
        if not is_installed(imp):
            return False, name
    return True, None


def main():
    installed, missing = all_deps_installed()

    if installed:
        # Already installed — just launch
        launch_main()
    else:
        # Show installer window
        InstallerWindow()


if __name__ == "__main__":
    main()
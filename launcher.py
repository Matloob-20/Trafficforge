"""
TrafficForge v4.0 - Self Contained Launcher
main.py is embedded inside this exe — no external files needed.
Only Chromium downloads on first run.
"""
import sys
import os
import subprocess
import threading
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

# ── main.py is embedded as a string inside the exe ────
# This gets replaced at build time by GitHub Actions
MAIN_PY_CODE = "__MAIN_PY_PLACEHOLDER__"


def get_install_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_python():
    """Find bundled portable Python."""
    install_dir = get_install_dir()
    candidates = [
        os.path.join(install_dir, "python.exe"),
        os.path.join(install_dir, "python", "python.exe"),
        os.path.join(install_dir, "runtime", "python.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def extract_main() -> str:
    """Extract embedded main.py to a temp file, return path."""
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.py',
        prefix='trafficforge_',
        delete=False,
        encoding='utf-8')
    tmp.write(MAIN_PY_CODE)
    tmp.close()
    return tmp.name


def chromium_installed() -> bool:
    try:
        cache = os.path.expanduser(
            os.path.join("~", "AppData", "Local", "ms-playwright"))
        if not os.path.exists(cache):
            return False
        for d in os.listdir(cache):
            if "chromium" in d.lower():
                for root, dirs, files in os.walk(os.path.join(cache, d)):
                    for f in files:
                        if f.lower() in ("chrome.exe",
                                         "chrome-headless-shell.exe"):
                            return True
        return False
    except Exception:
        return False


class InstallerWindow:
    def __init__(self, python_path):
        self.python = python_path
        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0 - Setup")
        self.root.geometry("500x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(28, 4))

        tk.Label(self.root,
                 text="One-time setup: Download Chromium browser",
                 font=("Segoe UI", 11),
                 bg="#0d0d1a", fg="#6b7280").pack(pady=(0, 12))

        self.status = tk.Label(
            self.root,
            text="Chromium is required to simulate browser visits.\n"
                 "Download is ~300MB and happens once only.",
            font=("Segoe UI", 10),
            bg="#0d0d1a", fg="#9ca3af",
            wraplength=440, justify="center")
        self.status.pack(pady=6)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("purple.Horizontal.TProgressbar",
                        background="#7c3aed", troughcolor="#1e1e4a",
                        bordercolor="#1e1e4a", lightcolor="#7c3aed",
                        darkcolor="#7c3aed")
        self.progress = ttk.Progressbar(
            self.root, style="purple.Horizontal.TProgressbar",
            length=420, mode="indeterminate")
        self.progress.pack(pady=14)

        self.btn = tk.Button(
            self.root,
            text="  ▶  Download & Launch TrafficForge  ",
            font=("Segoe UI", 11, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#a855f7", activeforeground="white",
            relief="flat", cursor="hand2",
            padx=16, pady=10,
            command=self.start)
        self.btn.pack(pady=8)

        tk.Label(self.root,
                 text="All packages bundled — no Python installation needed",
                 font=("Segoe UI", 8),
                 bg="#0d0d1a", fg="#374151").pack(side="bottom", pady=10)

        self.root.mainloop()

    def start(self):
        self.btn.config(state="disabled", text="  ⏳  Downloading…  ")
        self.progress.start(8)
        threading.Thread(target=self._download, daemon=True).start()

    def _update(self, msg):
        self.status.config(text=msg)
        self.root.update_idletasks()

    def _download(self):
        try:
            self._update("Downloading Chromium browser…\nPlease wait 2-3 minutes")
            r = subprocess.run(
                [self.python, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True,
                creationflags=NO_WINDOW, timeout=600)
            if r.returncode != 0:
                raise Exception(r.stderr[-400:] or r.stdout[-400:])
            self._update("✅ Done! Launching TrafficForge…")
            self.progress.stop()
            self.root.after(900, self._launch)
        except subprocess.TimeoutExpired:
            self.progress.stop()
            messagebox.showerror("Timeout",
                                 "Download timed out.\nCheck your internet and retry.")
            self._reset()
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Setup Failed", str(e))
            self._reset()

    def _reset(self):
        self.btn.config(state="normal", text="  ▶  Retry Download  ")
        self._update("Failed — click Retry.")

    def _launch(self):
        self.root.destroy()
        _launch(self.python)


def _launch(python):
    main_path = extract_main()
    subprocess.Popen([python, main_path], creationflags=NO_WINDOW)


def main():
    python = find_python()
    if not python:
        messagebox.showerror(
            "Installation Error",
            "Bundled Python not found.\nPlease reinstall TrafficForge.")
        return
    if chromium_installed():
        _launch(python)
    else:
        InstallerWindow(python)


if __name__ == "__main__":
    main()
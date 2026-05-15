"""
TrafficForge v4.0 - Launcher
Python is bundled inside this exe.
Only Chromium browser needs to be downloaded on first run (~300MB).
"""
import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

PYTHON = sys.executable
NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0


def find_main():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(exe_dir, 'main.py')
    return path if os.path.exists(path) else None


def chromium_installed() -> bool:
    try:
        cache = os.path.expanduser(r"~\AppData\Local\ms-playwright")
        if os.path.exists(cache):
            for d in os.listdir(cache):
                if "chromium" in d.lower():
                    chrome_path = os.path.join(cache, d)
                    for root, dirs, files in os.walk(chrome_path):
                        for f in files:
                            if "chrome" in f.lower() and f.endswith(".exe"):
                                return True
        return False
    except Exception:
        return False


class InstallerWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0")
        self.root.geometry("500x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(28, 4))

        tk.Label(self.root, text="First-time setup: downloading Chromium browser",
                 font=("Segoe UI", 10),
                 bg="#0d0d1a", fg="#4b5563").pack(pady=(0, 16))

        self.status = tk.Label(
            self.root,
            text="Click below to download Chromium (~300MB)\nThis is required once only.",
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
            length=400, mode="indeterminate")
        self.progress.pack(pady=14)

        self.btn = tk.Button(
            self.root,
            text="  ▶  Download Chromium & Launch  ",
            font=("Segoe UI", 12, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#a855f7", activeforeground="white",
            relief="flat", cursor="hand2",
            padx=20, pady=10,
            command=self.start_install)
        self.btn.pack(pady=8)

        tk.Label(self.root,
                 text="Python & all packages are already included — no extra installation needed!",
                 font=("Segoe UI", 8),
                 bg="#0d0d1a", fg="#374151").pack(side="bottom", pady=10)

        self.root.mainloop()

    def start_install(self):
        self.btn.config(state="disabled", text="  ⏳  Downloading…  ")
        self.progress.start(10)
        threading.Thread(target=self.install, daemon=True).start()

    def update(self, msg):
        self.status.config(text=msg)
        self.root.update()

    def install(self):
        try:
            self.update("Downloading Chromium browser…\nPlease wait 2-3 minutes")
            r = subprocess.run(
                [PYTHON, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True, creationflags=NO_WINDOW)
            if r.returncode != 0:
                raise Exception(f"Download failed:\n{r.stderr[:300]}")
            self.update("✅ Done! Launching TrafficForge…")
            self.progress.stop()
            self.root.after(800, self.launch)
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Setup Failed",
                                 f"{str(e)}\n\nTry running as Administrator.")
            self.btn.config(state="normal", text="  ▶  Retry Download  ")
            self.update("Failed — see error above.")

    def launch(self):
        self.root.destroy()
        launch_main()


def launch_main():
    main_path = find_main()
    if not main_path:
        messagebox.showerror("main.py Not Found",
                             f"Place main.py in same folder as TrafficForge.exe\n"
                             f"Folder: {os.path.dirname(sys.executable)}")
        return
    subprocess.Popen([PYTHON, main_path], creationflags=NO_WINDOW)


def main():
    if chromium_installed():
        launch_main()
    else:
        InstallerWindow()


if __name__ == "__main__":
    main()
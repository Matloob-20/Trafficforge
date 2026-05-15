"""
TrafficForge v4.0 - Self Contained Launcher
main.py is embedded inside this exe.
Only Chromium downloads on first run (~300MB).
"""
import sys, os, subprocess, threading, tempfile, tkinter as tk
from tkinter import ttk, messagebox

NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

# Injected at build time by GitHub Actions
MAIN_PY_CODE = "__MAIN_PY_PLACEHOLDER__"


def get_install_dir():
    """Folder where TrafficForge.exe lives."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_python():
    """Find bundled portable python.exe in install dir."""
    d = get_install_dir()
    for p in [
        os.path.join(d, "python.exe"),
        os.path.join(d, "python", "python.exe"),
        os.path.join(d, "runtime", "python.exe"),
    ]:
        if os.path.exists(p):
            return p
    return None


def get_env(python_path):
    """Build environment with correct paths for portable Python."""
    env = os.environ.copy()
    python_dir = os.path.dirname(python_path)

    # Set PLAYWRIGHT_BROWSERS_PATH to user's AppData so Chromium
    # is downloaded/found in standard location across all runs
    browsers_path = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "TrafficForge", "browsers")
    os.makedirs(browsers_path, exist_ok=True)
    env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

    # Make sure portable Python libs are on PATH
    env["PATH"] = python_dir + os.pathsep + env.get("PATH", "")

    # Remove any conflicting PYTHONPATH/PYTHONHOME that might confuse portable Python
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)

    return env, browsers_path


def chromium_installed(browsers_path) -> bool:
    """Check if Chromium is downloaded in our browsers folder."""
    try:
        if not os.path.exists(browsers_path):
            return False
        for d in os.listdir(browsers_path):
            if "chromium" in d.lower():
                for root, dirs, files in os.walk(os.path.join(browsers_path, d)):
                    for f in files:
                        if f.lower() in ("chrome.exe", "chrome-headless-shell.exe"):
                            return True
        return False
    except Exception:
        return False


def extract_main() -> str:
    """Write embedded main.py to temp file and return path."""
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', prefix='tf_',
        delete=False, encoding='utf-8')
    tmp.write(MAIN_PY_CODE)
    tmp.close()
    return tmp.name


class InstallerWindow:
    def __init__(self, python_path, env, browsers_path):
        self.python = python_path
        self.env = env
        self.browsers_path = browsers_path

        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0 - Setup")
        self.root.geometry("500x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(28, 4))

        tk.Label(self.root, text="First-time setup: Download Chromium browser",
                 font=("Segoe UI", 11), bg="#0d0d1a", fg="#6b7280").pack(pady=(0, 12))

        self.status = tk.Label(
            self.root,
            text="Chromium is required to simulate browser visits.\n"
                 "~300MB download — happens once only.",
            font=("Segoe UI", 10), bg="#0d0d1a", fg="#9ca3af",
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
            relief="flat", cursor="hand2", padx=16, pady=10,
            command=self.start)
        self.btn.pack(pady=8)

        tk.Label(self.root,
                 text="✅ Python & all packages already bundled — no extra installs needed",
                 font=("Segoe UI", 8), bg="#0d0d1a", fg="#374151"
                 ).pack(side="bottom", pady=10)

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
            self._update("Contacting server…\nPlease wait 2-3 minutes")
            r = subprocess.run(
                [self.python, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True,
                env=self.env, creationflags=NO_WINDOW, timeout=600)
            if r.returncode != 0:
                err = (r.stderr or r.stdout or "Unknown error")[-500:]
                raise Exception(f"Download failed:\n{err}")
            self._update("✅ Chromium ready!\nLaunching TrafficForge…")
            self.progress.stop()
            self.root.after(900, self._launch)
        except subprocess.TimeoutExpired:
            self.progress.stop()
            messagebox.showerror("Timeout",
                                 "Download timed out.\nCheck internet connection and retry.")
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
        _launch(self.python, self.env)


def _launch(python, env):
    """Extract and run main.py with correct environment."""
    main_path = extract_main()
    subprocess.Popen([python, main_path], env=env, creationflags=NO_WINDOW)


def main():
    python = find_python()
    if not python:
        messagebox.showerror(
            "Installation Error",
            "Bundled Python not found in installation folder.\n"
            "Please reinstall TrafficForge using TrafficForge_Setup.exe")
        return

    env, browsers_path = get_env(python)

    if chromium_installed(browsers_path):
        _launch(python, env)
    else:
        InstallerWindow(python, env, browsers_path)


if __name__ == "__main__":
    main()
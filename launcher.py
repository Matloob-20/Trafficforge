"""
TrafficForge v4.0 - Launcher
main.py embedded as base64 — no escaping issues.
"""
import sys, os, subprocess, threading, tempfile, base64, tkinter as tk
from tkinter import ttk, messagebox

NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

# main.py embedded as base64 — injected by GitHub Actions
MAIN_PY_B64 = "__MAIN_PY_B64_PLACEHOLDER__"


def get_install_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_python():
    d = get_install_dir()
    for p in [
        os.path.join(d, "python.exe"),
        os.path.join(d, "python", "python.exe"),
    ]:
        if os.path.exists(p):
            return p
    return None


def get_env(python_path):
    env = os.environ.copy()
    python_dir = os.path.dirname(python_path)
    scripts_dir = os.path.join(python_dir, "Scripts")
    env["PATH"] = python_dir + os.pathsep + scripts_dir + os.pathsep + env.get("PATH", "")
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    return env


def chromium_installed() -> bool:
    try:
        path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
        if not os.path.exists(path):
            return False
        for d in os.listdir(path):
            if "chromium" in d.lower():
                for root, dirs, files in os.walk(os.path.join(path, d)):
                    for f in files:
                        if f.lower() in ("chrome.exe", "chrome-headless-shell.exe"):
                            return True
        return False
    except Exception:
        return False


def extract_main() -> str:
    """Decode base64 embedded main.py and write to temp file."""
    code = base64.b64decode(MAIN_PY_B64).decode('utf-8')
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', prefix='tf_',
        delete=False, encoding='utf-8')
    tmp.write(code)
    tmp.close()
    return tmp.name


class InstallerWindow:
    def __init__(self, python_path, env):
        self.python = python_path
        self.env = env
        self.root = tk.Tk()
        self.root.title("TrafficForge v4.0 - Setup")
        self.root.geometry("500x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d1a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="⚡ TrafficForge v4.0",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0d0d1a", fg="#a855f7").pack(pady=(28, 4))

        tk.Label(self.root, text="First-time setup: Downloading Chromium browser",
                 font=("Segoe UI", 11), bg="#0d0d1a", fg="#6b7280").pack(pady=(0, 12))

        self.status = tk.Label(self.root,
                               text="Chromium is required to simulate browser visits.\n~300MB — happens once only.",
                               font=("Segoe UI", 10), bg="#0d0d1a", fg="#9ca3af",
                               wraplength=440, justify="center")
        self.status.pack(pady=6)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("purple.Horizontal.TProgressbar",
                        background="#7c3aed", troughcolor="#1e1e4a",
                        bordercolor="#1e1e4a", lightcolor="#7c3aed",
                        darkcolor="#7c3aed")
        self.progress = ttk.Progressbar(self.root,
                                        style="purple.Horizontal.TProgressbar",
                                        length=420, mode="indeterminate")
        self.progress.pack(pady=14)

        self.btn = tk.Button(self.root,
                             text="  ▶  Download & Launch TrafficForge  ",
                             font=("Segoe UI", 11, "bold"),
                             bg="#7c3aed", fg="white",
                             activebackground="#a855f7", activeforeground="white",
                             relief="flat", cursor="hand2", padx=16, pady=10,
                             command=self.start)
        self.btn.pack(pady=8)

        tk.Label(self.root,
                 text="All packages bundled — no Python installation needed",
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
            self._update("Downloading Chromium…\nPlease wait 2-3 minutes")
            r = subprocess.run(
                [self.python, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True,
                env=self.env, creationflags=NO_WINDOW, timeout=600)
            if r.returncode != 0:
                raise Exception((r.stderr or r.stdout or "Unknown")[-400:])
            self._update("✅ Done! Launching TrafficForge…")
            self.progress.stop()
            self.root.after(900, self._launch)
        except subprocess.TimeoutExpired:
            self.progress.stop()
            messagebox.showerror("Timeout", "Download timed out. Check internet and retry.")
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
    main_path = extract_main()
    subprocess.Popen([python, main_path], env=env, creationflags=NO_WINDOW)


def main():
    python = find_python()
    if not python:
        messagebox.showerror("Error",
                             "Bundled Python not found.\nReinstall TrafficForge.")
        return
    env = get_env(python)
    if chromium_installed():
        _launch(python, env)
    else:
        InstallerWindow(python, env)


if __name__ == "__main__":
    main()
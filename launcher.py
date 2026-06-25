"""
TrafficForge launcher — tiny bootstrap EXE.

Responsibilities:
  1. Decode the embedded base64 copy of New_traffic.py to disk.
  2. Set PLAYWRIGHT_BROWSERS_PATH to the bundled ms-playwright folder
     next to the EXE (so we do NOT depend on a registry env var).
  3. Hand off execution to portable_python\\pythonw.exe.

The placeholder MAIN_PY_B64 is replaced at build time by the GitHub
Actions workflow.
"""
import sys, os, base64, subprocess, tempfile, ctypes

MAIN_PY_B64 = "__MAIN_PY_B64_PLACEHOLDER__"


def _msgbox(title, text):
    """Pop a Windows message box so users see fatal errors when the
    console is hidden (windowed EXE)."""
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
    except Exception:
        print(f"[{title}] {text}")


def _exe_dir():
    """Folder containing the running EXE (or this script in dev mode)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _find_portable_python(base):
    """Locate pythonw.exe inside the bundled portable_python folder."""
    for name in ("pythonw.exe", "python.exe"):
        cand = os.path.join(base, "portable_python", name)
        if os.path.isfile(cand):
            return cand
    return None


def _find_bundled_browsers(base):
    """Return the absolute ms-playwright folder path if it exists."""
    cand = os.path.join(base, "ms-playwright")
    return cand if os.path.isdir(cand) else None


def main():
    base = _exe_dir()

    # 1. Decode embedded New_traffic.py
    try:
        script_bytes = base64.b64decode(MAIN_PY_B64)
    except Exception as exc:
        _msgbox("TrafficForge", f"Failed to decode embedded script:\n{exc}")
        sys.exit(1)

    # Write to a stable per-user location so the file path stays the
    # same across runs (helps Windows Defender / SmartScreen heuristics).
    work_dir = os.path.join(tempfile.gettempdir(), "TrafficForge")
    os.makedirs(work_dir, exist_ok=True)
    script_path = os.path.join(work_dir, "New_traffic.py")
    try:
        with open(script_path, "wb") as f:
            f.write(script_bytes)
    except Exception as exc:
        _msgbox("TrafficForge", f"Cannot write script to disk:\n{exc}")
        sys.exit(1)

    # 2. Locate bundled Python + Chromium
    py = _find_portable_python(base)
    if not py:
        _msgbox("TrafficForge",
                f"Portable Python not found in:\n{base}\\portable_python\n\n"
                "The installation appears corrupted. Please reinstall.")
        sys.exit(1)

    env = os.environ.copy()
    browsers = _find_bundled_browsers(base)
    if browsers:
        env["PLAYWRIGHT_BROWSERS_PATH"] = browsers
    # Make portable Python self-contained (ignore user site-packages)
    env["PYTHONNOUSERSITE"] = "1"

    # 3. Launch the real app
    try:
        # CREATE_NO_WINDOW so no console pops behind the Qt window
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(
            [py, script_path],
            env=env,
            cwd=work_dir,
            creationflags=CREATE_NO_WINDOW,
            close_fds=True,
        )
    except Exception as exc:
        _msgbox("TrafficForge", f"Failed to launch app:\n{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
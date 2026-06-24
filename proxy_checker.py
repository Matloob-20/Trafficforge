#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   Proxy Checker  —  Test SOCKS5 proxies & save working ones ║
║   Reads:  proxies.txt  (same folder as this script)         ║
║   Saves:  running.txt  (same folder as this script)         ║
╚══════════════════════════════════════════════════════════════╝

USAGE:
    python3 proxy_checker.py              ← uses proxies.txt automatically
    python3 proxy_checker.py --threads 50
    python3 proxy_checker.py --timeout 10
    python3 proxy_checker.py --url https://httpbin.org/ip

pip install PySocks requests
"""

import sys, os, socket, struct, time, argparse, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# ── Same-directory paths ──────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IN   = os.path.join(SCRIPT_DIR, "running.txt")
DEFAULT_OUT  = os.path.join(SCRIPT_DIR, "today.txt")

# ─── Terminal colors ──────────────────────────────────────
class C:
    RESET  = "\033[0m";  BOLD  = "\033[1m"
    GREEN  = "\033[92m"; RED   = "\033[91m"
    YELLOW = "\033[93m"; CYAN  = "\033[96m"
    GREY   = "\033[90m"; WHITE = "\033[97m"
    PURP   = "\033[95m"

# ─── Thread-safe counter ──────────────────────────────────
class Counter:
    def __init__(self):
        self._lock   = threading.Lock()
        self.total   = self.ok = self.fail = self.checked = 0
    def inc_ok(self):
        with self._lock: self.ok += 1; self.checked += 1
    def inc_fail(self):
        with self._lock: self.fail += 1; self.checked += 1

CTR        = Counter()
PRINT_LOCK = threading.Lock()

def progress_line(proxy_short, status, speed_ms, col):
    done = CTR.checked; total = CTR.total
    pct  = int(done / total * 100) if total else 0
    bar  = "█" * (pct // 5) + "░" * (20 - pct // 5)
    with PRINT_LOCK:
        print(
            f"\r{C.GREY}[{done:>4}/{total}] [{bar}] {pct:>3}%  "
            f"{col}{status:<5}{C.RESET}  "
            f"{C.CYAN}{proxy_short:<38}{C.RESET}  "
            f"{C.GREY}{speed_ms:>5}ms{C.RESET}",
            end="", flush=True)

# ═══════════════════════════════════════════════════════════
#  PROXY PARSER  — all formats supported
# ═══════════════════════════════════════════════════════════
def parse_proxy(raw: str) -> Optional[dict]:
    raw = raw.strip()
    if not raw or raw.startswith("#"): return None
    # Strip inline comments  e.g.  proxy:line  # 943ms
    if "  #" in raw: raw = raw[:raw.index("  #")].strip()
    if "://" in raw:
        scheme, rest = raw.split("://", 1)
        user = pwd = None
        if "@" in rest:
            creds, rest = rest.rsplit("@", 1)
            user, pwd = creds.split(":", 1) if ":" in creds else (creds, None)
        if ":" not in rest: return None
        host, port_s = rest.rsplit(":", 1)
        try: return {"scheme": scheme, "host": host, "port": int(port_s),
                     "user": user or "", "pass": pwd or ""}
        except ValueError: return None
    if "@" in raw:
        creds, rest = raw.rsplit("@", 1)
        user, pwd   = creds.split(":", 1) if ":" in creds else (creds, "")
        host, port_s = rest.rsplit(":", 1)
        try: return {"scheme": "socks5", "host": host, "port": int(port_s),
                     "user": user, "pass": pwd}
        except ValueError: return None
    parts = raw.split(":")
    if len(parts) == 4:
        a, b, c, d = parts
        try: return {"scheme":"socks5","host":a,"port":int(b),"user":c,"pass":d}
        except ValueError: pass
        try: return {"scheme":"socks5","host":c,"port":int(d),"user":a,"pass":b}
        except ValueError: return None
    if len(parts) == 2:
        try: return {"scheme":"socks5","host":parts[0],"port":int(parts[1]),
                     "user":"","pass":""}
        except ValueError: return None
    return None

def display_proxy(info: dict) -> str:
    auth = f"{info['user']}:***@" if info["user"] else ""
    return f"{info['scheme']}://{auth}{info['host']}:{info['port']}"

# ═══════════════════════════════════════════════════════════
#  TEST — Raw TCP SOCKS5 handshake (fast, no extra deps)
# ═══════════════════════════════════════════════════════════
def test_socks5_raw(info: dict, timeout: float):
    t0 = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((info["host"], info["port"]))
        has_auth = bool(info.get("user"))
        methods  = b"\x02" if has_auth else b"\x00"
        s.sendall(b"\x05\x01" + methods)
        resp = s.recv(2)
        if len(resp) < 2 or resp[0] != 5:
            s.close(); return False, int((time.time()-t0)*1000)
        if resp[1] == 0xff:
            s.close(); return False, int((time.time()-t0)*1000)
        if resp[1] == 2 and has_auth:
            user = info["user"].encode(); pwd = info["pass"].encode()
            s.sendall(bytes([1,len(user)]) + user + bytes([len(pwd)]) + pwd)
            ar = s.recv(2)
            if len(ar) < 2 or ar[1] != 0:
                s.close(); return False, int((time.time()-t0)*1000)
        target = b"google.com"
        req = b"\x05\x01\x00\x03" + bytes([len(target)]) + target + struct.pack("!H", 80)
        s.sendall(req)
        cr = s.recv(10); s.close()
        if len(cr) >= 2 and cr[0] == 5 and cr[1] == 0:
            return True, int((time.time()-t0)*1000)
        return False, int((time.time()-t0)*1000)
    except Exception:
        return False, int((time.time()-t0)*1000)

# ═══════════════════════════════════════════════════════════
#  TEST — PySocks + real HTTP (accurate, needs requests)
# ═══════════════════════════════════════════════════════════
def test_via_requests(info: dict, timeout: float, check_url: str):
    t0 = time.time()
    try:
        import requests
        auth = f"{info['user']}:{info['pass']}@" if info.get("user") else ""
        px_url = f"socks5h://{auth}{info['host']}:{info['port']}"
        proxies = {"http": px_url, "https": px_url}
        r  = requests.get(check_url, proxies=proxies, timeout=timeout)
        ms = int((time.time()-t0)*1000)
        ip = ""
        if "httpbin" in check_url or "icanhazip" in check_url:
            try: ip = r.json().get("origin","") or r.text.strip()
            except Exception: ip = r.text.strip()[:20]
        return r.status_code < 400, ms, ip
    except Exception:
        return False, int((time.time()-t0)*1000), ""

# ═══════════════════════════════════════════════════════════
#  WORKER
# ═══════════════════════════════════════════════════════════
def check_proxy(raw: str, timeout: float, check_url: str, use_http: bool) -> dict:
    info = parse_proxy(raw)
    if not info:
        CTR.inc_fail()
        return {"raw": raw, "alive": False, "ms": 0, "ip": "", "reason": "parse_error"}
    short = display_proxy(info)
    if use_http:
        alive, ms, ip = test_via_requests(info, timeout, check_url)
    else:
        alive, ms = test_socks5_raw(info, timeout)
        ip = ""
    reason = "ok" if alive else ("timeout" if ms >= int(timeout*1000)-100 else "refused")
    if alive:
        CTR.inc_ok()
        progress_line(short, "LIVE ", ms, C.GREEN)
    else:
        CTR.inc_fail()
        progress_line(short, "DEAD ", ms, C.RED)
    return {"raw": raw, "info": info, "alive": alive,
            "ms": ms, "ip": ip, "short": short, "reason": reason}

# ═══════════════════════════════════════════════════════════
#  LOAD INPUT — strips inline comments from running.txt lines
# ═══════════════════════════════════════════════════════════
def load_proxies(path: str) -> list:
    if not os.path.exists(path):
        print(f"\n{C.RED}  ✗ File not found: {path}{C.RESET}")
        print(f"  Create a file named {C.CYAN}proxies.txt{C.RESET} in the same folder as this script.")
        print(f"  Put one proxy per line.\n")
        sys.exit(1)
    lines = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            # strip inline comment
            if "  #" in line: line = line[:line.index("  #")].strip()
            if line: lines.append(line)
    return lines

# ═══════════════════════════════════════════════════════════
#  LOAD EXISTING running.txt — to avoid duplicates
# ═══════════════════════════════════════════════════════════
def load_existing(path: str) -> set:
    if not os.path.exists(path): return set()
    existing = set()
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "  #" in line: line = line[:line.index("  #")].strip()
            if line: existing.add(line)
    return existing

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Proxy Checker — reads proxies.txt, appends working ones to running.txt")
    parser.add_argument("--threads", type=int,   default=30,  help="Threads (default: 30)")
    parser.add_argument("--timeout", type=float, default=10, help="Timeout per proxy in seconds (default: 8)")
    parser.add_argument("--url",     default="",              help="HTTP check URL — e.g. https://httpbin.org/ip")
    parser.add_argument("--fast",    action="store_true",     help="Fast raw TCP mode only")
    parser.add_argument("--input",   default=DEFAULT_IN,      help=f"Input file (default: proxies.txt in script folder)")
    parser.add_argument("--output",  default=DEFAULT_OUT,     help=f"Output file (default: running.txt in script folder)")
    args = parser.parse_args()

    use_http = bool(args.url) and not args.fast
    if use_http:
        try: import requests, socks
        except ImportError:
            print(f"{C.YELLOW}  pip install requests PySocks required for --url mode → using fast TCP{C.RESET}")
            use_http = False

    check_url = args.url or "https://httpbin.org/ip"
    proxies   = load_proxies(args.input)
    existing  = load_existing(args.output)

    CTR.total = len(proxies)

    # ── Header ──────────────────────────────────────────
    print(f"\n{C.PURP}{C.BOLD}{'═'*64}{C.RESET}")
    print(f"{C.PURP}{C.BOLD}  ⚡ Proxy Checker{C.RESET}")
    print(f"{C.PURP}{'─'*64}{C.RESET}")
    print(f"  Input    : {C.CYAN}{args.input}{C.RESET}  ({len(proxies)} proxies)")
    print(f"  Output   : {C.CYAN}{args.output}{C.RESET}  ({len(existing)} already saved)")
    print(f"  Threads  : {args.threads}  ·  Timeout: {args.timeout}s")
    print(f"  Method   : {'HTTP — ' + check_url if use_http else 'Fast raw TCP handshake'}")
    print(f"{C.PURP}{'═'*64}{C.RESET}\n")

    start   = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {pool.submit(check_proxy, raw, args.timeout, check_url, use_http): raw
                   for raw in proxies}
        for future in as_completed(futures):
            try: results.append(future.result())
            except Exception as e:
                results.append({"raw": futures[future], "alive": False,
                                "ms": 0, "ip": "", "reason": str(e)})

    print()  # newline after progress line

    alive   = sorted([r for r in results if r["alive"]], key=lambda r: r["ms"])
    dead    = [r for r in results if not r["alive"]]
    elapsed = time.time() - start

    # ── Append NEW working proxies to running.txt ───────
    new_alive = [r for r in alive if r["raw"] not in existing]

    with open(args.output, "a", encoding="utf-8") as f:
        # if not existing and not new_alive:
        #     File is new but nothing worked — write empty header
        #     f.write(f"# Proxy Checker — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if new_alive:
            # f.write(f"\n# Added {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {len(new_alive)} new working\n")
            for r in new_alive:
                f.write(f"{r['raw']}\n")

    # ── Summary ─────────────────────────────────────────
    print(f"\n{C.PURP}{'─'*64}{C.RESET}")
    print(f"  {C.BOLD}RESULTS{C.RESET}")
    print(f"{'─'*64}")
    print(f"  Total checked  : {len(proxies)}")
    print(f"  {C.GREEN}Working        : {len(alive)}{C.RESET}")
    print(f"  {C.RED}Dead           : {len(dead)}{C.RESET}")
    print(f"  Success rate   : {int(len(alive)/len(proxies)*100) if proxies else 0}%")
    print(f"  Time taken     : {elapsed:.1f}s")
    print(f"  {C.GREEN}New added      : {len(new_alive)}{C.RESET}  (skipped {len(alive)-len(new_alive)} duplicates)")

    if alive:
        speeds = [r["ms"] for r in alive]
        print(f"\n  Fastest: {min(speeds)}ms  ·  Slowest: {max(speeds)}ms  ·  Avg: {int(sum(speeds)/len(speeds))}ms")
        print(f"\n  {C.BOLD}Top 5 fastest:{C.RESET}")
        for r in alive[:5]:
            ip_note = f"  [{r['ip']}]" if r.get("ip") else ""
            print(f"    {C.GREEN}{r['ms']:>5}ms{C.RESET}  {r.get('short', r['raw'])}{C.GREY}{ip_note}{C.RESET}")

    total_saved = len(existing) + len(new_alive)
    print(f"\n  {C.GREEN}✓ running.txt now has {total_saved} working proxies → {args.output}{C.RESET}")
    print(f"{C.PURP}{'═'*64}{C.RESET}\n")


if __name__ == "__main__":
    main()
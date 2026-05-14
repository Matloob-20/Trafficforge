#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║       TrafficForge v4.0  —  Project-Based Traffic Engine    ║
║  Projects · Live Dashboard · Chart · SOCKS Rows · Social   ║
╚══════════════════════════════════════════════════════════════╝
pip install PyQt5 playwright PySocks
playwright install chromium
python trafficforge.py
"""
import sys, os, json, uuid, asyncio, random, time, socket, struct
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from copy import deepcopy

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QFileDialog, QFrame, QStackedWidget, QScrollArea,
    QProgressBar, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QCheckBox, QMessageBox, QGridLayout, QSizePolicy,
    QRadioButton, QButtonGroup, QListWidget, QListWidgetItem, QSplitter
)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QObject, QTimer,
                          QRect, QPoint, QSize, QPointF)
from PyQt5.QtGui import (QFont, QTextCursor, QColor, QPainter, QPen,
                         QBrush, QLinearGradient, QPolygonF, QPainterPath,
                         QPixmap, QIcon)

# ═══════════════════════════════════════════════════════
#  THEME  (TrafficPeak-inspired purple/dark)
# ═══════════════════════════════════════════════════════
BG    = "#0d0d1a"
PAN   = "#12122a"
SURF  = "#17173a"
SUR2  = "#1e1e4a"
BOR   = "#2a2a5a"
BOR2  = "#353570"
PURP  = "#7c3aed"
PRP2  = "#a855f7"
PRPG  = "#7c3aed22"
CYAN  = "#06b6d4"
CYN2  = "#22d3ee"
GRNS  = "#10b981"
GRN2  = "#34d399"
PINK  = "#ec4899"
PKN2  = "#f472b6"
YEL   = "#f59e0b"
RED   = "#ef4444"
RED2  = "#f87171"
ORG   = "#f97316"
TXT   = "#f1f0ff"
TX2   = "#9ca3af"
TX3   = "#4b5563"
HIGH  = "#7c3aed10"
GLOW  = "#7c3aed20"

QSS = f"""
QMainWindow{{background:{BG};}} QDialog{{background:{PAN};}}
QWidget{{background:transparent;color:{TXT};
  font-family:'Segoe UI',Arial,sans-serif;font-size:13px;}}
QToolTip{{background:{SUR2};color:{TXT};border:1px solid {BOR2};
  border-radius:5px;padding:6px;font-size:12px;}}

/* ── SIDEBAR ── */
#sidebar{{background:{PAN};border-right:1px solid {BOR};
  min-width:220px;max-width:220px;}}
#logoWrap{{background:{BG};border-bottom:1px solid {BOR};}}

/* ── NAV ── */
QPushButton#navBtn{{background:transparent;color:{TX2};border:none;
  border-radius:8px;padding:11px 16px;text-align:left;
  font-size:13px;font-weight:500;margin:2px 8px;}}
QPushButton#navBtn:hover{{background:{HIGH};color:{TXT};}}
QPushButton#navBtn[active="true"]{{
  background:{PRPG};color:{PRP2};font-weight:700;
  border:1px solid {PURP}44;}}

/* ── MAIN ── */
#mainArea{{background:{BG};}}

/* ── LABELS ── */
QLabel#pageTitle{{font-size:20px;font-weight:800;color:{TXT};}}
QLabel#pageSub{{font-size:12px;color:{TX3};}}
QLabel#cardTitle{{font-size:12px;font-weight:700;color:{TX2};
  text-transform:uppercase;letter-spacing:1px;}}
QLabel#statBig{{font-size:32px;font-weight:900;}}
QLabel#statSmall{{font-size:11px;color:{TX3};margin-top:2px;}}

/* ── CARDS ── */
#card{{background:{SURF};border:1px solid {BOR};border-radius:12px;padding:20px;}}
#glowCard{{background:{SURF};border:1px solid {PURP}44;border-radius:12px;padding:20px;}}
#visitCard{{background:{SURF};border:1px solid {BOR};border-radius:12px;}}

/* ── TABLE ── */
QTableWidget{{background:transparent;border:none;color:{TXT};
  gridline-color:{BOR};outline:0;}}
QTableWidget::item{{padding:10px 12px;border-bottom:1px solid {BOR};}}
QTableWidget::item:selected{{background:{PRPG};color:{PRP2};}}
QTableWidget::item:hover{{background:{HIGH};}}
QHeaderView{{background:{SURF};}}
QHeaderView::section{{background:{SUR2};color:{TX2};border:none;
  border-bottom:1px solid {BOR};
  padding:10px 12px;font-size:11px;font-weight:700;letter-spacing:0.5px;}}

/* ── LIST (SOCKS rows) ── */
QListWidget{{background:transparent;border:none;outline:0;}}
QListWidget::item{{background:{SUR2};border:1px solid {BOR};
  border-radius:8px;padding:10px;margin:3px 0;color:{TXT};}}
QListWidget::item:hover{{border-color:{PURP}55;}}
QListWidget::item:selected{{background:{PRPG};border-color:{PURP};}}

/* ── FORM ── */
QLineEdit,QTextEdit,QSpinBox,QDoubleSpinBox,QComboBox{{
  background:{SUR2};border:1px solid {BOR2};border-radius:8px;
  color:{TXT};padding:9px 12px;
  selection-background-color:{PRPG};font-size:13px;}}
QLineEdit:focus,QTextEdit:focus,QSpinBox:focus,
QDoubleSpinBox:focus,QComboBox:focus{{border:1px solid {PURP}99;}}
QLineEdit::placeholder,QTextEdit{{color:{TX3};}}
QSpinBox::up-button,QSpinBox::down-button,
QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{
  background:{BOR};border:none;width:20px;border-radius:4px;}}
QComboBox::drop-down{{border:none;background:{BOR};width:28px;
  border-radius:0 8px 8px 0;}}
QComboBox QAbstractItemView{{background:{SURF};border:1px solid {BOR2};
  color:{TXT};selection-background-color:{PRPG};outline:0;}}
QCheckBox{{color:{TX2};spacing:9px;}}
QCheckBox::indicator{{width:17px;height:17px;background:{SUR2};
  border:1px solid {BOR2};border-radius:5px;}}
QCheckBox::indicator:checked{{background:{PURP};border-color:{PURP};}}
QRadioButton{{color:{TX2};spacing:9px;}}
QRadioButton::indicator{{width:17px;height:17px;background:{SUR2};
  border:1px solid {BOR2};border-radius:9px;}}
QRadioButton::indicator:checked{{background:{PURP};border-color:{PURP};}}

/* ── BUTTONS ── */
QPushButton#primaryBtn{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {PURP},stop:1 {PINK});
  color:#fff;border:none;border-radius:10px;
  padding:11px 28px;font-weight:700;font-size:14px;min-height:42px;}}
QPushButton#primaryBtn:hover{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {PRP2},stop:1 {PKN2});}}
QPushButton#primaryBtn:disabled{{background:{BOR};color:{TX3};}}

QPushButton#startBtn{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #059669,stop:1 #10b981);
  color:#fff;border:none;border-radius:10px;
  padding:14px 44px;font-weight:900;font-size:16px;min-height:52px;
  letter-spacing:0.5px;}}
QPushButton#startBtn:hover{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #10b981,stop:1 #34d399);}}
QPushButton#startBtn:disabled{{background:#0a2010;color:#1a4020;}}

QPushButton#stopBtn{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #b91c1c,stop:1 #ef4444);
  color:#fff;border:none;border-radius:10px;
  padding:14px 44px;font-weight:900;font-size:16px;min-height:52px;}}
QPushButton#stopBtn:hover{{
  background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #ef4444,stop:1 #f87171);}}
QPushButton#stopBtn:disabled{{background:#200000;color:#401010;border:none;}}

QPushButton#nextBtn{{
  background:#ffffff;color:#000000;
  border:none;border-radius:10px;
  padding:13px 36px;font-weight:800;font-size:14px;min-height:48px;}}
QPushButton#nextBtn:hover{{background:#e0e0e0;}}
QPushButton#nextBtn:disabled{{background:{BOR};color:{TX3};}}

QPushButton#ghostBtn{{background:transparent;color:{TX2};
  border:1px solid {BOR2};border-radius:8px;padding:8px 16px;font-size:12px;}}
QPushButton#ghostBtn:hover{{background:{SUR2};color:{TXT};border-color:{PURP}44;}}

QPushButton#addBtn{{background:{PRPG};color:{PRP2};
  border:1px solid {PURP}44;border-radius:8px;padding:8px 18px;font-weight:600;}}
QPushButton#addBtn:hover{{background:{PURP}33;border-color:{PURP};}}

QPushButton#removeBtn{{background:{RED}15;color:{RED2};
  border:1px solid {RED}33;border-radius:6px;
  padding:4px 12px;font-size:12px;font-weight:600;}}
QPushButton#removeBtn:hover{{background:{RED}25;border-color:{RED};}}

QPushButton#helpBtn{{background:transparent;color:{TX3};
  border:1px solid {BOR};border-radius:12px;
  padding:2px 8px;font-size:11px;font-weight:700;min-width:24px;max-width:24px;}}
QPushButton#helpBtn:hover{{background:{SUR2};color:{PRP2};border-color:{PURP};}}

QPushButton#srcBtn{{background:{SUR2};color:{TX2};
  border:1px solid {BOR};border-radius:9px;
  padding:10px 16px;font-size:12px;font-weight:600;}}
QPushButton#srcBtn:hover{{border-color:{PURP}55;color:{PRP2};}}
QPushButton#srcBtn[active="true"]{{
  background:{PRPG};color:{PRP2};border:1px solid {PURP};font-weight:700;}}

QPushButton#fbBtn{{background:#1877f218;color:#60a5fa;
  border:1px solid #1877f233;border-radius:9px;padding:9px 14px;font-weight:600;font-size:12px;}}
QPushButton#fbBtn[active="true"]{{background:#1877f2;color:#fff;border-color:#1877f2;}}
QPushButton#igBtn{{background:#e1306c18;color:#f472b6;
  border:1px solid #e1306c33;border-radius:9px;padding:9px 14px;font-weight:600;font-size:12px;}}
QPushButton#igBtn[active="true"]{{background:#e1306c;color:#fff;border-color:#e1306c;}}
QPushButton#twBtn{{background:#1da1f218;color:#38bdf8;
  border:1px solid #1da1f233;border-radius:9px;padding:9px 14px;font-weight:600;font-size:12px;}}
QPushButton#twBtn[active="true"]{{background:#1da1f2;color:#fff;border-color:#1da1f2;}}
QPushButton#pinBtn{{background:#e6002318;color:#f87171;
  border:1px solid #e6002333;border-radius:9px;padding:9px 14px;font-weight:600;font-size:12px;}}
QPushButton#pinBtn[active="true"]{{background:#e60023;color:#fff;border-color:#e60023;}}
QPushButton#ytBtn{{background:#ff000018;color:#f87171;
  border:1px solid #ff000033;border-radius:9px;padding:9px 14px;font-weight:600;font-size:12px;}}
QPushButton#ytBtn[active="true"]{{background:#ff0000;color:#fff;border-color:#ff0000;}}

/* ── LOG ── */
#logBox{{background:{BG};border:1px solid {BOR};border-radius:10px;
  color:{CYN2};font-family:'Cascadia Code','Consolas',monospace;
  font-size:11px;padding:10px;}}

/* ── PROGRESS ── */
QProgressBar{{background:{SUR2};border:none;border-radius:5px;height:8px;font-size:0;}}
QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
  stop:0 {PURP},stop:1 {PINK});border-radius:5px;}}

/* ── SCROLLBARS ── */
QScrollBar:vertical{{background:transparent;width:5px;}}
QScrollBar::handle:vertical{{background:{BOR2};border-radius:3px;min-height:20px;}}
QScrollBar::handle:vertical:hover{{background:{PURP}55;}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
QScrollBar:horizontal{{background:transparent;height:5px;}}
QScrollBar::handle:horizontal{{background:{BOR2};border-radius:3px;}}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{{width:0;}}
"""

# ═══════════════════════════════════════════════════════
#  USER-AGENTS (120+)
# ═══════════════════════════════════════════════════════
UA_GROUPS = {
    "Random (All)": [],
    "Chrome Windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ],
    "Chrome Mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ],
    "Firefox Windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ],
    "Firefox Mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:126.0) Gecko/20100101 Firefox/126.0",
    ],
    "Safari Mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ],
    "Edge Windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        # ],
        # "Mobile Chrome Android": [
        #     "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 14; Samsung Galaxy S24) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        # ],
        # "Mobile Safari iPhone": [
        #     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        #     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
        #     "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        #     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.6367.88 Mobile/15E148 Safari/604.1",
        # ],
        # "Samsung Browser": [
        #     "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/111.0.0.0 Mobile Safari/537.36",
        # ],
        # "UCBrowser Android": [
        #     "Mozilla/5.0 (Linux; U; Android 12; en-US; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 UCBrowser/13.4.0.1306 Mobile Safari/537.36",
        #     "Mozilla/5.0 (Linux; U; Android 13; en-US; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 UCBrowser/13.4.0.1306 Mobile Safari/537.36",
    ],
}
for k, v in UA_GROUPS.items():
    if k != "Random (All)":
        UA_GROUPS["Random (All)"].extend(v)

RESOLUTIONS = ["1920x1080","2560x1440","1366x768","1440x900","1280x800","1536x864","375x812","390x844","414x896"]
PLATFORMS   = ["Win32","MacIntel","Linux x86_64"]
WEBGL_LIST  = [
    ("Google Inc.","ANGLE (NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0)"),
    ("Google Inc.","ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)"),
    ("Intel Inc.", "Intel(R) UHD Graphics 630"),
    ("AMD",        "Radeon RX 580 Series"),
    ("Apple",      "Apple M1"),
    ("Apple",      "Apple M2"),
]

SOCIAL_REFERERS = {
    "facebook":  ["https://www.facebook.com/","https://l.facebook.com/","https://m.facebook.com/","https://www.facebook.com/feed/"],
    "instagram": ["https://www.instagram.com/","https://www.instagram.com/explore/","https://www.instagram.com/reels/"],
    "twitter":   ["https://twitter.com/","https://t.co/","https://x.com/"],
    "pinterest": ["https://www.pinterest.com/","https://pin.it/"],
    "youtube":   ["https://www.youtube.com/","https://m.youtube.com/"],
}

ORGANIC_QUERIES = [
    "best websites 2024","top blogs to read","interesting articles today",
    "must read content online","trending news articles","helpful guides and tutorials",
    "learn something new today","popular websites to visit","top rated content online",
    "best resources for beginners","informative articles 2024","latest updates and news",
    "recommended reading list","useful tools and websites","expert tips and advice",
    "quality content to explore","interesting reads this week","top educational websites",
    "best how-to guides online","most visited pages today","trending topics 2024",
    "best online resources","top reviewed websites","comprehensive guides online",
]
ORGANIC_ENGINES = [
    "https://www.google.com/search?q=",
    "https://www.google.co.uk/search?q=",
    "https://www.bing.com/search?q=",
    "https://duckduckgo.com/?q=",
    "https://search.yahoo.com/search?p=",
]


def make_profile(ua_group="Random (All)"):
    pool = UA_GROUPS.get(ua_group, UA_GROUPS["Random (All)"])
    ua   = random.choice(pool) if pool else random.choice(UA_GROUPS["Random (All)"])
    is_mobile = any(k in ua for k in ["Mobile","Android","iPhone","Samsung","UCBrowser"])
    res  = random.choice(["375x812","390x844","414x896"] if is_mobile
                         else ["1920x1080","2560x1440","1366x768","1440x900"])
    # Correct platform detection
    if "Macintosh" in ua or "Mac OS X" in ua:
        plat = "MacIntel"
    elif "Windows" in ua:
        plat = "Win32"
    elif "Linux" in ua and "Android" not in ua:
        plat = "Linux x86_64"
    else:
        plat = "Win32"  # default for mobile/unknown
    wv, wr = random.choice(WEBGL_LIST)
    w, h   = map(int, res.split("x"))
    # Short labels
    if   "Firefox"     in ua: br = "Firefox"
    elif "SamsungBrowser" in ua: br = "Samsung Browser"
    elif "UCBrowser"   in ua: br = "UCBrowser"
    elif "Edg"         in ua: br = "Edge"
    elif "CriOS"       in ua: br = "Chrome iOS"
    elif "Chrome"      in ua: br = "Chrome"
    elif "Safari"      in ua: br = "Safari"
    else:                      br = "Browser"
    dev = "📱 Mobile" if is_mobile else "🖥 Desktop"
    return {"user_agent": ua, "viewport": {"width": w, "height": h},
            "platform": plat, "webgl_v": wv, "webgl_r": wr,
            "hw_conc": random.choice([2,4,6,8]), "device_ram": random.choice([4,8,16]),
            "browser": br, "device": dev}

# ═══════════════════════════════════════════════════════
#  PROXY PARSER
# ═══════════════════════════════════════════════════════
def parse_proxy(raw: str) -> Optional[dict]:
    raw = raw.strip()
    if not raw or raw.startswith("#"): return None
    scheme = "socks5"
    if "://" in raw:
        scheme, raw = raw.split("://", 1)
        user = pwd = None
        if "@" in raw:
            creds, raw = raw.rsplit("@", 1)
            user, pwd = creds.split(":", 1) if ":" in creds else (creds, None)
        if ":" not in raw: return None
        host, port_s = raw.rsplit(":", 1)
        try: port = int(port_s)
        except ValueError: return None
        return {"scheme": scheme, "host": host, "port": port,
                "user": user or "", "pass": pwd or ""}
    if "@" in raw:
        creds, rest = raw.rsplit("@", 1)
        user, pwd = creds.split(":", 1) if ":" in creds else (creds, "")
        host, port_s = rest.rsplit(":", 1)
        try: port = int(port_s)
        except ValueError: return None
        return {"scheme": "socks5", "host": host, "port": port, "user": user, "pass": pwd}
    parts = raw.split(":")
    if len(parts) == 4:
        a, b, c, d = parts
        # Detect format by checking if part[1] or part[3] is a valid port number
        # Format 1: ip:port:user:pass  → parts[1] is the port (numeric)
        # Format 2: user:pass:host:port → parts[3] is the port (numeric)
        try:
            port = int(b)   # ip:port:user:pass
            return {"scheme": "socks5", "host": a, "port": port,
                    "user": c, "pass": d}
        except ValueError:
            pass
        try:
            port = int(d)   # user:pass:host:port  ← your format
            return {"scheme": "socks5", "host": c, "port": port,
                    "user": a, "pass": b}
        except ValueError:
            return None
    elif len(parts) == 2:
        host, port_s = parts
        try: port = int(port_s)
        except ValueError: return None
        return {"scheme": "socks5", "host": host, "port": port, "user": "", "pass": ""}
    return None

# ═══════════════════════════════════════════════════════
#  SOCKS5 TUNNEL
# ═══════════════════════════════════════════════════════
class Socks5Tunnel:
    def __init__(self, host, port, user=None, pwd=None):
        self._h=host; self._p=int(port); self._u=user; self._pw=pwd
        self._srv=None; self.local_port=0
        self._tasks: list = []   # track all tasks for clean shutdown

    async def start(self) -> int:
        self._srv = await asyncio.start_server(self._handle,"127.0.0.1",0)
        self.local_port = self._srv.sockets[0].getsockname()[1]
        t = asyncio.get_event_loop().create_task(self._serve())
        self._tasks.append(t)
        return self.local_port

    async def _serve(self):
        try:
            async with self._srv:
                await self._srv.serve_forever()
        except asyncio.CancelledError:
            pass

    async def stop(self):
        if self._srv:
            self._srv.close()
        # Cancel all tracked tasks cleanly
        for t in self._tasks:
            if not t.done():
                t.cancel()
                try:
                    await asyncio.wait_for(asyncio.shield(t), timeout=0.5)
                except Exception:
                    pass
        self._tasks.clear()

    async def _handle(self, r, w):
        t = asyncio.current_task()
        if t: self._tasks.append(t)
        try:
            await self._session(r, w)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        finally:
            try: w.close()
            except Exception: pass

    async def _session(self, cr, cw):
        hdr = await cr.read(2)
        if not hdr or hdr[0] != 5: return
        await cr.read(hdr[1]); cw.write(b"\x05\x00"); await cw.drain()
        req = await cr.read(4)
        if not req or req[0] != 5: return
        cmd, atyp = req[1], req[3]
        if   atyp==1: host=socket.inet_ntoa(await cr.read(4))
        elif atyp==3: ln=(await cr.read(1))[0]; host=(await cr.read(ln)).decode()
        elif atyp==4: host=socket.inet_ntop(socket.AF_INET6,await cr.read(16))
        else: cw.write(b"\x05\x08\x00\x01"+b"\x00"*6); await cw.drain(); return
        port=struct.unpack("!H",await cr.read(2))[0]
        if cmd!=1: cw.write(b"\x05\x07\x00\x01"+b"\x00"*6); await cw.drain(); return
        loop=asyncio.get_event_loop()
        try:
            sock=await loop.run_in_executor(None,self._connect,host,port)
            rr,rw=await asyncio.open_connection(sock=sock)
            cw.write(b"\x05\x00\x00\x01"+b"\x00"*6); await cw.drain()
            await asyncio.gather(self._relay(cr,rw),self._relay(rr,cw),return_exceptions=True)
        except Exception:
            try: cw.write(b"\x05\x05\x00\x01"+b"\x00"*6); await cw.drain()
            except Exception: pass

    def _connect(self, host, port):
        import socks as _s
        s=_s.socksocket()
        s.set_proxy(_s.SOCKS5,self._h,self._p,rdns=True,username=self._u,password=self._pw)
        s.settimeout(20); s.connect((host,port)); s.setblocking(False); return s

    @staticmethod
    async def _relay(r, w):
        try:
            while True:
                data=await r.read(65536)
                if not data: break
                w.write(data); await w.drain()
        except Exception: pass
        finally:
            try: w.close()
            except Exception: pass

# ═══════════════════════════════════════════════════════
#  DATA MODELS
# ═══════════════════════════════════════════════════════
@dataclass
class ProjectConfig:
    id:             str   = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    name:           str   = "My Project"
    url:            str   = ""
    keyword:        str   = ""          # for organic search query
    socks_list:     List[str] = field(default_factory=list)
    traffic_source: str   = "direct"
    ua_group:       str   = "Random (All)"
    workers:        int   = 5
    tabs:           int   = 2
    impressions:    int   = 100
    stay_min:       float = 20.0
    stay_max:       float = 50.0
    headless:       bool  = True
    created:        str   = field(default_factory=lambda: datetime.now().strftime("%d %b %Y"))

    def to_dict(self): return asdict(self)

    @staticmethod
    def from_dict(d): return ProjectConfig(**{k:v for k,v in d.items() if k in ProjectConfig.__dataclass_fields__})

# ═══════════════════════════════════════════════════════
#  STORE
# ═══════════════════════════════════════════════════════
import uuid
class Store:
    PATH = os.path.join(os.path.expanduser("~"), ".trafficforge_v4.json")
    def __init__(self):
        self.projects: Dict[str, ProjectConfig] = {}
        self._load()
    def _load(self):
        if os.path.exists(self.PATH):
            try:
                with open(self.PATH) as f:
                    for d in json.load(f):
                        p = ProjectConfig.from_dict(d)
                        self.projects[p.id] = p
            except Exception: pass
    def save(self):
        try:
            with open(self.PATH,"w") as f:
                json.dump([p.to_dict() for p in self.projects.values()],f,indent=2)
        except Exception: pass
    def add(self, p): self.projects[p.id]=p; self.save()
    def update(self, p): self.projects[p.id]=p; self.save()
    def delete(self, pid): self.projects.pop(pid,None); self.save()
    def all(self): return list(self.projects.values())

# ═══════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════
class Logger(QObject):
    sig = pyqtSignal(str)
    C   = {"INFO":CYAN,"OK":GRNS,"WARN":YEL,"ERROR":RED,
           "SYS":PRP2,"HIT":GRNS,"EXPIRE":ORG}
    def emit(self, msg, level="INFO"):
        ts=datetime.now().strftime("%H:%M:%S")
        col=self.C.get(level,TXT)
        self.sig.emit(
            f'<span style="color:{TX3}">[{ts}]</span> '
            f'<span style="color:{col};font-weight:bold">[{level}]</span> '
            f'<span style="color:{TX2}">{msg}</span>')

LOG = Logger()

# ═══════════════════════════════════════════════════════
#  TRAFFIC CHART WIDGET
# ═══════════════════════════════════════════════════════
class TrafficChart(QWidget):
    """Live area chart — hits per second with cumulative progress bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[int] = [0]*60   # hits per second, last 60s
        self._max   = 1
        self._total = 0    # cumulative hits
        self._target= 0    # target impressions
        self.setMinimumHeight(160)
        self._timer = QTimer()
        self._timer.timeout.connect(self._shift)
        self._timer.start(1000)

    def set_target(self, target: int):
        self._target = target
        self._total  = 0
        self.update()

    def _shift(self):
        self._data.pop(0); self._data.append(0)
        self.update()

    def add_hit(self, n: int = 1):
        self._data[-1] += n
        self._total    += n
        if self._data[-1] > self._max: self._max = self._data[-1]
        self.update()

    def reset(self):
        self._data   = [0]*60
        self._max    = 1
        self._total  = 0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(SURF))
        p.setPen(Qt.NoPen)

        # ── Progress bar at top (visits / target) ──────────
        bar_h = 22
        bar_r = QRect(0, 0, w, bar_h)
        p.fillRect(bar_r, QColor(SUR2))
        if self._target > 0:
            pct = min(1.0, self._total / self._target)
            fill_w = int(w * pct)
            grad_b = QLinearGradient(0,0,fill_w,0)
            grad_b.setColorAt(0, QColor(PURP))
            grad_b.setColorAt(1, QColor(PINK))
            p.fillRect(QRect(0,0,fill_w,bar_h), QBrush(grad_b))
            # White text always visible on gradient
            p.setPen(QColor("#ffffff"))
            p.setFont(QFont("Segoe UI",9,QFont.Bold))
            pct_txt = f"{self._total:,} / {self._target:,}  ({int(pct*100)}%)"
            p.drawText(QRect(0,0,w,bar_h), Qt.AlignCenter, pct_txt)

        # ── Area chart below ────────────────────────────────
        pad  = 8
        cy   = bar_h + pad   # chart top y
        ch   = h - bar_h - pad*2  # chart height

        n = len(self._data)
        if self._max == 0 or ch < 10:
            p.end(); return

        pts = []
        for i, v in enumerate(self._data):
            x = pad + i*(w-2*pad)/max(n-1,1)
            y = cy + ch - (v/self._max)*ch
            pts.append(QPointF(x, y))

        if not pts: p.end(); return

        # Gradient fill
        grad = QLinearGradient(0, cy, 0, cy+ch)
        grad.setColorAt(0, QColor(PURP+"aa"))
        grad.setColorAt(0.5, QColor(PINK+"55"))
        grad.setColorAt(1, QColor(PURP+"00"))
        path = QPainterPath()
        path.moveTo(pts[0].x(), cy+ch)
        for pt in pts:
            path.lineTo(pt)
        path.lineTo(pts[-1].x(), cy+ch)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(path, QBrush(grad))

        # Line
        pen = QPen(QColor(PRP2), 2.2)
        p.setPen(pen)
        for i in range(1, len(pts)):
            p.drawLine(pts[i-1], pts[i])

        # Labels
        p.setPen(QColor(TX3))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(pad, h-2, "60s ago")
        p.drawText(w-60, h-2, "Now")

        p.end()

# ═══════════════════════════════════════════════════════
#  VISIT TABLE WIDGET
# ═══════════════════════════════════════════════════════
class VisitTable(QWidget):
    """Shows recent page visits like TrafficPeak."""

    MAX_ROWS = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Device","Browser","URL","Source","Time"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for i in [0,1,3,4]:
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        lay.addWidget(self.table)

    def add_visit(self, device: str, browser: str, url: str,
                  source: str, elapsed_s: float):
        row = 0
        self.table.insertRow(row)
        self.table.setRowHeight(row, 40)

        def c(text, col=TX2, bold=False):
            item = QTableWidgetItem(str(text))
            item.setForeground(QColor(col))
            if bold: f=QFont(); f.setBold(True); item.setFont(f)
            return item

        # Source color
        src_colors = {
            "direct":"#94a3b8","organic":GRNS,"facebook":"#60a5fa",
            "instagram":"#f472b6","twitter":"#38bdf8",
            "pinterest":"#f87171","youtube":"#f87171","all_social":PRP2,
        }
        src_col = src_colors.get(source, TX2)

        self.table.setItem(row, 0, c(device))
        self.table.setItem(row, 1, c(browser, CYN2))
        self.table.setItem(row, 2, c(url, TXT, bold=True))
        self.table.setItem(row, 3, c(source, src_col))
        self.table.setItem(row, 4, c(f"{elapsed_s:.0f}s ago", TX3))

        # Remove oldest if too many
        if self.table.rowCount() > self.MAX_ROWS:
            self.table.removeRow(self.MAX_ROWS)

    def clear(self):
        self.table.setRowCount(0)

    def tick_times(self):
        """Called every second to update elapsed times (just redraw)."""
        pass  # times are static labels; keep it simple

# ═══════════════════════════════════════════════════════
#  HELP DIALOG (Proxy Formats)
# ═══════════════════════════════════════════════════════
class ProxyHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Proxy Format Guide")
        self.setModal(True); self.setFixedSize(560, 380)
        self.setStyleSheet(f"background:{PAN};")
        lay = QVBoxLayout(self); lay.setContentsMargins(24,20,24,20); lay.setSpacing(14)

        t = QLabel("Supported Proxy Formats")
        t.setStyleSheet(f"font-size:16px;font-weight:bold;color:{PRP2};")
        lay.addWidget(t)

        rows = [
            ("★  ip:port:user:pass",        "46.224.52.65:42601:myuser:mypass",        "← YOUR FORMAT (auto-converted)"),
            ("socks5://user:pass@ip:port",   "socks5://u:p@91.99.95.238:43185",         "← Tisocks.net standard"),
            ("ip:port",                      "119.154.199.23:1080",                     "← no auth, plain SOCKS5"),
            ("user:pass@ip:port",            "user:pass@91.99.95.238:43185",            "← with credentials"),
            ("http://user:pass@host:port",   "http://u:p@proxy.com:3128",               "← HTTP proxy"),
        ]

        for fmt, ex, note in rows:
            row_w = QWidget()
            row_w.setStyleSheet(f"background:{SUR2};border:1px solid {BOR};border-radius:8px;padding:8px;")
            rl = QVBoxLayout(row_w); rl.setContentsMargins(10,6,10,6); rl.setSpacing(2)
            top = QLabel(fmt); top.setStyleSheet(f"color:{PRP2};font-family:'Consolas';font-size:12px;font-weight:bold;")
            ex_l = QLabel(ex); ex_l.setStyleSheet(f"color:{CYN2};font-family:'Consolas';font-size:11px;")
            note_l = QLabel(note); note_l.setStyleSheet(f"color:{TX3};font-size:11px;")
            rl.addWidget(top); rl.addWidget(ex_l); rl.addWidget(note_l)
            lay.addWidget(row_w)

        note2 = QLabel("★ SOCKS5 with auth uses a local tunnel via PySocks automatically.")
        note2.setStyleSheet(f"color:{YEL};font-size:11px;")
        lay.addWidget(note2)

        close = QPushButton("Close"); close.setObjectName("ghostBtn")
        close.clicked.connect(self.accept)
        lay.addWidget(close, alignment=Qt.AlignRight)

# ═══════════════════════════════════════════════════════
#  PROJECT WIZARD DIALOG
# ═══════════════════════════════════════════════════════
class ProjectDialog(QDialog):
    """Full project creation / edit dialog."""

    def __init__(self, parent=None, project: Optional[ProjectConfig] = None):
        super().__init__(parent)
        self.proj = deepcopy(project) if project else ProjectConfig()
        self.setWindowTitle("Edit Project" if project else "New Project")
        self.setModal(True); self.setMinimumSize(720, 680)
        self.resize(780, 720)
        self.setStyleSheet(f"background:{PAN};")
        self._current_source = self.proj.traffic_source
        self._build()
        self._fill()

    def _build(self):
        main = QVBoxLayout(self); main.setContentsMargins(0,0,0,0); main.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setStyleSheet(f"background:{SUR2};border-bottom:1px solid {BOR};")
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(24,18,24,18)
        t   = QLabel("✦  Project Configuration")
        t.setStyleSheet(f"font-size:17px;font-weight:bold;color:{TXT};")
        hl.addWidget(t); hl.addStretch()
        main.addWidget(hdr)

        # Scroll body
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        body = QWidget(); body.setStyleSheet(f"background:{PAN};")
        bl   = QVBoxLayout(body); bl.setContentsMargins(24,20,24,20); bl.setSpacing(20)

        def lbl(t, col=None):
            l = QLabel(t.upper())
            l.setStyleSheet(f"font-size:10px;font-weight:bold;color:{col or TX3};letter-spacing:1px;padding-bottom:3px;")
            return l

        # ── Basic ─────────────────────────────────────────
        basic = QWidget(); basic.setObjectName("card")
        bg = QGridLayout(basic); bg.setSpacing(14); bg.setContentsMargins(0,0,0,0)
        bg.addWidget(lbl("Project Name"), 0, 0)
        self.name_le = QLineEdit(); self.name_le.setPlaceholderText("e.g. CryptoWeir Traffic")
        bg.addWidget(self.name_le, 1, 0)
        bg.addWidget(lbl("Target URL"), 0, 1)
        self.url_le = QLineEdit(); self.url_le.setPlaceholderText("https://yourwebsite.com")
        bg.addWidget(self.url_le, 1, 1)
        bg.addWidget(lbl("Keyword  (for Organic search query)"), 2, 0, 1, 2)
        self.kw_le = QLineEdit(); self.kw_le.setPlaceholderText("e.g.  crypto news  best defi sites  bitcoin tips  (leave blank for random)")
        bg.addWidget(self.kw_le, 3, 0, 1, 2)
        bl.addWidget(basic)

        # ── Traffic Source ────────────────────────────────
        src_card = QWidget(); src_card.setObjectName("card")
        sc = QVBoxLayout(src_card); sc.setSpacing(12)
        sc.addWidget(lbl("Traffic Source", PRP2))
        row1 = QHBoxLayout(); row1.setSpacing(8)
        self._src_btns: Dict[str, QPushButton] = {}
        for key, label, obj in [("direct","🔗 Direct","srcBtn"),("organic","🔍 Organic","srcBtn"),("all_social","📱 All Social","srcBtn")]:
            b=QPushButton(label); b.setObjectName(obj)
            b.clicked.connect(lambda _,k=key: self._set_src(k))
            self._src_btns[key]=b; row1.addWidget(b)
        row1.addStretch(); sc.addLayout(row1)
        sc.addWidget(lbl("Individual Social Networks", TX3))
        row2 = QHBoxLayout(); row2.setSpacing(8)
        for key, label, obj in [("facebook","📘 Facebook","fbBtn"),("instagram","📸 Instagram","igBtn"),
                                ("twitter","🐦 Twitter","twBtn"),("pinterest","📌 Pinterest","pinBtn"),("youtube","▶ YouTube","ytBtn")]:
            b=QPushButton(label); b.setObjectName(obj)
            b.clicked.connect(lambda _,k=key: self._set_src(k))
            self._src_btns[key]=b; row2.addWidget(b)
        row2.addStretch(); sc.addLayout(row2)
        self.src_info = QLabel(""); self.src_info.setStyleSheet(f"color:{CYN2};font-size:12px;font-weight:bold;")
        sc.addWidget(self.src_info)
        bl.addWidget(src_card)

        # ── Settings grid ─────────────────────────────────
        cfg_card = QWidget(); cfg_card.setObjectName("card")
        cg = QGridLayout(cfg_card); cg.setSpacing(14); cg.setContentsMargins(0,0,0,0)
        cg.addWidget(lbl("Total Impressions"), 0, 0)
        self.imp_sp = QSpinBox(); self.imp_sp.setRange(1,999999); self.imp_sp.setValue(100)
        cg.addWidget(self.imp_sp, 1, 0)
        cg.addWidget(lbl("Concurrent Workers"), 0, 1)
        self.wk_sp = QSpinBox(); self.wk_sp.setRange(1,50); self.wk_sp.setValue(5)
        cg.addWidget(self.wk_sp, 1, 1)
        cg.addWidget(lbl("Tabs per Worker"), 2, 0)
        self.tabs_sp = QSpinBox(); self.tabs_sp.setRange(1,20); self.tabs_sp.setValue(2)
        cg.addWidget(self.tabs_sp, 3, 0)
        cg.addWidget(lbl("Stay Min (sec)"), 2, 1)
        self.smin_sp = QDoubleSpinBox(); self.smin_sp.setRange(5,600); self.smin_sp.setValue(20); self.smin_sp.setSingleStep(5)
        cg.addWidget(self.smin_sp, 3, 1)
        cg.addWidget(lbl("Stay Max (sec)"), 4, 1)
        self.smax_sp = QDoubleSpinBox(); self.smax_sp.setRange(5,600); self.smax_sp.setValue(50); self.smax_sp.setSingleStep(5)
        cg.addWidget(self.smax_sp, 5, 1)
        cg.addWidget(lbl("User-Agent Group"), 4, 0)
        self.ua_cb = QComboBox()
        for grp in UA_GROUPS: self.ua_cb.addItem(f"{grp}  ({len(UA_GROUPS[grp])} UAs)", grp)
        cg.addWidget(self.ua_cb, 5, 0)
        # Headless
        self.headless_chk = QCheckBox("Headless mode  (invisible browsers — faster)")
        self.headless_chk.setChecked(True)
        cg.addWidget(self.headless_chk, 6, 0, 1, 2)
        bl.addWidget(cfg_card)

        # ── SOCKS (row-based) ─────────────────────────────
        socks_card = QWidget(); socks_card.setObjectName("card")
        sk = QVBoxLayout(socks_card); sk.setSpacing(10)
        socks_hdr = QHBoxLayout()
        socks_hdr.addWidget(lbl("SOCKS Proxies  — one per row", PRP2))
        socks_hdr.addStretch()
        help_btn = QPushButton("?"); help_btn.setObjectName("helpBtn")
        help_btn.setToolTip("View proxy format guide")
        help_btn.clicked.connect(lambda: ProxyHelpDialog(self).exec_())
        socks_hdr.addWidget(help_btn)
        sk.addLayout(socks_hdr)

        # Input row
        add_row = QHBoxLayout(); add_row.setSpacing(8)
        self.socks_le = QLineEdit()
        self.socks_le.setPlaceholderText("46.224.52.65:42601:user:pass   or   socks5://u:p@host:port")
        self.socks_le.returnPressed.connect(self._add_socks)
        add_btn = QPushButton("+ Add"); add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self._add_socks)
        load_btn = QPushButton("📂 Load .txt"); load_btn.setObjectName("ghostBtn")
        load_btn.clicked.connect(self._load_socks)
        add_row.addWidget(self.socks_le, 1); add_row.addWidget(add_btn); add_row.addWidget(load_btn)
        sk.addLayout(add_row)

        # SOCKS list widget
        self.socks_lw = QListWidget()
        self.socks_lw.setFixedHeight(150)
        sk.addWidget(self.socks_lw)

        socks_footer = QHBoxLayout()
        self.socks_count_lbl = QLabel("0 proxies added")
        self.socks_count_lbl.setStyleSheet(f"color:{TX3};font-size:11px;")
        clear_all_btn = QPushButton("🗑  Remove All Proxies")
        clear_all_btn.setObjectName("removeBtn")
        clear_all_btn.setFixedHeight(28)
        clear_all_btn.clicked.connect(self._clear_all_socks)
        socks_footer.addWidget(self.socks_count_lbl)
        socks_footer.addStretch()
        socks_footer.addWidget(clear_all_btn)
        sk.addLayout(socks_footer)
        bl.addWidget(socks_card)

        scroll.setWidget(body)
        main.addWidget(scroll, 1)

        # Footer with NEXT (white) at bottom
        ftr = QWidget(); ftr.setStyleSheet(f"background:{SUR2};border-top:1px solid {BOR};")
        fl2 = QHBoxLayout(ftr); fl2.setContentsMargins(24,16,24,16)
        cancel = QPushButton("Cancel"); cancel.setObjectName("ghostBtn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("✓  Save Project")
        save.setObjectName("nextBtn"); save.clicked.connect(self._save)
        fl2.addWidget(cancel); fl2.addStretch(); fl2.addWidget(save)
        main.addWidget(ftr)

    def _fill(self):
        p = self.proj
        self.name_le.setText(p.name)
        self.url_le.setText(p.url)
        self.kw_le.setText(p.keyword)
        self.imp_sp.setValue(p.impressions)
        self.wk_sp.setValue(p.workers)
        self.tabs_sp.setValue(p.tabs)
        self.smin_sp.setValue(p.stay_min)
        self.smax_sp.setValue(p.stay_max)
        self.headless_chk.setChecked(p.headless)
        idx = self.ua_cb.findData(p.ua_group)
        if idx >= 0: self.ua_cb.setCurrentIndex(idx)
        self._set_src(p.traffic_source)
        for s in p.socks_list:
            self._add_socks_row(s)

    def _set_src(self, key):
        self._current_source = key
        info = {
            "direct":    "🔗 Direct — browser navigates directly (no referrer)",
            "organic":   "🔍 Organic — simulates Google/Bing search click",
            "all_social":"📱 All Social — random from all platforms per tab",
            "facebook":  "📘 Facebook — traffic appears from Facebook",
            "instagram": "📸 Instagram — traffic appears from Instagram",
            "twitter":   "🐦 Twitter/X — traffic appears from Twitter",
            "pinterest": "📌 Pinterest — traffic appears from Pinterest",
            "youtube":   "▶ YouTube — traffic appears from YouTube",
        }
        self.src_info.setText(info.get(key,""))
        for k, btn in self._src_btns.items():
            btn.setProperty("active","true" if k==key else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

    def _add_socks(self):
        raw = self.socks_le.text().strip()
        if not raw: return
        if not parse_proxy(raw):
            self.socks_le.setStyleSheet(f"border:1px solid {RED}88;")
            return
        self.socks_le.setStyleSheet("")
        self._add_socks_row(raw)
        self.socks_le.clear()

    def _add_socks_row(self, raw: str):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, raw)
        # Row widget
        row_w = QWidget(); row_w.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(row_w); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)
        # Parse for display
        info = parse_proxy(raw)
        if info:
            disp = f"socks5://{info['user']}:***@{info['host']}:{info['port']}" if info["user"] else f"{info['scheme']}://{info['host']}:{info['port']}"
        else:
            disp = raw[:60]
        lbl_w = QLabel(f"🔒  {disp}")
        lbl_w.setStyleSheet(f"color:{CYN2};font-family:'Consolas';font-size:11px;")
        rm_btn = QPushButton("✕ Remove"); rm_btn.setObjectName("removeBtn")
        rm_btn.setFixedHeight(26)
        rm_btn.clicked.connect(lambda: self._remove_socks(item))
        rl.addWidget(lbl_w, 1); rl.addWidget(rm_btn)
        item.setSizeHint(QSize(0, 46))
        self.socks_lw.addItem(item)
        self.socks_lw.setItemWidget(item, row_w)
        self._update_socks_count()

    def _clear_all_socks(self):
        self.socks_lw.clear()
        self._update_socks_count()

    def _remove_socks(self, item: QListWidgetItem):
        row = self.socks_lw.row(item)
        if row >= 0: self.socks_lw.takeItem(row)
        self._update_socks_count()

    def _update_socks_count(self):
        n = self.socks_lw.count()
        self.socks_count_lbl.setText(
            f"{n} {'proxy' if n==1 else 'proxies'} added"
            + (" — will run direct if 0" if n==0 else ""))

    def _load_socks(self):
        p,_ = QFileDialog.getOpenFileName(self,"Load SOCKS","","Text (*.txt)")
        if not p: return
        with open(p,encoding="utf-8",errors="ignore") as f:
            for line in f:
                raw = line.strip()
                if raw and not raw.startswith("#") and parse_proxy(raw):
                    self._add_socks_row(raw)

    def _save(self):
        name = self.name_le.text().strip()
        url  = self.url_le.text().strip()
        if not name:
            QMessageBox.warning(self,"Error","Project name cannot be empty."); return
        if not url or not url.startswith(("http://","https://")):
            QMessageBox.warning(self,"Error","Enter a valid URL starting with https://"); return
        if self.smin_sp.value() > self.smax_sp.value():
            QMessageBox.warning(self,"Error","Stay Min cannot exceed Stay Max."); return

        socks = [self.socks_lw.item(i).data(Qt.UserRole)
                 for i in range(self.socks_lw.count())]
        self.proj.name           = name
        self.proj.url            = url
        self.proj.keyword        = self.kw_le.text().strip()
        self.proj.socks_list     = socks
        self.proj.traffic_source = self._current_source
        self.proj.ua_group       = self.ua_cb.currentData()
        self.proj.impressions    = self.imp_sp.value()
        self.proj.workers        = self.wk_sp.value()
        self.proj.tabs           = self.tabs_sp.value()
        self.proj.stay_min       = self.smin_sp.value()
        self.proj.stay_max       = self.smax_sp.value()
        self.proj.headless       = self.headless_chk.isChecked()
        self.accept()

    def result(self) -> ProjectConfig:
        return self.proj

# ═══════════════════════════════════════════════════════
#  WORKER  (browser session)
# ═══════════════════════════════════════════════════════
COOKIE_SELECTORS = [
    # Common cookie consent
    "button[id*='accept']","button[id*='cookie']","button[id*='consent']",
    "button[class*='accept']","button[class*='cookie']","button[class*='consent']",
    "button[aria-label*='Accept']","button[aria-label*='accept']",
    # Common popup close buttons
    "button[class*='close']","button[aria-label*='Close']",
    "button[aria-label*='close']","[class*='modal-close']",
    "[class*='popup-close']","[id*='popup-close']",
    # GDPR specific
    "#onetrust-accept-btn-handler",".cc-btn.cc-allow",
    "[data-testid='cookie-accept']","#accept-cookie-consent",
    ".cookie-accept","#cookieAccept",".js-cookie-accept",
]

async def _close_popups(page):
    """Try to close cookie banners and popups after page load."""
    try:
        for selector in COOKIE_SELECTORS:
            try:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    await el.click(timeout=1000)
                    await asyncio.sleep(0.3)
                    break
            except Exception:
                continue
    except Exception:
        pass

# ═══════════════════════════════════════════════════════
#  WORKER  (browser session)
# ═══════════════════════════════════════════════════════
class ImpressionWorker:
    def __init__(self, wid, proj: ProjectConfig, proxy_raw, stop_ev, counter, visit_cb):
        self.wid=wid; self.proj=proj; self.proxy_raw=proxy_raw
        self.stop=stop_ev; self.counter=counter; self.visit_cb=visit_cb
        self._tunnel=None

    async def _resolve_proxy(self):
        if not self.proxy_raw: return None
        info = parse_proxy(self.proxy_raw)
        if not info: return None
        scheme,host,port,user,pwd = info["scheme"],info["host"],info["port"],info["user"],info["pass"]
        if scheme.startswith("socks") and user:
            self._tunnel = Socks5Tunnel(host,port,user,pwd)
            lp = await self._tunnel.start()
            LOG.emit(f"[W{self.wid}] Tunnel :{lp}→{host}:{port}","SYS")
            return {"server":f"socks5://127.0.0.1:{lp}"}
        if scheme.startswith("socks"): return {"server":f"{scheme}://{host}:{port}"}
        px = {"server":f"{scheme}://{host}:{port}"}
        if user: px["username"]=user; px["password"]=pwd
        return px

    async def run(self, browser):
        if self.stop.is_set(): return
        profile  = make_profile(self.proj.ua_group)
        pw_proxy = await self._resolve_proxy()
        ctx_args = {"user_agent":profile["user_agent"],"viewport":profile["viewport"]}
        if pw_proxy: ctx_args["proxy"]=pw_proxy
        context=None
        try:
            context = await browser.new_context(**ctx_args)
            await context.add_init_script(f"""
                Object.defineProperty(navigator,'platform',{{get:()=>'{profile["platform"]}'}});
                Object.defineProperty(navigator,'hardwareConcurrency',{{get:()=>{profile["hw_conc"]}}});
                Object.defineProperty(navigator,'deviceMemory',{{get:()=>{profile["device_ram"]}}});
                Object.defineProperty(navigator,'webdriver',{{get:()=>undefined}});
                Object.defineProperty(navigator,'plugins',{{get:()=>Array(3).fill({{}})}});
                Object.defineProperty(navigator,'languages',{{get:()=>['en-US','en']}});
                const _wp=WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter=function(q){{
                    if(q===37445)return'{profile["webgl_v"]}';
                    if(q===37446)return'{profile["webgl_r"]}';
                    return _wp.call(this,q);
                }};
                window.chrome={{runtime:{{}}}};
            """)
            self.counter["active"]+=1
            tasks=[asyncio.create_task(self._tab(context,profile,i)) for i in range(self.proj.tabs)]
            await asyncio.gather(*tasks,return_exceptions=True)
        except Exception as exc:
            LOG.emit(f"[W{self.wid}] Context err: {str(exc)[:70]}","ERROR")
        finally:
            self.counter["active"]=max(0,self.counter["active"]-1)
            try:
                if context: await context.close()
            except Exception: pass
            if self._tunnel: await self._tunnel.stop(); self._tunnel=None

    async def _tab(self, context, profile, tab_idx):
        tag  = f"[W{self.wid}][T{tab_idx+1}]"
        page = None
        t0   = time.time()
        src  = self.proj.traffic_source
        url  = self.proj.url
        try:
            page = await context.new_page()

            # ── Auto-close popups/dialogs only ────────────
            page.on("dialog", lambda d: asyncio.create_task(d.dismiss()))

            if src == "direct":
                await page.goto(url, timeout=40000, wait_until="domcontentloaded")

            elif src == "organic":
                # Use user keyword or random query
                kw     = self.proj.keyword.strip() if self.proj.keyword.strip() else random.choice(ORGANIC_QUERIES)
                engine = random.choice(ORGANIC_ENGINES)
                search_url = f"{engine}{kw.replace(' ','+')}"
                try:
                    await page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(1.2, 2.5))
                except Exception: pass
                await page.goto(url, timeout=40000, wait_until="domcontentloaded", referer=search_url)

            else:
                # Social: resolve platform
                platform = src if src != "all_social" else random.choice(list(SOCIAL_REFERERS.keys()))
                social_ref = random.choice(SOCIAL_REFERERS.get(platform, SOCIAL_REFERERS["facebook"]))
                # Append ?source=platform to URL
                target_url = f"{url}{'&' if '?' in url else '?'}source={platform}"
                try:
                    await page.goto(social_ref, timeout=18000, wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(0.8, 2.0))
                except Exception: pass
                await page.goto(target_url, timeout=40000, wait_until="domcontentloaded", referer=social_ref)
                url = target_url

            speed_ms = int((time.time()-t0)*1000)
            stay     = random.uniform(self.proj.stay_min, self.proj.stay_max)

            # ── Close cookie banners / popups ─────────────
            await _close_popups(page)

            LOG.emit(
                f"{tag}[{src}][{profile['browser']}/{profile['device'].split()[1]}] ✓  "
                f"{url}  speed={speed_ms}ms  scroll={stay:.0f}s","HIT")

            # Fire visit callback for live table + chart
            elapsed = time.time()-t0
            if self.visit_cb:
                self.visit_cb(profile["device"],profile["browser"],url,src,elapsed)

            await self._scroll(page,stay)
            self.counter["done"]+=1; self.counter["hits"]+=1
            # Reset consecutive error count for this proxy on success
            if self.proxy_raw and "proxy_errors" in self.counter:
                self.counter["proxy_errors"].pop(self.proxy_raw, None)

        except Exception as exc:
            self.counter["errors"]+=1
            err=str(exc)
            # Only count as proxy error if it's actually a proxy/connection issue
            # Website timeouts should NOT expire the proxy
            is_proxy_err = any(k in err for k in [
                "SOCKS","proxy","refused","tunnel",
                "ERR_PROXY","ERR_SOCKS","ERR_CONNECTION_REFUSED"
            ])
            if self.proxy_raw and is_proxy_err:
                pe=self.counter.setdefault("proxy_errors",{})
                pe[self.proxy_raw]=pe.get(self.proxy_raw,0)+1
            if "Timeout" in err or "timeout" in err:
                px_id=self.proxy_raw.split(":")[-2] if self.proxy_raw else "direct"
                LOG.emit(f"{tag} ⏱ TIMEOUT 40s — website slow  ({px_id})","WARN")
            elif is_proxy_err:
                LOG.emit(f"{tag} PROXY ERR: {err[:60]}","ERROR")
            else:
                LOG.emit(f"{tag} {err[:70]}","ERROR")
        finally:
            try:
                if page: await page.close()
            except Exception: pass

    async def _scroll(self, page, duration):
        try:
            th=await page.evaluate("document.body.scrollHeight")
            vh=await page.evaluate("window.innerHeight")
            sc=max(0,th-vh)
            if sc<=0: await asyncio.sleep(duration); return
            end=time.time()+duration; n=random.randint(6,16)
            ts=(duration*0.72)/n
            for i in range(n):
                if self.stop.is_set() or time.time()>=end: break
                tgt=max(0,min(sc,int(sc*(i+1)/n)+random.randint(-20,20)))
                await page.evaluate(f"window.scrollTo({{top:{tgt},behavior:'smooth'}})")
                await asyncio.sleep(min(ts*random.uniform(0.6,1.5),end-time.time()))
            rem=end-time.time()
            if rem>0.5 and not self.stop.is_set():
                await asyncio.sleep(min(random.uniform(0.8,2.0),rem))
            rem=end-time.time()
            if rem>0.5 and not self.stop.is_set():
                nu=random.randint(3,7)
                for i in range(nu):
                    if self.stop.is_set(): break
                    await page.evaluate(f"window.scrollTo({{top:{int(sc*(1-(i+1)/nu))},behavior:'smooth'}})")
                    await asyncio.sleep(rem/nu*random.uniform(0.8,1.2))
            await page.evaluate("window.scrollTo({top:0,behavior:'smooth'})")
            await asyncio.sleep(0.3)
        except Exception: pass

# ═══════════════════════════════════════════════════════
#  ENGINE + THREAD
# ═══════════════════════════════════════════════════════
class Engine:
    def __init__(self, proj: ProjectConfig, counter, visit_cb):
        self._dead = set()   # ← instance variable — resets every new run
        self.proj=proj; self.counter=counter; self.visit_cb=visit_cb
        self._stop=asyncio.Event()
    def stop(self): self._stop.set()

    async def run(self):
        from playwright.async_api import async_playwright
        proj=self.proj; total=proj.impressions
        proxies=list(proj.socks_list) if proj.socks_list else [None]
        working=list(proxies)
        LOG.emit(f"Engine starting — {proj.name}  impressions={total}  workers={proj.workers}  "
                 f"tabs={proj.tabs}  source={proj.traffic_source}","SYS")
        async with async_playwright() as pw:
            launch_args = ["--no-sandbox","--disable-setuid-sandbox",
                           "--disable-blink-features=AutomationControlled",
                           "--disable-infobars","--disable-extensions",
                           "--disable-web-security","--disable-features=IsolateOrigins",
                           "--disable-dev-shm-usage"]
            try: browser=await pw.chromium.launch(headless=proj.headless, args=launch_args)
            except Exception as exc: LOG.emit(f"Browser failed: {exc}","ERROR"); return
            LOG.emit("Browser ready ✓","OK")
            sem=asyncio.Semaphore(proj.workers)

            async def run_one(wid, px):
                async with sem:
                    if self._stop.is_set(): return
                    # Skip already-dead proxy immediately
                    if px and px in self._dead:
                        return
                    w=ImpressionWorker(wid,proj,px,self._stop,self.counter,self.visit_cb)
                    await w.run(browser)
                    if px and px not in self._dead:
                        errs=self.counter.get("proxy_errors",{}).get(px,0)
                        # Mark dead after just 3 consecutive failures (faster detection)
                        if errs>=3:
                            self._dead.add(px); info=parse_proxy(px)
                            tag=f"{info['host']}:{info['port']}" if info else px[:30]
                            LOG.emit(f"⚠ PROXY DEAD: {tag} ({errs} consecutive fails) — removed from pool","EXPIRE")
                            if px in working: working.remove(px)
                            remaining=[p for p in working if p and p not in self._dead]
                            LOG.emit(f"   Active proxies remaining: {len(remaining)}","SYS")
                            if not remaining:
                                LOG.emit("🛑 ALL PROXIES EXPIRED — stopping automatically!","ERROR")
                                self._stop.set(); return
                    await asyncio.sleep(random.uniform(0.5,1.5))

            tasks=[]; wid=0; px_idx=0
            while not self._stop.is_set() and self.counter["done"]<total:
                px = working[px_idx%len(working)] if (working and working[0]) else None
                px_idx+=1
                tasks.append(asyncio.create_task(run_one(wid+1,px)))
                wid+=1; await asyncio.sleep(0.1)

            stop_task=asyncio.create_task(self._stop.wait())
            await asyncio.wait(tasks+[stop_task],return_when=asyncio.FIRST_COMPLETED)
            for t in tasks:
                if not t.done(): t.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
            try: await browser.close()
            except Exception: pass

        done=self.counter["done"]; hits=self.counter["hits"]
        if self._stop.is_set() and done<total:
            LOG.emit(f"⛔ Stopped — delivered={hits}  remaining={total-done}","ERROR")
        else:
            LOG.emit(f"✓ Complete — hits={hits}  errors={self.counter['errors']}","OK")


class EngineThread(QThread):
    done_sig   = pyqtSignal()
    visit_sig  = pyqtSignal(str,str,str,str,float)  # device,browser,url,source,elapsed

    def __init__(self, proj: ProjectConfig, counter):
        super().__init__()
        self.proj=proj; self.counter=counter; self._engine=None

    def run(self):
        loop=asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        self.counter["proxy_errors"]={}

        def _visit_cb(device,browser,url,source,elapsed):
            self.visit_sig.emit(device,browser,url,source,elapsed)

        self._engine=Engine(self.proj,self.counter,_visit_cb)
        try: loop.run_until_complete(self._engine.run())
        except Exception as exc: LOG.emit(f"Engine error: {exc}","ERROR")
        finally:
            # Cancel any remaining tasks before closing loop
            try:
                pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
                if pending:
                    for t in pending: t.cancel()
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception: pass
            loop.close(); self.done_sig.emit()

    def stop(self):
        if self._engine: self._engine.stop()

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def hline(col=None):
    f=QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background:{col or BOR}; border:none;"); return f

def stat_chip(label, val="0", col=None):
    col=col or PRP2
    w=QWidget(); w.setObjectName("card")
    vl=QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(3)
    v=QLabel(val); v.setObjectName("statBig"); v.setStyleSheet(f"color:{col};font-size:32px;font-weight:900;")
    l=QLabel(label); l.setObjectName("statSmall")
    vl.addWidget(v); vl.addWidget(l); return w, v

# ═══════════════════════════════════════════════════════
#  PANEL: PROJECTS LIST
# ═══════════════════════════════════════════════════════
class ProjectsPanel(QWidget):
    run_sig  = pyqtSignal(str)   # project_id
    edit_sig = pyqtSignal(str)

    COLS = ["Project Name","URL","Source","Workers","Tabs","Impressions","Created","Actions"]

    def __init__(self, store: Store):
        super().__init__()
        self.store=store
        lay=QVBoxLayout(self); lay.setContentsMargins(28,24,28,24); lay.setSpacing(16)

        hdr=QHBoxLayout()
        title=QLabel("Projects"); title.setObjectName("pageTitle")
        sub=QLabel("Create and manage your traffic projects")
        sub.setObjectName("pageSub")
        tc=QVBoxLayout(); tc.setSpacing(2); tc.addWidget(title); tc.addWidget(sub)
        hdr.addLayout(tc); hdr.addStretch()
        new_btn=QPushButton("+ Create Project"); new_btn.setObjectName("primaryBtn")
        new_btn.clicked.connect(self._new)
        hdr.addWidget(new_btn); lay.addLayout(hdr); lay.addWidget(hline())

        self.table=QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for i in [2,3,4,5,6]: self.table.horizontalHeader().setSectionResizeMode(i,QHeaderView.ResizeToContents)
        # Actions column — fixed wide enough for 3 buttons
        self.table.horizontalHeader().setSectionResizeMode(7,QHeaderView.Fixed)
        self.table.setColumnWidth(7, 142)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        lay.addWidget(self.table,1)
        self.refresh()

    def refresh(self):
        projs=self.store.all()
        self.table.setRowCount(len(projs))
        for row,p in enumerate(projs):
            self.table.setRowHeight(row,54)
            def c(text,col=TX2,bold=False):
                item=QTableWidgetItem(str(text))
                item.setForeground(QColor(col))
                if bold: f=QFont(); f.setBold(True); item.setFont(f)
                return item

            src_cols={"direct":TX2,"organic":GRNS,"all_social":PRP2,"facebook":"#60a5fa",
                      "instagram":"#f472b6","twitter":"#38bdf8","pinterest":RED2,"youtube":RED2}

            self.table.setItem(row,0,c(p.name,TXT,True))
            self.table.setItem(row,1,c(p.url[:45]+("…" if len(p.url)>45 else ""),CYN2))
            self.table.setItem(row,2,c(p.traffic_source,src_cols.get(p.traffic_source,TX2)))
            self.table.setItem(row,3,c(str(p.workers)))
            self.table.setItem(row,4,c(str(p.tabs)))
            self.table.setItem(row,5,c(str(p.impressions),PRP2))
            self.table.setItem(row,6,c(p.created,TX3))

            # Actions — all three as equal 38x34 icon buttons
            pid=p.id; aw=QWidget(); aw.setStyleSheet("background:transparent;")
            al=QHBoxLayout(aw); al.setContentsMargins(8,6,8,6); al.setSpacing(6)

            run_btn=QPushButton("▶")
            run_btn.setToolTip("Run this project")
            run_btn.setStyleSheet(f"""
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PURP},stop:1 {PINK});
                color:#fff;border:none;border-radius:7px;
                font-size:14px;font-weight:bold;
            """)
            run_btn.setFixedSize(38,34)
            run_btn.clicked.connect(lambda _,i=pid: self.run_sig.emit(i))

            edit_btn=QPushButton("✎")
            edit_btn.setToolTip("Edit this project")
            edit_btn.setStyleSheet(f"""
                background:{SUR2};color:{TX2};border:1px solid {BOR2};
                border-radius:7px;font-size:14px;
            """)
            edit_btn.setFixedSize(38,34)
            edit_btn.clicked.connect(lambda _,i=pid: self.edit_sig.emit(i))

            del_btn=QPushButton("✕")
            del_btn.setToolTip("Delete this project")
            del_btn.setStyleSheet(f"""
                background:{RED}15;color:{RED2};border:1px solid {RED}33;
                border-radius:7px;font-size:13px;font-weight:bold;
            """)
            del_btn.setFixedSize(38,34)
            del_btn.clicked.connect(lambda _,i=pid: self._delete(i))

            al.addWidget(run_btn); al.addWidget(edit_btn); al.addWidget(del_btn)
            self.table.setCellWidget(row,7,aw)

    def _new(self):
        dlg=ProjectDialog(self)
        if dlg.exec_()==QDialog.Accepted:
            p=dlg.result(); self.store.add(p)
            LOG.emit(f"Project created: {p.name}","OK"); self.refresh()

    def _delete(self,pid):
        p=self.store.projects.get(pid)
        if not p: return
        if QMessageBox.question(self,"Delete",f"Delete '{p.name}'?",
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.store.delete(pid); LOG.emit(f"Project deleted: {p.name}","WARN"); self.refresh()

# ═══════════════════════════════════════════════════════
#  PANEL: DASHBOARD (run view)
# ═══════════════════════════════════════════════════════
class DashboardPanel(QWidget):
    back_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build()
        self._thread: Optional[EngineThread] = None
        self._counter={"done":0,"hits":0,"errors":0,"active":0}
        self._target=0
        self._start_time=0.0

        self._tick_timer=QTimer()
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(800)

    def _build(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(28,24,28,24); lay.setSpacing(16)

        # Header
        hdr=QHBoxLayout()
        self.proj_lbl=QLabel("Dashboard"); self.proj_lbl.setObjectName("pageTitle")
        self.proj_sub=QLabel(""); self.proj_sub.setObjectName("pageSub")
        tc=QVBoxLayout(); tc.setSpacing(2); tc.addWidget(self.proj_lbl); tc.addWidget(self.proj_sub)
        hdr.addLayout(tc); hdr.addStretch()
        back_btn=QPushButton("← Projects"); back_btn.setObjectName("ghostBtn")
        back_btn.clicked.connect(self.back_sig)
        hdr.addWidget(back_btn); lay.addLayout(hdr); lay.addWidget(hline())

        # Stat row
        sr=QHBoxLayout(); sr.setSpacing(12)
        self.s_done,  self.v_done   = stat_chip("Page Visits","0",PRP2)
        self.s_tgt,   self.v_tgt    = stat_chip("Target","—",TX2)
        self.s_active,self.v_active = stat_chip("Active Workers","0",GRNS)
        self.s_err,   self.v_err    = stat_chip("Errors","0",RED)
        for w in [self.s_done,self.s_tgt,self.s_active,self.s_err]: sr.addWidget(w)
        sr.addStretch(); lay.addLayout(sr)

        # Progress
        self.prog=QProgressBar(); self.prog.setValue(0)
        self.pct_lbl=QLabel("0%  —  waiting to start")
        self.pct_lbl.setStyleSheet(f"color:{TX3};font-size:12px;")
        lay.addWidget(self.prog); lay.addWidget(self.pct_lbl)

        # Control buttons (prominent)
        br=QHBoxLayout(); br.setSpacing(14)
        self.start_btn=QPushButton("▶  START  —  Deliver Impressions")
        self.start_btn.setObjectName("startBtn"); self.start_btn.setMinimumWidth(300)
        self.start_btn.clicked.connect(self._start)
        self.stop_btn=QPushButton("■  STOP")
        self.stop_btn.setObjectName("stopBtn"); self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumWidth(160)
        self.stop_btn.clicked.connect(self._stop)
        br.addWidget(self.start_btn); br.addWidget(self.stop_btn); br.addStretch()
        lay.addLayout(br)

        # Splitter: visits + chart | log
        split=QSplitter(Qt.Vertical)

        # Top: visits table + chart side by side
        top_w=QWidget(); top_w.setStyleSheet("background:transparent;")
        tl=QHBoxLayout(top_w); tl.setContentsMargins(0,0,0,0); tl.setSpacing(14)

        # Visits table
        vt_card=QWidget()
        vt_card.setStyleSheet(f"background:{SURF};border:1px solid {BOR};border-radius:12px;")
        vt_lay=QVBoxLayout(vt_card); vt_lay.setContentsMargins(0,0,0,0); vt_lay.setSpacing(0)
        vt_hdr=QWidget()
        vt_hdr.setStyleSheet(f"background:{SUR2};border-radius:12px 12px 0 0;")
        vh_l=QHBoxLayout(vt_hdr); vh_l.setContentsMargins(14,8,14,8)
        vt_title=QLabel("RECENT PAGE VISITS")
        vt_title.setStyleSheet(f"font-size:11px;font-weight:700;color:{TX2};letter-spacing:1px;background:transparent;")
        vh_l.addWidget(vt_title); vh_l.addStretch()
        clr_btn=QPushButton("Clear"); clr_btn.setObjectName("ghostBtn")
        clr_btn.setFixedHeight(24); clr_btn.setFixedWidth(52)
        clr_btn.setStyleSheet(f"background:transparent;color:{TX3};border:1px solid {BOR};border-radius:5px;font-size:11px;padding:0;")
        vh_l.addWidget(clr_btn)
        vt_lay.addWidget(vt_hdr)
        self.visit_table=VisitTable()
        self.visit_table.setStyleSheet("background:transparent;")
        clr_btn.clicked.connect(self.visit_table.clear)
        vt_lay.addWidget(self.visit_table,1)
        tl.addWidget(vt_card,3)

        # Right: chart
        chart_col=QVBoxLayout(); chart_col.setSpacing(10)
        chart_card=QWidget()
        chart_card.setStyleSheet(f"background:{SURF};border:1px solid {BOR};border-radius:12px;")
        cc_lay=QVBoxLayout(chart_card); cc_lay.setContentsMargins(14,10,14,10); cc_lay.setSpacing(6)
        ch_lbl=QLabel("TRAFFIC DYNAMICS")
        ch_lbl.setStyleSheet(f"font-size:11px;font-weight:700;color:{TX2};letter-spacing:1px;background:transparent;")
        cc_lay.addWidget(ch_lbl)
        self.chart=TrafficChart()
        self.chart.setStyleSheet("background:transparent;")
        cc_lay.addWidget(self.chart,1)
        chart_col.addWidget(chart_card,1)
        tl.addLayout(chart_col,2)
        split.addWidget(top_w)

        # Log
        log_card=QWidget()
        log_card.setStyleSheet(f"background:{SURF};border:1px solid {BOR};border-radius:12px;")
        ll=QVBoxLayout(log_card); ll.setContentsMargins(0,0,0,0); ll.setSpacing(0)
        log_hdr=QWidget()
        log_hdr.setStyleSheet(f"background:{SUR2};border-radius:12px 12px 0 0;")
        lh_l=QHBoxLayout(log_hdr); lh_l.setContentsMargins(14,8,14,8)
        log_title=QLabel("ACTIVITY LOG")
        log_title.setStyleSheet(f"font-size:11px;font-weight:700;color:{TX2};letter-spacing:1px;background:transparent;")
        lh_l.addWidget(log_title); lh_l.addStretch()
        clr_log=QPushButton("Clear"); clr_log.setFixedHeight(24); clr_log.setFixedWidth(52)
        clr_log.setStyleSheet(f"background:transparent;color:{TX3};border:1px solid {BOR};border-radius:5px;font-size:11px;padding:0;")
        lh_l.addWidget(clr_log)
        ll.addWidget(log_hdr)
        self.log_box=QTextEdit(); self.log_box.setObjectName("logBox"); self.log_box.setReadOnly(True)
        clr_log.clicked.connect(self.log_box.clear)
        ll.addWidget(self.log_box,1)
        split.addWidget(log_card)
        split.setSizes([350,200])
        lay.addWidget(split,1)

    def load_project(self, proj: ProjectConfig):
        self._proj=proj
        self.proj_lbl.setText(f"▶  {proj.name}")
        src_icon = {"direct":"🔗","organic":"🔍","all_social":"📱",
                    "facebook":"📘","instagram":"📸","twitter":"🐦",
                    "pinterest":"📌","youtube":"▶"}.get(proj.traffic_source,"")
        self.proj_sub.setText(
            f"{proj.url}  ·  {src_icon} {proj.traffic_source}  ·  "
            f"{proj.impressions:,} impressions  ·  {proj.workers} workers × {proj.tabs} tabs  ·  "
            f"{len(proj.socks_list)} SOCKS")
        self._counter={"done":0,"hits":0,"errors":0,"active":0}
        self._target=proj.impressions
        self.visit_table.clear()
        self.chart.reset()
        self.chart.set_target(proj.impressions)   # wire target to chart progress bar
        self.v_done.setText("0"); self.v_tgt.setText(f"{proj.impressions:,}")
        self.v_active.setText("0"); self.v_err.setText("0")
        self.prog.setMaximum(proj.impressions); self.prog.setValue(0)
        self.pct_lbl.setText(
            f"0%  —  ready to start  ·  target: {proj.impressions:,} impressions  ·  "
            f"{proj.workers} workers × {proj.tabs} tabs")

    def append_log(self, html):
        self.log_box.append(html); self.log_box.moveCursor(QTextCursor.End)

    def _on_visit(self, device, browser, url, source, elapsed):
        self.visit_table.add_visit(device, browser, url, source, elapsed)
        self.chart.add_hit(1)   # one hit per successful tab visit

    def _tick(self):
        if self._target:
            done=self._counter["done"]; tgt=self._target
            active=self._counter["active"]; err=self._counter["errors"]
            self.v_done.setText(f"{done:,}")
            self.v_tgt.setText(f"{tgt:,}")
            self.v_active.setText(str(active))
            self.v_err.setText(str(err))
            pct=min(100,int(done/tgt*100)) if tgt else 0
            self.prog.setValue(done)
            elapsed=""
            if self._start_time and done>0:
                secs=int(time.time()-self._start_time)
                rate=done/max(secs,1)*60
                eta_s=int((tgt-done)/max(done/max(secs,1),0.01)) if done<tgt else 0
                elapsed=(f"  ·  {secs//60}m{secs%60}s elapsed  ·  "
                         f"~{rate:.0f}/min  ·  ETA {eta_s//60}m{eta_s%60}s")
            self.pct_lbl.setText(f"{pct}%  —  {done:,} / {tgt:,} impressions{elapsed}")
            col=GRNS if pct>=100 else PRP2
            bold="bold" if pct>=100 else "normal"
            self.pct_lbl.setStyleSheet(f"color:{col};font-size:12px;font-weight:{bold};")

    def _start(self):
        if not hasattr(self,"_proj"): return
        # Full reset for re-run
        self._counter={"done":0,"hits":0,"errors":0,"active":0,"proxy_errors":{}}
        self._start_time=time.time()
        self.chart.reset()
        self.chart.set_target(self._proj.impressions)
        self.visit_table.clear()
        self.prog.setValue(0)
        self.v_done.setText("0"); self.v_err.setText("0"); self.v_active.setText("0")
        self.pct_lbl.setText(f"0%  —  starting…  target: {self._proj.impressions:,} impressions")
        self._thread=EngineThread(self._proj,self._counter)
        self._thread.done_sig.connect(self._on_done)
        self._thread.visit_sig.connect(self._on_visit)
        LOG.sig.connect(self.append_log)
        self._thread.start()
        self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True)
        LOG.emit(f"Started: {self._proj.name}","OK")

    def _stop(self):
        if self._thread and self._thread.isRunning():
            self._thread.stop(); LOG.emit("Stop signal sent…","WARN")

    def _on_done(self):
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)
        try: LOG.sig.disconnect(self.append_log)
        except Exception: pass
        self._tick()

    def stop_running(self):
        if self._thread and self._thread.isRunning():
            self._thread.stop(); self._thread.wait(3000)

# ═══════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    NAV=[("📊","Projects",0),("▶","Dashboard",1)]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrafficForge v4.0")
        self.setMinimumSize(1100,700); self.resize(1300,800)
        self.store=Store(); self._nav_btns=[]
        self._build()
        LOG.emit("TrafficForge v4.0 ready — Create a project to start","SYS")
        self._check_deps()

    def _check_deps(self):
        missing=[]
        try: import playwright
        except ImportError: missing.append("playwright")
        try: import socks
        except ImportError: missing.append("PySocks")
        if missing:
            LOG.emit(f"⚠ Missing: {', '.join(missing)} → pip install {' '.join(missing)}","WARN")
        else:
            LOG.emit(f"✓ All deps OK  ·  {len(UA_GROUPS['Random (All)'])} user-agents loaded","OK")

    def _build(self):
        root=QWidget(); root.setStyleSheet(f"background:{BG};")
        rl=QHBoxLayout(root); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
        self.setCentralWidget(root)

        # ── SIDEBAR ──────────────────────────────────────
        sb=QWidget(); sb.setObjectName("sidebar")
        sl=QVBoxLayout(sb); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)

        # Logo
        logo=QWidget(); logo.setObjectName("logoWrap"); logo.setFixedHeight(72)
        ll=QHBoxLayout(logo); ll.setContentsMargins(18,0,18,0); ll.setSpacing(12)
        ico=QLabel("⚡"); ico.setStyleSheet(f"font-size:26px;color:{PRP2};font-weight:bold;")
        nc=QVBoxLayout(); nc.setSpacing(1)
        n1=QLabel("TrafficForge"); n1.setStyleSheet(f"font-size:16px;font-weight:900;color:{TXT};")
        n2=QLabel("v4.0  ·  Project Suite"); n2.setStyleSheet(f"font-size:10px;color:{TX3};")
        nc.addWidget(n1); nc.addWidget(n2); ll.addWidget(ico); ll.addLayout(nc)
        sl.addWidget(logo); sl.addWidget(hline())

        sep=QLabel("NAVIGATION")
        sep.setStyleSheet(f"color:{TX3};font-size:9px;font-weight:bold;letter-spacing:2px;padding:14px 18px 6px 18px;")
        sl.addWidget(sep)

        for icon,label,idx in self.NAV:
            btn=QPushButton(f"  {icon}   {label}")
            btn.setObjectName("navBtn"); btn.setFlat(True)
            btn.clicked.connect(lambda _,i=idx: self._switch(i))
            sl.addWidget(btn); self._nav_btns.append(btn)

        sl.addStretch()
        self._status_lbl=QLabel("● Idle")
        self._status_lbl.setStyleSheet(f"color:{TX3};font-size:11px;padding:8px 18px;")
        sl.addWidget(self._status_lbl)
        ver=QLabel("For testing use only")
        ver.setStyleSheet(f"color:{TX3};font-size:9px;padding:0 18px 14px 18px;")
        sl.addWidget(ver); rl.addWidget(sb)

        # ── STACK ─────────────────────────────────────────
        scroll=QScrollArea(); scroll.setObjectName("mainArea")
        scroll.setWidgetResizable(True); scroll.setStyleSheet(f"background:{BG};border:none;")
        self.stack=QStackedWidget(); self.stack.setStyleSheet(f"background:{BG};")

        self.projects_panel=ProjectsPanel(self.store)
        self.dash_panel=DashboardPanel()
        for p in [self.projects_panel,self.dash_panel]: self.stack.addWidget(p)

        scroll.setWidget(self.stack); rl.addWidget(scroll,1)

        # Connect
        self.projects_panel.run_sig.connect(self._run_project)
        self.projects_panel.edit_sig.connect(self._edit_project)
        self.dash_panel.back_sig.connect(lambda: self._switch(0))
        LOG.sig.connect(lambda html: None)   # prevent crash before dashboard connect
        self._switch(0)

    def _switch(self,idx):
        self.stack.setCurrentIndex(idx)
        for i,btn in enumerate(self._nav_btns):
            btn.setProperty("active","true" if i==idx else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

    def _run_project(self, pid):
        p=self.store.projects.get(pid)
        if not p: return
        self.dash_panel.load_project(p)
        self._switch(1)
        self._status_lbl.setText(f"● {p.name}")
        self._status_lbl.setStyleSheet(f"color:{GRNS};font-size:11px;font-weight:bold;padding:8px 18px;")

    def _edit_project(self, pid):
        p=self.store.projects.get(pid)
        if not p: return
        dlg=ProjectDialog(self,p)
        if dlg.exec_()==QDialog.Accepted:
            updated=dlg.result()
            self.store.update(updated)
            LOG.emit(f"Project updated: {updated.name}  ·  {len(updated.socks_list)} SOCKS  ·  "
                     f"{updated.impressions} impressions","OK")
            self.projects_panel.refresh()

    def _run_project_confirm(self, pid):
        """Run project — load into dashboard and switch."""
        self._run_project(pid)
        # Auto-start is intentionally NOT done here — user clicks START in dashboard

    def closeEvent(self,event):
        self.dash_panel.stop_running()
        self.store.save(); event.accept()


# ═══════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════
def main():
    app=QApplication(sys.argv)
    app.setApplicationName("TrafficForge v4.0")
    app.setStyleSheet(QSS)
    app.setFont(QFont("Segoe UI",10))
    win=MainWindow(); win.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
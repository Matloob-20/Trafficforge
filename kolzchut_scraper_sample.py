"""
Bituach Leumi Full Rights Scraper v7 — All 16 fields, CSV + JSON
=================================================================
INSTALL:  pip install requests beautifulsoup4
RUN:      python btl_scraper_v7.py
Output:   rights.csv  +  rights.json  (same directory)
"""

import csv, json, re, time, logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import Counter
import requests
from bs4 import BeautifulSoup

# ── Config ───────────────────────────────────────────────────────────────────

BASE_URL    = "https://www.btl.gov.il"
DELAY       = 1.5          # seconds between requests — polite but fast
OUTPUT_CSV  = Path("rights.csv")
OUTPUT_JSON = Path("rights.json")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Referer":         "https://www.btl.gov.il/",
}

# ── All verified sections ────────────────────────────────────────────────────

SECTIONS = [
    ("נכות כללית",              "General Disability",        "/benefits/Disability/Pages/default.aspx"),
    ("נפגעי עבודה",             "Work Injury",               "/benefits/Work_Injury/Pages/default.aspx"),
    ("אזרח ותיק",               "Old Age Pension",           "/benefits/old_age/Pages/default.aspx"),
    ("לידה ואימהות",            "Maternity",                 "/benefits/Maternity/Pages/default.aspx"),
    ("ילד נכה",                 "Disabled Child",            "/benefits/Disabled_Child/Pages/default.aspx"),
    ("שיקום מקצועי",            "Vocational Rehabilitation", "/benefits/Vocational_Rehabilitation/Pages/default.aspx"),
    ("נפגעי פעולות איבה",       "Hostility Victims",         "/benefits/Victims_of_Hostilities/Pages/default.aspx"),
    ("אבטלה",                   "Unemployment",              "/benefits/unemployment/Pages/default.aspx"),
    ("שירותים מיוחדים לנכים",  "Special Disability Svcs",  "/benefits/Attendance_Allowance/Pages/default.aspx"),
    ("נפגעי תאונות",            "Accident Victims",          "/benefits/accident_victims/Pages/default.aspx"),
    ("הבטחת הכנסה",             "Income Support",            "/benefits/Incomeassurance/Pages/default.aspx"),
    ("מילואים",                 "Military Reserve",          "/benefits/Miluim/Pages/default.aspx"),
    ("קצבת ילדים",              "Child Allowance",           "/benefits/ChildrenAllowance/Pages/default.aspx"),
    ("מזונות",                  "Alimony",                   "/benefits/Alimony/Pages/default.aspx"),
    ("זכויות בפשיטת רגל",      "Bankruptcy Rights",         "/benefits/Bankruptcy/Pages/default.aspx"),
    ("ניידות",                  "Mobility",                  "/benefits/Mobility/Pages/default.aspx"),
    ("נפגעי פוליו",             "Polio Victims",             "/benefits/Polio/Pages/default.aspx"),
    ("פגיעה בהתנדבות",          "Volunteer Injury",          "/benefits/Volunteering/Pages/default.aspx"),
    ("אסירי ציון",              "Zion Prisoners",            "/benefits/ZionPrisoners/Pages/default.aspx"),
    ("שאירים",                  "Survivors",                 "/benefits/Survivors/Pages/default.aspx"),
    ("גמלת סיעוד",              "Nursing Care",              "/benefits/nursingcare/Pages/default.aspx"),
]

# CSV flat columns (JSON has the full nested structure)
CSV_COLS = [
    "right_id", "title_he", "category_he", "category_en",
    "summary",
    "eligibility",           # pipe-separated list
    "amount_full",           # main benefit amount in ₪
    "amount_with_spouse",    # with spouse supplement
    "amount_updated",        # date amounts were updated
    "how_to_apply",          # pipe-separated steps
    "required_documents",    # pipe-separated list
    "process_steps",         # pipe-separated steps
    "processing_time",
    "fast_track",            # pipe-separated conditions
    "related_benefits",      # pipe-separated
    "related_forms",         # pipe-separated "number:description"
    "contact_phone",
    "applies_to_conditions", # pipe-separated medical conditions
    "source_url",
    "last_verified",
]

SKIP_PATTERNS = [
    "/_layouts/", "/PublishingImages/", "/SiteCollectionImages/",
    "tfassim", "HozrimGimlaot", "Publications", "sitemap",
    "login", "logout", "contact_us", "newspapers",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("btl_v7")

sess = requests.Session()
sess.headers.update(HEADERS)
visited: set[str] = set()


# ── HTTP ──────────────────────────────────────────────────────────────────────

def fetch(url: str) -> BeautifulSoup | None:
    if url in visited:
        return None
    visited.add(url)
    time.sleep(DELAY)
    try:
        r = sess.get(url, timeout=25)
        log.info(f"  {r.status_code}  {url}")
        if r.status_code in (403, 404, 500):
            return None
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        log.error(f"  Error: {e}")
        return None


# ── Content zone ──────────────────────────────────────────────────────────────

def content_zone(soup: BeautifulSoup):
    for sel in [
        ".ms-rtestate-field",
        "#ctl00_PlaceHolderMain_ctl00__ControlWrapper_RichHtmlField",
        ".ms-WPBody", "#DeltaPlaceHolderMain", "article", "main",
    ]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 80:
            return el
    divs = soup.find_all("div")
    return max(divs, key=lambda d: len(d.get_text(strip=True)), default=None) if divs else None


# ── Field extractors ──────────────────────────────────────────────────────────

def extract_title(soup: BeautifulSoup) -> str:
    for sel in ["h1", ".ms-rtestate-field h2", "h2"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t:
                return t
    t = soup.find("title")
    if t:
        return re.sub(r"\s*[|\-]\s*ביטוח לאומי.*", "", t.get_text(strip=True)).strip()
    return ""


def extract_summary(zone) -> str:
    paras = [p.get_text(" ", strip=True) for p in zone.find_all("p")
             if len(p.get_text(strip=True)) > 40]
    return " ".join(paras[:3])[:700] if paras else zone.get_text(" ", strip=True)[:500]


def extract_eligibility(zone) -> list[str]:
    """Extract structured eligibility conditions."""
    items = []
    text = zone.get_text(" ", strip=True)

    # Look for numbered conditions (תנאי ראשון, תנאי שני, etc.)
    condition_pattern = re.findall(r"תנאי [א-ת]+[:\s]+([^תנאי]{10,200})", text)
    items.extend([c.strip() for c in condition_pattern])

    # Also grab bullet lists
    for ul in zone.find_all(["ul", "ol"]):
        for li in ul.find_all("li"):
            t = li.get_text(" ", strip=True)
            if len(t) > 15 and t not in items:
                items.append(t)

    return items[:12]


def extract_amounts(zone, full_text: str) -> dict:
    """Extract benefit amounts with context."""
    amounts = {}

    # Find ₪ amounts with surrounding context
    pattern = r"([\w\s,א-ת]{5,40}?)([\d,]+)\s*₪"
    matches = re.findall(pattern, full_text)

    # Known keys to look for
    amount_map = {
        "full": ["אי כושר מלא", "100%", "מלאה"],
        "with_spouse": ["בן זוג", "בת זוג", "תוספת"],
        "updated": ["ינואר 2026", "2026", "ינואר 2025"],
    }

    raw_amounts = re.findall(r"([\d,]+)\s*₪", full_text)
    if raw_amounts:
        amounts["all_amounts_nis"] = list(set(raw_amounts))

    # Try to find specific amounts by context
    for label, keywords in amount_map.items():
        for kw in keywords:
            idx = full_text.find(kw)
            if idx != -1:
                nearby = full_text[max(0, idx-30):idx+60]
                found = re.findall(r"([\d,]+)\s*₪", nearby)
                if found and label not in amounts:
                    amounts[label] = found[0].replace(",", "")

    return amounts


def extract_how_to_apply(zone, full_text: str) -> list[str]:
    steps = []
    apply_keywords = ["הגשת תביעה", "הגש", "פנה", "מלא", "שלח", "הצג"]
    for kw in apply_keywords:
        sentences = re.findall(rf"[^.]*{kw}[^.]*\.", full_text)
        steps.extend([s.strip() for s in sentences if len(s.strip()) > 15])
    return list(dict.fromkeys(steps))[:5]


def extract_documents(zone, full_text: str) -> list[str]:
    docs = []
    doc_keywords = ["תעודת זהות", "טופס", "אישור", "מסמך", "תלוש", "צילום"]
    for ul in zone.find_all(["ul", "ol"]):
        for li in ul.find_all("li"):
            t = li.get_text(" ", strip=True)
            if any(kw in t for kw in doc_keywords) and len(t) > 5:
                docs.append(t)
    return docs[:8]


def extract_process_steps(zone, full_text: str) -> list[str]:
    steps = []
    # Look for numbered steps
    numbered = re.findall(r"\d+[.)\s]+([^.\d]{10,150})", full_text)
    steps.extend([s.strip() for s in numbered if len(s.strip()) > 10])

    # Process keywords
    process_kws = ["הגשת תביעה", "ועדה רפואית", "קביעת", "הודעה", "תחילת תשלום"]
    for kw in process_kws:
        if kw in full_text and kw not in " ".join(steps):
            steps.append(kw)

    return list(dict.fromkeys(steps))[:7]


def extract_processing_time(full_text: str) -> str:
    patterns = [
        r"(\d+)\s*ימים?",
        r"(\d+)\s*חודשים?",
        r"מסלול מהיר[^.]{0,80}\.",
        r"זמן טיפול[^.]{0,80}\.",
    ]
    found = []
    for p in patterns:
        m = re.findall(p, full_text)
        if m:
            found.extend(m if isinstance(m[0], str) else [f"{v} ימים" for v in m])
    return " | ".join(dict.fromkeys(found))[:200]


def extract_fast_track(zone, full_text: str) -> list[str]:
    if "מסלול מהיר" not in full_text and "מסלול ירוק" not in full_text:
        return []
    items = []
    for ul in zone.find_all(["ul", "ol"]):
        text_before = ul.find_previous_sibling(text=True) or ""
        header = ul.find_previous(["h2", "h3", "h4", "strong", "b"])
        header_text = header.get_text() if header else ""
        if "מהיר" in header_text or "מהיר" in str(text_before):
            items.extend([li.get_text(" ", strip=True) for li in ul.find_all("li")])
    return items[:8]


def extract_related_benefits(zone) -> list[str]:
    related = []
    for a in zone.find_all("a", href=True):
        if "/benefits/" in a["href"]:
            t = a.get_text(strip=True)
            if t and len(t) > 3 and t not in related:
                related.append(t)
    return related[:8]


def extract_forms(zone, full_text: str) -> list[dict]:
    forms = []
    # Look for form numbers like "טופס 211" or "טופס BL/800"
    form_matches = re.findall(r"טופס\s+([\w/]+)[^א-ת]{0,60}([א-ת][^,.\n]{5,60})?", full_text)
    for num, desc in form_matches:
        forms.append({"number": num.strip(), "description": desc.strip() if desc else ""})
    return forms[:6]


def extract_phone(full_text: str) -> str:
    phones = re.findall(r"\*\d{4}|\d{2,4}-\d{6,8}|1-800-\d+", full_text)
    return phones[0] if phones else "*6050"  # default BTL number


def extract_conditions(full_text: str) -> list[str]:
    condition_keywords = [
        "מחלה", "תאונה", "נכות", "ליקוי", "פגיעה", "מום",
        "סרטן", "סיעוד", "שבץ", "לב", "אורתופד", "נפשי", "שכלי",
    ]
    found = [kw for kw in condition_keywords if kw in full_text]
    return found


# ── Main parser ───────────────────────────────────────────────────────────────

def parse_page(soup: BeautifulSoup, url: str, cat_he: str, cat_en: str) -> dict | None:
    title = extract_title(soup)
    if not title:
        return None

    zone = content_zone(soup)
    if not zone:
        return None

    full_text = zone.get_text(" ", strip=True)
    if len(full_text) < 100:
        return None

    summary      = extract_summary(zone)
    eligibility  = extract_eligibility(zone)
    amounts      = extract_amounts(zone, full_text)
    how_to_apply = extract_how_to_apply(zone, full_text)
    documents    = extract_documents(zone, full_text)
    steps        = extract_process_steps(zone, full_text)
    proc_time    = extract_processing_time(full_text)
    fast_track   = extract_fast_track(zone, full_text)
    related      = extract_related_benefits(zone)
    forms        = extract_forms(zone, full_text)
    phone        = extract_phone(full_text)
    conditions   = extract_conditions(full_text)
    today        = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── Full JSON record (nested, rich) ──────────────────────────────────
    json_record = {
        "right_id":    f"btl_{abs(hash(url)) % 10**8:08d}",
        "title_he":    title,
        "category_he": cat_he,
        "category_en": cat_en,
        "source_url":  url,
        "last_verified": today,

        "summary": summary,
        "eligibility_conditions": eligibility,
        "benefit_amounts": amounts,
        "how_to_apply": how_to_apply,
        "required_documents": documents,
        "process_steps": steps,
        "processing_time": proc_time,
        "fast_track_eligible": fast_track,
        "related_benefits": related,
        "related_forms": forms,
        "contact": {"phone": phone, "website": BASE_URL},
        "applies_to_conditions": conditions,
    }

    # ── Flat CSV record ───────────────────────────────────────────────────
    csv_record = {
        "right_id":              json_record["right_id"],
        "title_he":              title,
        "category_he":           cat_he,
        "category_en":           cat_en,
        "summary":               summary,
        "eligibility":           " | ".join(eligibility),
        "amount_full":           amounts.get("full", ""),
        "amount_with_spouse":    amounts.get("with_spouse", ""),
        "amount_updated":        amounts.get("updated", ""),
        "how_to_apply":          " | ".join(how_to_apply),
        "required_documents":    " | ".join(documents),
        "process_steps":         " | ".join(steps),
        "processing_time":       proc_time,
        "fast_track":            " | ".join(fast_track),
        "related_benefits":      " | ".join(related),
        "related_forms":         " | ".join(f"{f['number']}:{f['description']}" for f in forms),
        "contact_phone":         phone,
        "applies_to_conditions": " | ".join(conditions),
        "source_url":            url,
        "last_verified":         today,
    }

    return {"json": json_record, "csv": csv_record}


# ── Sub-page discovery ────────────────────────────────────────────────────────

def find_sub_pages(soup: BeautifulSoup, base_url: str, section_prefix: str) -> list[str]:
    urls = []
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if not h or h.startswith("#") or h.startswith("javascript") or h.startswith("mailto"):
            continue
        full = urljoin(base_url, h).split("?")[0].split("#")[0]
        p = urlparse(full)
        if (
                "btl.gov.il" in p.netloc
                and section_prefix.lower() in p.path.lower()
                and p.path.endswith(".aspx")
                and full not in visited
                and not any(skip in full for skip in SKIP_PATTERNS)
        ):
            urls.append(full)
    return list(dict.fromkeys(urls))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log.info("=== BTL Full Scraper v7 — 16 fields, CSV + JSON ===")
    log.info(f"Sections: {len(SECTIONS)}")

    json_records = []
    csv_records  = []

    for cat_he, cat_en, index_path in SECTIONS:
        index_url      = BASE_URL + index_path
        section_prefix = index_path.rsplit("/Pages/", 1)[0]

        log.info(f"\n{'─'*55}")
        log.info(f"► {cat_he} ({cat_en})")

        soup = fetch(index_url)
        if not soup:
            continue

        result = parse_page(soup, index_url, cat_he, cat_en)
        if result:
            json_records.append(result["json"])
            csv_records.append(result["csv"])

        # Sub-pages (level 1)
        sub_urls = find_sub_pages(soup, index_url, section_prefix)
        log.info(f"  Sub-pages: {len(sub_urls)}")

        for sub_url in sub_urls:
            sub_soup = fetch(sub_url)
            if not sub_soup:
                continue
            r = parse_page(sub_soup, sub_url, cat_he, cat_en)
            if r:
                json_records.append(r["json"])
                csv_records.append(r["csv"])

            # Sub-sub-pages (level 2)
            deep_urls = find_sub_pages(sub_soup, sub_url, section_prefix)
            for deep_url in deep_urls:
                deep_soup = fetch(deep_url)
                if not deep_soup:
                    continue
                dr = parse_page(deep_soup, deep_url, cat_he, cat_en)
                if dr:
                    json_records.append(dr["json"])
                    csv_records.append(dr["csv"])

    log.info(f"\n{'='*55}")
    log.info(f"TOTAL RECORDS: {len(json_records)}")

    if not json_records:
        log.error("0 records — check HTTP statuses above.")
        return

    # ── Write CSV ─────────────────────────────────────────────────────────
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        w.writerows(csv_records)
    log.info(f"✓ CSV  → {OUTPUT_CSV}  ({len(csv_records)} rows, {len(CSV_COLS)} columns)")

    # ── Write JSON ────────────────────────────────────────────────────────
    OUTPUT_JSON.write_text(
        json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "Bituach Leumi (btl.gov.il) — Israeli Government",
            "license": "Government content — attribute as: המוסד לביטוח לאומי",
            "total": len(json_records),
            "categories": sorted(set(r["category_he"] for r in json_records)),
            "rights": json_records,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"✓ JSON → {OUTPUT_JSON}  ({len(json_records)} records)")

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"{'Category':<35} {'Records':>7}")
    print(f"{'─'*50}")
    for cat, count in Counter(r["category_he"] for r in json_records).most_common():
        print(f"  {cat:<33} {count:>7}")
    print(f"{'─'*50}")
    print(f"  {'TOTAL':<33} {len(json_records):>7}")


if __name__ == "__main__":
    main()
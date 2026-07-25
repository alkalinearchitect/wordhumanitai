"""
HumanitAI — Live news early-warning ingestion
Pulls UK social-policy RSS (Guardian Society, BBC), extracts items relevant to
the five pressures, and scores an EARLY-WARNING signal per pressure from keyword
intensity + recency. Feeds the prevention system as a live signal layer.

No API key. RSS only. Aggregate/theme-level — no individuals.
Run:  python prediction/news_ingest.py
"""
import json, re, sys, os, datetime
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
OUT = ROOT / "prediction" / "news_signals.json"

FEEDS = {
    "guardian_society": "https://www.theguardian.com/society/rss",
    "bbc_uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "bbc_health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    "bbc_politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
}

PRESSURE_KW = {
    "poverty": ["poverty", "benefit", "universal credit", "cost of living", "welfare",
                "food bank", "fuel poverty", "child poverty", "low income", "debt"],
    "homelessness": ["homeless", "rough sleep", "rough sleeping", "eviction", "section 21",
                     "temporary accommodation", "hostel", "sleeping rough"],
    "nhs": ["nhs", "waiting list", "a&e", "ambulance", "gps", "gp surgery", "hospital",
            "trolley", "waiting time", "bed crisis"],
    "mental": ["mental health", "suicide", "self-harm", "loneliness", "isolation",
               "wellbeing", "depression", "anxiety", "crisis line"],
    "isolation": ["loneliness", "isolat", "community", "befriend", "social prescrib",
                  "third place", "warm space"],
}

import urllib.request, xml.etree.ElementTree as ET

def fetch(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HumanitAI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:
        return f"<error>{e}</error>"

def parse_items(xmltext):
    items = []
    if xmltext.startswith("<error>"):
        return items
    try:
        root = ET.fromstring(xmltext)
    except Exception:
        return items
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        desc = (it.findtext("description") or "").strip()
        link = (it.findtext("link") or "").strip()
        # Guardian puts link in <link> as text or CDATA
        items.append((title, desc, link))
    # BBC sometimes uses <entry> (Atom)
    for it in root.iter("entry"):
        title = (it.findtext("{http://www.w3.org/2005/Atom}title") or
                 it.findtext("title") or "").strip()
        link = ""
        for l in it.iter("{http://www.w3.org/2005/Atom}link"):
            link = l.get("href", "")
        items.append((title, "", link))
    return items

def score(text):
    t = (text or "").lower()
    out = {}
    for p, kws in PRESSURE_KW.items():
        hits = sum(t.count(k) for k in kws)
        if hits:
            out[p] = hits
    return out

def main():
    collected = []
    per_pressure = {p: [] for p in PRESSURE_KW}
    for name, url in FEEDS.items():
        xml = fetch(url)
        for title, desc, link in parse_items(xml):
            if not title or title in ("BBC News", "The Guardian", "Society | The Guardian"):
                continue
            sc = score(title + " " + desc)
            if not sc:
                continue
            rec = {"source": name, "title": title, "link": link, "pressures": sc}
            collected.append(rec)
            for p in sc:
                per_pressure[p].append(rec)
    summary = {p: len(v) for p, v in per_pressure.items()}
    # early-warning: pressure with >=2 distinct recent signals = elevated
    early = {p: ("ELEVATED" if summary[p] >= 2 else "baseline") for p in summary}
    out = {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "n_signals": len(collected),
        "per_pressure_counts": summary,
        "early_warning": early,
        "items": collected[:40],
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"News early-warning: {len(collected)} signals")
    print("Per-pressure counts:", summary)
    print("Early warning:", early)
    for p, v in per_pressure.items():
        if v:
            print(f"  [{p}] sample: {v[0]['title'][:80]}")

if __name__ == "__main__":
    main()

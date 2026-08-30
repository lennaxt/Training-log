#!/usr/bin/env python3
"""Legt die Schlagzeilen als news.json neben index.html ab.

GitHub Pages liefert die Datei von derselben Herkunft wie die App aus. Damit
braucht der Browser keinen fremden Dienst anzufragen und laeuft nicht in CORS —
die Feeds selbst erlauben Zugriff von fremden Seiten naemlich nicht.
"""
import json, os, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

FEEDS = {
    "tagesschau": ("Tagesschau", "https://www.tagesschau.de/xml/rss2/"),
    "dlf": ("Deutschlandfunk", "https://www.deutschlandfunk.de/nachrichten-100.rss"),
    "taz": ("taz", "https://taz.de/!p4608;rss/"),
}
PER_FEED = 20
OUT = os.path.join(os.path.dirname(__file__), "..", "news.json")
UA = "Trainingslog-Newsbot/1.0 (+https://github.com/lennaxt/Training-log)"


def clean(s, limit):
    s = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()
    return s[:limit].rstrip() + "…" if len(s) > limit else s


def items(raw):
    out = []
    for it in ET.fromstring(raw).iter("item"):
        title = clean(it.findtext("title"), 140)
        if not title:
            continue
        out.append({"t": title,
                    "s": clean(it.findtext("description"), 320),
                    "u": (it.findtext("link") or "").strip()})
        if len(out) >= PER_FEED:
            break
    return out


def main():
    try:
        with open(OUT, encoding="utf-8") as f:
            prev = json.load(f).get("sources", {})
    except Exception:
        prev = {}

    sources, failed = {}, []
    for key, (name, url) in FEEDS.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                got = items(r.read())
            if not got:
                raise ValueError("Feed geliefert, aber keine Eintraege darin")
            sources[key] = {"name": name, "items": got}
            print(f"{key}: {len(got)} Schlagzeilen")
        except Exception as e:
            failed.append(key)
            print(f"{key} FEHLER: {e}", file=sys.stderr)
            # Eine kaputte Quelle darf die anderen nicht mitreissen: lieber den
            # alten Stand behalten als die Quelle leer ausliefern.
            if key in prev:
                sources[key] = prev[key]
                print(f"{key}: alter Stand behalten ({len(prev[key].get('items', []))})")

    if not any(k not in failed for k in FEEDS):
        print("Keine einzige Quelle erreichbar.", file=sys.stderr)
        return 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "sources": sources}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

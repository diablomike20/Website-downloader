#!/usr/bin/env python3
import csv
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

UA = "OpenCudy-FU7-CDN-Indexer/1.0 (+https://github.com/diablomike20/Website-downloader)"
CDN_PREFIXES = (
    "https://www.cudy.com/cdn/shop/files/",
    "http://www.cudy.com/cdn/shop/files/",
    "https://cudy.com/cdn/shop/files/",
    "http://cudy.com/cdn/shop/files/",
)
URL_RE = re.compile(r'https?://(?:www\.)?cudy\.com/cdn/shop/files/[^"\'<>\s]+', re.I)
REL_RE = re.compile(r'(?:"|\'|\()(/cdn/shop/files/[^"\'<>\s)]+)', re.I)

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers), r.status

def text_fetch(url, timeout=30):
    data, headers, status = fetch(url, timeout)
    return data.decode("utf-8", "replace"), headers, status

def norm_url(url):
    url = url.replace("&amp;", "&").strip()
    while url and url[-1] in ".,;)]}":
        url = url[:-1]
    if url.startswith("/cdn/shop/files/"):
        url = "https://www.cudy.com" + url
    p = urllib.parse.urlsplit(url)
    if p.netloc.lower() in ("cudy.com", "www.cudy.com") and p.path.startswith("/cdn/shop/files/"):
        return urllib.parse.urlunsplit(("https", "www.cudy.com", p.path, p.query, ""))
    return None

def add(found, url, source, seen=None):
    u = norm_url(url)
    if not u:
        return
    rec = found[u]
    rec["sources"].add(source)
    if seen:
        rec["seen"].add(seen)

def extract_urls(found, body, source):
    for m in URL_RE.findall(body):
        add(found, m, source)
    for m in REL_RE.findall(body):
        add(found, m, source)

def parse_sitemap(url):
    try:
        body, _, _ = text_fetch(url)
        root = ET.fromstring(body)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [x.text.strip() for x in root.findall(".//s:loc", ns) if x.text]
        return root.tag, locs
    except Exception as e:
        print("SITEMAP_FAIL", url, repr(e))
        return "", []

def crawl_cudy_site(found):
    tag, roots = parse_sitemap("https://www.cudy.com/sitemap.xml")
    child_sitemaps = roots if tag.endswith("sitemapindex") else []
    pages = roots if tag.endswith("urlset") else []

    for sm in child_sitemaps:
        _, locs = parse_sitemap(sm)
        pages.extend(locs)

    keep = []
    for u in pages:
        lu = u.lower()
        if (
            "/pages/download-center/" in lu
            or "/blogs/" in lu
            or "/pages/download" in lu
            or "/products/" in lu
        ):
            keep.append(u)

    keep = sorted(set(keep))
    print("CUDY_PAGES_SELECTED", len(keep))
    for idx, u in enumerate(keep, 1):
        try:
            body, _, _ = text_fetch(u, 25)
            extract_urls(found, body, "cudy_page:" + u)
        except Exception as e:
            print("PAGE_FAIL", u, repr(e))
        if idx % 50 == 0:
            print("CUDY_PROGRESS", idx, len(keep))
        time.sleep(0.03)

def commoncrawl_indexes():
    body, _, _ = text_fetch("https://index.commoncrawl.org/collinfo.json")
    arr = json.loads(body)
    ids = []
    for x in arr:
        ident = x.get("id", "")
        frm = x.get("from", "")
        if ident.startswith("CC-MAIN-2026-") or ident.startswith("CC-MAIN-2025-"):
            ids.append((ident, frm))
    return ids

def crawl_commoncrawl(found):
    for ident, frm in commoncrawl_indexes():
        base = f"https://index.commoncrawl.org/{ident}-index"
        params = urllib.parse.urlencode({
            "url": "www.cudy.com/cdn/shop/files/*",
            "output": "json",
            "filter": "status:200",
        })
        url = base + "?" + params
        try:
            body, _, _ = text_fetch(url, 90)
        except Exception as e:
            print("CC_FAIL", ident, repr(e))
            continue
        n = 0
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            original = obj.get("url") or obj.get("original")
            if original:
                ts = obj.get("timestamp") or frm or ident
                add(found, original, "commoncrawl:" + ident, "cc:" + str(ts))
                n += 1
        print("CC_INDEX", ident, n)
        time.sleep(0.15)

def crawl_wayback(found):
    params = urllib.parse.urlencode({
        "url": "www.cudy.com/cdn/shop/files/*",
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype,digest",
        "filter": "statuscode:200",
        "collapse": "urlkey",
    })
    url = "https://web.archive.org/cdx/search/cdx?" + params
    try:
        body, _, _ = text_fetch(url, 120)
        rows = json.loads(body)
    except Exception as e:
        print("WAYBACK_FAIL", repr(e))
        return
    if not rows:
        return
    hdr = rows[0]
    for row in rows[1:]:
        obj = dict(zip(hdr, row))
        original = obj.get("original")
        if original:
            add(found, original, "wayback", "wb:" + obj.get("timestamp", ""))
    print("WAYBACK_ROWS", max(0, len(rows) - 1))

def verify_url(url):
    # HEAD first. If Shopify/CDN refuses HEAD, use GET Range.
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.headers.get("Content-Length", ""), r.headers.get("ETag", ""), r.headers.get("Last-Modified", "")
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.headers.get("Content-Range") or r.headers.get("Content-Length", ""), r.headers.get("ETag", ""), r.headers.get("Last-Modified", "")
        except Exception as e:
            code = getattr(e, "code", "")
            return code or "ERR", "", "", ""

def parse_filename(url):
    return urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])

def score_candidate(filename):
    s = filename.lower()
    score = 0
    if "r25" in s: score += 8
    if "lt500d" in s: score += 7
    if "lt500" in s: score += 5
    if "2.5." in s: score += 6
    if "flash" in s: score += 2
    if s.endswith(".zip") or s.endswith(".bin"): score += 2
    return score

def main():
    found = defaultdict(lambda: {"sources": set(), "seen": set()})
    crawl_commoncrawl(found)
    crawl_wayback(found)
    crawl_cudy_site(found)

    rows = []
    for url, rec in found.items():
        fn = parse_filename(url)
        rows.append({
            "url": url,
            "filename": fn,
            "candidate_score": score_candidate(fn),
            "sources": " | ".join(sorted(rec["sources"])),
            "seen": " | ".join(sorted(rec["seen"])),
            "http_status": "",
            "content_length_or_range": "",
            "etag": "",
            "last_modified": "",
        })

    rows.sort(key=lambda r: (-r["candidate_score"], r["filename"].lower(), r["url"]))

    # Verify all firmware-ish discovered objects; never generate candidate names.
    for i, r in enumerate(rows, 1):
        fn = r["filename"].lower()
        firmwareish = (
            "flash" in fn
            or "sysupgrade" in fn
            or fn.endswith(".bin")
            or (fn.endswith(".zip") and any(x in fn for x in ("2.5.", "r25", "lt500")))
        )
        if firmwareish:
            st, ln, et, lm = verify_url(r["url"])
            r["http_status"] = st
            r["content_length_or_range"] = ln
            r["etag"] = et
            r["last_modified"] = lm
            time.sleep(0.05)

    fields = ["url","filename","candidate_score","sources","seen","http_status","content_length_or_range","etag","last_modified"]
    with open("fu_7-CUDY-CDN-FILES-INDEX.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    candidates = [
        r for r in rows
        if (
            "r25" in r["filename"].lower()
            or "lt500" in r["filename"].lower()
            or "lt500d" in r["filename"].lower()
        )
    ]
    with open("fu_7-CUDY-CDN-R25-LT500-CANDIDATES.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(candidates)

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "unique_cdn_urls": len(rows),
        "r25_lt500_candidates": len(candidates),
        "r25_25_candidates": [
            r for r in candidates
            if "r25" in r["filename"].lower() and "2.5." in r["filename"].lower()
        ],
        "lt500_25_candidates": [
            r for r in candidates
            if ("lt500" in r["filename"].lower() or "lt500d" in r["filename"].lower())
            and "2.5." in r["filename"].lower()
        ],
    }
    with open("fu_7-CUDY-CDN-INDEX-SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import csv, html, json, os, re, time, urllib.request
from collections import defaultdict

UA="OpenCudy-FU7-Dev-Harvest/1.0"
SOURCES=[
    ("openwrt","https://www.cudy.com/blogs/faq/openwrt-software-download?page={}",260),
    ("zerotier","https://www.cudy.com/en-gb/blogs/faq/how-to-remote-connect-cudy-router-via-zerotier?page={}",30),
    ("beta_tmobile","https://www.cudy.com/blogs/faq/beta-firmware-fix-lt18-lt450-lt500-lt500d-and-t-mobile-configuration-issue?page={}",15),
    ("csp25","https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}",90),
    ("upgrade","https://www.cudy.com/blogs/faq/how-to-upgrade-the-firmware-of-cudy-router?page={}",50),
    ("wr3000_vpn","https://www.cudy.com/en-th/blogs/news/cudy-wr3000-now-supports-openvpn-and-wireguard-vpn?page={}",15),
]

DEV_WORDS=[
    "beta firmware","beta","intermediate firmware","intermediary firmware","middle firmware",
    "transition image","signed openwrt","remove signature","google drive","sent you the firmware",
    "sent you firmware","via email","zerotier","test firmware","debug firmware","developer",
    "development firmware","recovery tftp","without recovery","new flash","f50l1g41lc",
]
FILE_RE=re.compile(r'(?i)([A-Za-z0-9_+ .()\-]{2,160}\.(?:bin|zip|img|trx|itb|tar\.gz|tgz))')
URL_RE=re.compile(r'https?://[^"\'<>\s]+',re.I)

def get(url,timeout=35):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,*/*"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read().decode("utf-8","replace")

def clean(s):
    s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
    s=re.sub(r'(?s)<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',html.unescape(s)).strip()

rows=[]
links=[]
visited=0
for kind,tpl,maxp in SOURCES:
    misses=0
    for p in range(1,maxp+1):
        url=tpl.format(p)
        try:
            raw=get(url)
        except Exception as e:
            print("FETCH_FAIL",kind,p,repr(e))
            misses+=1
            if misses>=8 and p>10:
                break
            continue
        misses=0
        visited+=1
        txt=clean(raw)
        low=txt.lower()

        for m in FILE_RE.finditer(txt):
            name=m.group(1).strip(" .,:;()[]{}'\"")
            if len(name)>180: continue
            a=max(0,m.start()-1400);b=min(len(txt),m.end()+1800)
            ctx=txt[a:b]
            cl=ctx.lower()
            dev=[w for w in DEV_WORDS if w in cl]
            cudyish=(
                "cudy" in cl or "firmware" in cl or
                name.lower().startswith(("lt","wr","tr","ap","m","re","cudy_","cudy-"))
            )
            if not cudyish: continue
            rows.append({
                "source_kind":kind,"page":p,"source_url":url,"filename":name,
                "dev_terms":" | ".join(dev),"context":ctx
            })

        for m in URL_RE.finditer(raw):
            u=html.unescape(m.group(0)).rstrip(").,;\"'")
            ul=u.lower()
            if any(h in ul for h in ("drive.google.com","mega.nz","dropbox.com","1drv.ms","onedrive.live.com")) or                re.search(r'\.(?:bin|zip|img|trx|itb)(?:\?|$)',ul):
                # context from raw, then clean
                a=max(0,m.start()-1800);b=min(len(raw),m.end()+2200)
                ctx=clean(raw[a:b])
                cl=ctx.lower()
                dev=[w for w in DEV_WORDS if w in cl]
                links.append({
                    "source_kind":kind,"page":p,"source_url":url,
                    "link":u,"dev_terms":" | ".join(dev),"context":ctx
                })

        if p%25==0:
            print("PROGRESS",kind,p,"files",len(rows),"links",len(links))
        time.sleep(.025)

# deduplicate filename contexts and links
seen=set();uniq=[]
for r in rows:
    k=(r["filename"].lower(),r["source_kind"],r["page"],re.sub(r'\s+',' ',r["context"].lower())[:1000])
    if k in seen: continue
    seen.add(k);uniq.append(r)

seen=set();ulinks=[]
for r in links:
    k=(r["link"],r["source_kind"],r["page"])
    if k in seen: continue
    seen.add(k);ulinks.append(r)

# aggregate filenames
agg=defaultdict(lambda:{"count":0,"dev_terms":set(),"sources":set(),"contexts":[]})
for r in uniq:
    a=agg[r["filename"]]
    a["count"]+=1
    a["dev_terms"].update(x.strip() for x in r["dev_terms"].split("|") if x.strip())
    a["sources"].add(r["source_url"])
    if len(a["contexts"])<4:a["contexts"].append(r["context"])

summary_rows=[]
for name,a in agg.items():
    summary_rows.append({
        "filename":name,
        "occurrences":a["count"],
        "dev_terms":" | ".join(sorted(a["dev_terms"])),
        "source_count":len(a["sources"]),
        "sources":" | ".join(sorted(a["sources"])),
        "context_sample":" || ".join(a["contexts"]),
    })
summary_rows.sort(key=lambda x:(0 if x["dev_terms"] else 1,x["filename"].lower()))

os.makedirs("fu_7-CUDY-DEV-HARVEST",exist_ok=True)
with open("fu_7-CUDY-DEV-HARVEST/filename_hits.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["source_kind","page","source_url","filename","dev_terms","context"]);w.writeheader();w.writerows(uniq)
with open("fu_7-CUDY-DEV-HARVEST/filenames_aggregated.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["filename","occurrences","dev_terms","source_count","sources","context_sample"]);w.writeheader();w.writerows(summary_rows)
with open("fu_7-CUDY-DEV-HARVEST/link_hits.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["source_kind","page","source_url","link","dev_terms","context"]);w.writeheader();w.writerows(ulinks)

high=[x for x in summary_rows if x["dev_terms"]]
drive=[x for x in ulinks if "drive.google.com" in x["link"].lower()]
summary={
    "pages_visited":visited,
    "unique_filename_hits":len(summary_rows),
    "high_confidence_dev_private_names":len(high),
    "link_hits":len(ulinks),
    "google_drive_links":len(drive),
    "high_confidence_filenames":[x["filename"] for x in high],
    "drive_links":sorted({x["link"] for x in drive}),
}
open("fu_7-CUDY-DEV-HARVEST/summary.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))
print("=== HIGH CONFIDENCE NAMES ===")
for x in high:
    print(x["filename"],"::",x["dev_terms"])
print("=== DRIVE LINKS ===")
for u in summary["drive_links"]:
    print(u)

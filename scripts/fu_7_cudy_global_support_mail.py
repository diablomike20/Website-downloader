#!/usr/bin/env python3
import html,re,time,urllib.request,csv,json
from collections import defaultdict

BASE="https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}"
UA="OpenCudy-FU7-GlobalSupportMail/1.0"

DELIVERY_PATTERNS=[
    "sent you the firmware via email",
    "sent you firmware via email",
    "sent you the beta firmware",
    "sent you the firmware",
    "technical support has contacted you via email",
    "technical support has contacted you",
    "provided you with the beta firmware",
    "provided you the beta firmware",
    "send you the firmware",
    "send the firmware via email",
    "firmware via email",
]
MODEL_RE=re.compile(r'\b(?:WR|LT|M|RE|AP|P|TR|C|X|WBR|BE)[A-Z0-9+_-]{1,18}(?:\s*(?:V|v)?\d+(?:\.\d+)?)?\b')
VER_RE=re.compile(r'(?i)\b(?:firmware\s*(?:version[-: ]*)?)?((?:\d+\.){2}\d+(?:beta|b)?(?:[-_ ]?\d{8}[-_]\d{6})?)\b')
FULL_RE=re.compile(r'(?i)\b([A-Z0-9+_-]+-R\d+-[0-9A-Za-z._-]+(?:sysupgrade|flash|firmware|CellularUpgrade|upgrade-module)?(?:\.bin|\.zip)?)\b')

def fetch(u):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode("utf-8","replace")

def clean(s):
    s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
    s=re.sub(r'(?s)<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',html.unescape(s)).strip()

hits=[]
for p in range(1,101):
    try: txt=clean(fetch(BASE.format(p)))
    except Exception as e:
        print("FAIL",p,repr(e)); continue
    lo=txt.lower()
    for phrase in DELIVERY_PATTERNS:
        start=0
        ph=phrase.lower()
        while True:
            i=lo.find(ph,start)
            if i<0: break
            a=max(0,i-3500);b=min(len(txt),i+5000)
            ctx=txt[a:b]
            models=sorted(set(MODEL_RE.findall(ctx)))
            vers=sorted(set(m.group(1) for m in VER_RE.finditer(ctx)))
            full=sorted(set(FULL_RE.findall(ctx)))
            hits.append({
                "page":p,
                "phrase":phrase,
                "models":" | ".join(models),
                "versions":" | ".join(vers),
                "full_builds":" | ".join(full),
                "context":ctx
            })
            start=i+len(ph)
    if p%10==0:print("PAGE",p,"hits",len(hits))
    time.sleep(.025)

# Dedupe near-identical support blocks.
seen=set();uniq=[]
for h in hits:
    key=re.sub(r'\s+',' ',h["context"].lower())[:2500]
    if key in seen: continue
    seen.add(key);uniq.append(h)

# Extract per-model/version evidence candidates.
pairs=defaultdict(lambda:{"pages":set(),"phrases":set(),"contexts":[],"full_builds":set()})
for h in uniq:
    models=[x.strip() for x in h["models"].split("|") if x.strip()]
    vers=[x.strip() for x in h["versions"].split("|") if x.strip()]
    builds=[x.strip() for x in h["full_builds"].split("|") if x.strip()]
    if not models: models=["UNKNOWN"]
    if not vers: vers=["UNKNOWN"]
    for m in models:
        for v in vers:
            k=(m,v);a=pairs[k]
            a["pages"].add(h["page"]);a["phrases"].add(h["phrase"]);a["full_builds"].update(builds)
            if len(a["contexts"])<3:a["contexts"].append(h["context"])

pair_rows=[]
for (m,v),a in pairs.items():
    pair_rows.append({
        "model":m,"version":v,
        "pages":"|".join(map(str,sorted(a["pages"]))),
        "phrases":" | ".join(sorted(a["phrases"])),
        "full_builds":" | ".join(sorted(a["full_builds"])),
        "context":" || ".join(a["contexts"])
    })
pair_rows.sort(key=lambda x:(x["model"].lower(),x["version"].lower()))

with open("fu_7-CUDY-GLOBAL-SUPPORT-MAIL-HITS.csv","w",newline="",encoding="utf-8") as f:
    fields=["page","phrase","models","versions","full_builds","context"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(uniq)
with open("fu_7-CUDY-GLOBAL-SUPPORT-MAIL-PAIRS.csv","w",newline="",encoding="utf-8") as f:
    fields=["model","version","pages","phrases","full_builds","context"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(pair_rows)

summary={
    "unique_delivery_blocks":len(uniq),
    "model_version_pairs":len(pair_rows),
    "explicit_full_builds":sorted({b for h in uniq for b in h["full_builds"].split(" | ") if b}),
    "models":sorted({m.strip() for h in uniq for m in h["models"].split(" | ") if m.strip()}),
    "versions":sorted({v.strip() for h in uniq for v in h["versions"].split(" | ") if v.strip()}),
}
open("fu_7-CUDY-GLOBAL-SUPPORT-MAIL-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

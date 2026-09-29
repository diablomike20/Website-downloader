#!/usr/bin/env python3
import html,re,time,urllib.request,csv,json,urllib.parse

BASE="https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}"
UA="OpenCudy-FU7-LinkLeak/1.0"
URL_RE=re.compile(r'https?://[^"\'<>\s]+',re.I)
FILE_RE=re.compile(r'\b[A-Za-z0-9_.-]*(?:LT500D?|R25)[A-Za-z0-9_.-]*(?:\.zip|\.bin)\b',re.I)
TERMS=("lt500","lt500d","r25")

def fetch(u):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode("utf-8","replace")

def clean(s):
    s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
    s=re.sub(r'(?s)<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',html.unescape(s)).strip()

rows=[]
for p in range(1,81):
    try:
        txt=clean(fetch(BASE.format(p)))
    except Exception as e:
        print("FAIL",p,repr(e)); continue
    low=txt.lower()

    # URLs with LT500/R25 context
    for m in URL_RE.finditer(txt):
        url=m.group(0).rstrip(').,;')
        ulen=url.lower()
        if not any(host in ulen for host in (
            "drive.google.com","mega.nz","dropbox.com","onedrive.live.com",
            "1drv.ms","cdn.shopify.com","cudy.com/cdn/shop/files",
            "cloudfront.net","googleusercontent.com"
        )):
            continue
        a=max(0,m.start()-1800); b=min(len(txt),m.end()+1800)
        ctx=txt[a:b]
        cl=ctx.lower()
        if any(t in cl for t in TERMS):
            rows.append({"page":p,"kind":"URL","value":url,"context":ctx})

    # Literal firmware filenames even without visible URL
    for m in FILE_RE.finditer(txt):
        a=max(0,m.start()-1600); b=min(len(txt),m.end()+1600)
        rows.append({"page":p,"kind":"FILENAME","value":m.group(0),"context":txt[a:b]})

    if p%10==0: print("PAGE",p,"rows",len(rows))
    time.sleep(.03)

# dedupe
seen=set(); uniq=[]
for r in rows:
    key=(r["kind"],r["value"],re.sub(r'\s+',' ',r["context"].lower())[:1200])
    if key in seen: continue
    seen.add(key); uniq.append(r)

with open("fu_7-LT500-LINK-LEAK-HITS.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["page","kind","value","context"]);w.writeheader();w.writerows(uniq)
with open("fu_7-LT500-LINK-LEAK-HITS.json","w",encoding="utf-8") as f:
    json.dump(uniq,f,indent=2,ensure_ascii=False)

summary={
    "raw_hits":len(rows),
    "unique_hits":len(uniq),
    "values":sorted({r["value"] for r in uniq}),
}
open("fu_7-LT500-LINK-LEAK-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))
for r in uniq:
    print("\n--- PAGE",r["page"],r["kind"],r["value"],"---\n",r["context"][:3000])

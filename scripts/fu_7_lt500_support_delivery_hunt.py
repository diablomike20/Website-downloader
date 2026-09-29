#!/usr/bin/env python3
import html,re,time,urllib.request,csv,json

BASE="https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}"
UA="OpenCudy-FU7-SupportDelivery/1.0"
MODEL_TERMS=("lt500","lt500d","r25")
DELIVERY_TERMS=(
    "sent you the firmware via email",
    "sent you firmware via email",
    "sent you the new official firmware",
    "technical support has contacted you via email",
    "technical support has contacted you",
    "beta firmware",
    "new official firmware",
    "firmware via email",
    "send you the firmware",
    "send firmware",
    "2.5.x",
)

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
    lo=txt.lower()

    positions=[]
    for mt in MODEL_TERMS:
        start=0
        while True:
            i=lo.find(mt,start)
            if i<0: break
            positions.append((i,mt))
            start=i+len(mt)

    for i,mt in positions:
        a=max(0,i-2200); b=min(len(txt),i+3000)
        ctx=txt[a:b]
        cl=ctx.lower()
        matched=[d for d in DELIVERY_TERMS if d in cl]
        if matched:
            rows.append({
                "page":p,
                "model_term":mt,
                "delivery_terms":" | ".join(matched),
                "context":ctx
            })

    if p%10==0: print("PAGE",p,"rows",len(rows))
    time.sleep(.03)

seen=set();uniq=[]
for r in rows:
    key=re.sub(r'\s+',' ',r["context"].lower())[:1800]
    if key in seen: continue
    seen.add(key);uniq.append(r)

with open("fu_7-LT500-SUPPORT-DELIVERY-HITS.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["page","model_term","delivery_terms","context"]);w.writeheader();w.writerows(uniq)
with open("fu_7-LT500-SUPPORT-DELIVERY-HITS.json","w",encoding="utf-8") as f:
    json.dump(uniq,f,indent=2,ensure_ascii=False)

summary={
    "raw_hits":len(rows),
    "unique_hits":len(uniq),
    "pages":sorted({r["page"] for r in uniq}),
}
open("fu_7-LT500-SUPPORT-DELIVERY-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
for r in uniq:
    print("\n--- PAGE",r["page"],r["model_term"],r["delivery_terms"],"---\n",r["context"][:4200])

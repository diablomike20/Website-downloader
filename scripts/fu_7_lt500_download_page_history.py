#!/usr/bin/env python3
import csv,json,re,time,urllib.parse,urllib.request
from collections import defaultdict

UA="OpenCudy-FU7-PageHistory/1.0"
PAGES=[
 "https://www.cudy.com/pages/download-center/lt500-3-0",
 "https://www.cudy.com/pages/download-center/lt500d-3-0",
 "https://www.cudy.com/pages/download-center/lt500-2-0",
 "https://www.cudy.com/pages/download-center/lt500d-2-0",
]
FW_RE=re.compile(r'([A-Za-z0-9_.-]*(?:LT500|LT500D|R25)[A-Za-z0-9_.-]*(?:flash|firmware)[A-Za-z0-9_.?-]*\.(?:zip|bin))',re.I)
R25_RE=re.compile(r'([A-Za-z0-9_.-]*R25[A-Za-z0-9_.-]*(?:\.zip|\.bin))',re.I)
V25_RE=re.compile(r'([A-Za-z0-9_.-]*(?:LT500|LT500D|R25)[A-Za-z0-9_.-]*2\.5\.[A-Za-z0-9_.-]*)',re.I)

def get(url,timeout=60):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace")

records=[]
for page in PAGES:
 q=urllib.parse.urlencode([
  ("url",page),
  ("output","json"),
  ("fl","timestamp,original,statuscode,digest"),
  ("filter","statuscode:200"),
  ("from","2025"),
  ("to","2026"),
  ("collapse","digest"),
 ])
 try:
  data=json.loads(get("https://web.archive.org/cdx/search/cdx?"+q,90))
 except Exception as e:
  print("CDX_FAIL",page,repr(e));continue
 if not data: continue
 h=data[0]
 snaps=[dict(zip(h,r)) for r in data[1:]]
 print("PAGE",page,"UNIQUE_SNAPSHOTS",len(snaps))
 for i,s in enumerate(snaps):
  ts=s["timestamp"]
  archived=f"https://web.archive.org/web/{ts}id_/{page}"
  try:
   body=get(archived,50)
  except Exception as e:
   print("SNAP_FAIL",ts,page,repr(e));continue
  matches=sorted(set(FW_RE.findall(body)+R25_RE.findall(body)+V25_RE.findall(body)))
  # Also collect all literal contexts around R25 / 2.5 for filename leaks.
  contexts=[]
  for needle in ("R25","2.5.","LT500V2","LT500D"):
   pos=0
   while True:
    p=body.find(needle,pos)
    if p<0:break
    ctx=re.sub(r'\s+',' ',body[max(0,p-180):p+260])
    contexts.append(ctx[:440])
    pos=p+len(needle)
    if len(contexts)>=40:break
  records.append({
   "page":page,"timestamp":ts,"digest":s.get("digest",""),
   "matches":" | ".join(matches),
   "has_25":"YES" if any("2.5." in x for x in matches) or "2.5." in body else "NO",
   "has_r25":"YES" if "R25" in body else "NO",
   "contexts":" || ".join(contexts[:40]),
  })
  time.sleep(.08)

fields=["page","timestamp","digest","matches","has_25","has_r25","contexts"]
with open("fu_7-LT500-DOWNLOAD-PAGE-HISTORY.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
hits=[r for r in records if "2.5." in r["matches"] or (r["has_25"]=="YES" and r["has_r25"]=="YES")]
summary={
 "snapshots_checked":len(records),
 "interesting_snapshots":len(hits),
 "hits":[{k:r[k] for k in ("page","timestamp","matches","has_25","has_r25")} for r in hits],
 "all_match_sets":sorted(set(r["matches"] for r in records if r["matches"])),
}
open("fu_7-LT500-DOWNLOAD-PAGE-HISTORY-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

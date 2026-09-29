#!/usr/bin/env python3
import csv, json, urllib.parse, urllib.request, time
from collections import defaultdict

UA="OpenCudy-FU7-R25-CDN-Hunt/1.0"
PATTERNS=[
 "www.cudy.com/cdn/shop/files/LT500*",
 "www.cudy.com/cdn/shop/files/LT500D*",
 "www.cudy.com/cdn/shop/files/LT450-LT500*",
]
INDEXES=[
 "CC-MAIN-2026-34","CC-MAIN-2026-30","CC-MAIN-2026-25",
 "CC-MAIN-2026-21","CC-MAIN-2026-17","CC-MAIN-2026-12",
 "CC-MAIN-2026-08","CC-MAIN-2026-04",
 "CC-MAIN-2025-51","CC-MAIN-2025-47","CC-MAIN-2025-43",
 "CC-MAIN-2025-38","CC-MAIN-2025-33",
]
PAGES=[
 "https://www.cudy.com/pages/download-center/lt500-2-0",
 "https://www.cudy.com/pages/download-center/lt500-3-0",
 "https://www.cudy.com/pages/download-center/lt500d-2-0",
 "https://www.cudy.com/pages/download-center/lt500d-3-0",
]
def get(url,timeout=40):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace"),r.status,dict(r.headers)
def norm(u):
 u=u.replace("&amp;","&").strip()
 p=urllib.parse.urlsplit(u)
 if p.netloc.lower() in ("cudy.com","www.cudy.com") and p.path.startswith("/cdn/shop/files/"):
  return urllib.parse.urlunsplit(("https","www.cudy.com",p.path,p.query,""))
 return None
rows=defaultdict(lambda:{"sources":set(),"seen":set()})
def add(u,src,seen=""):
 u=norm(u)
 if not u:return
 rows[u]["sources"].add(src)
 if seen:rows[u]["seen"].add(seen)

# Common Crawl targeted prefix queries
for idx in INDEXES:
 for pat in PATTERNS:
  q=urllib.parse.urlencode({"url":pat,"output":"json","filter":"status:200"})
  url=f"https://index.commoncrawl.org/{idx}-index?{q}"
  try:
   body,_,_=get(url,60)
   n=0
   for ln in body.splitlines():
    try:o=json.loads(ln)
    except:continue
    u=o.get("url") or o.get("original")
    if u:
     add(u,"commoncrawl:"+idx,o.get("timestamp",""))
     n+=1
   print("CC",idx,pat,n)
  except Exception as e:
   print("CC_FAIL",idx,pat,repr(e))
  time.sleep(.05)

# Wayback targeted prefix queries
for pat in PATTERNS:
 q=urllib.parse.urlencode({
  "url":pat,"output":"json","fl":"timestamp,original,statuscode,digest",
  "filter":"statuscode:200","collapse":"urlkey"
 })
 try:
  body,_,_=get("https://web.archive.org/cdx/search/cdx?"+q,90)
  data=json.loads(body)
  if data:
   hdr=data[0]
   for rr in data[1:]:
    o=dict(zip(hdr,rr))
    if o.get("original"):add(o["original"],"wayback",o.get("timestamp",""))
  print("WB",pat,max(0,len(data)-1 if data else 0))
 except Exception as e:
  print("WB_FAIL",pat,repr(e))

# Current official pages: pull all Cudy CDN links from source
import re
rx=re.compile(r'https?://(?:www\.)?cudy\.com/cdn/shop/files/[^"\'<>\\\s]+',re.I)
for page in PAGES:
 try:
  body,_,_=get(page,30)
  for u in rx.findall(body): add(u,"cudy_page:"+page)
 except Exception as e:
  print("PAGE_FAIL",page,repr(e))

def verify(url):
 try:
  req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":UA})
  with urllib.request.urlopen(req,timeout=20) as r:
   return r.status,r.headers.get("Content-Length",""),r.headers.get("ETag",""),r.headers.get("Last-Modified","")
 except Exception as e:
  return getattr(e,"code","ERR"),"","",""

out=[]
for u,meta in rows.items():
 fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
 lo=fn.lower()
 score=(8 if "r25" in lo else 0)+(7 if "lt500d" in lo else 0)+(5 if "lt500" in lo else 0)+(6 if "2.5." in lo else 0)+(2 if "flash" in lo else 0)
 st,ln,etag,lm=verify(u)
 out.append({
  "filename":fn,"url":u,"score":score,"http_status":st,"content_length":ln,
  "etag":etag,"last_modified":lm,
  "sources":" | ".join(sorted(meta["sources"])),
  "seen":" | ".join(sorted(meta["seen"]))
 })
out.sort(key=lambda r:(-r["score"],r["filename"].lower(),r["url"]))
fields=["filename","url","score","http_status","content_length","etag","last_modified","sources","seen"]
with open("fu_7-R25-LT500-CDN-INDEX.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
hits=[r for r in out if "2.5." in r["filename"].lower()]
with open("fu_7-R25-LT500-CSP25-HITS.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(hits)
summary={"unique_urls":len(out),"csp25_hits":len(hits),"csp25_filenames":[r["filename"] for r in hits]}
with open("fu_7-R25-LT500-CDN-SUMMARY.json","w",encoding="utf-8") as f:json.dump(summary,f,indent=2,ensure_ascii=False)
print(json.dumps(summary,indent=2,ensure_ascii=False))

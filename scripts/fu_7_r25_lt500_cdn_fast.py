#!/usr/bin/env python3
import csv,json,re,urllib.parse,urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed

UA="OpenCudy-FU7-R25-CDN-Fast/1.0"
INDEXES=["CC-MAIN-2026-34","CC-MAIN-2026-30","CC-MAIN-2026-25","CC-MAIN-2026-21","CC-MAIN-2026-17","CC-MAIN-2026-12","CC-MAIN-2026-08","CC-MAIN-2026-04"]
PREFIXES=["LT500","LT500D","LT450-LT500"]
PAGES=[
"https://www.cudy.com/pages/download-center/lt500-2-0",
"https://www.cudy.com/pages/download-center/lt500-3-0",
"https://www.cudy.com/pages/download-center/lt500d-2-0",
"https://www.cudy.com/pages/download-center/lt500d-3-0"]
def get(url,timeout=18,method="GET"):
 req=urllib.request.Request(url,method=method,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace"),r.status,dict(r.headers)
def norm(u):
 u=u.replace("&amp;","&").strip().rstrip(".,;)]}")
 p=urllib.parse.urlsplit(u)
 if p.netloc.lower() in ("www.cudy.com","cudy.com") and p.path.startswith("/cdn/shop/files/"):
  return urllib.parse.urlunsplit(("https","www.cudy.com",p.path,p.query,""))
 return None
found=defaultdict(lambda:{"sources":set(),"seen":set()})
def add(u,src,seen=""):
 u=norm(u)
 if not u:return
 found[u]["sources"].add(src)
 if seen:found[u]["seen"].add(seen)

def cc_one(idx,prefix):
 params=urllib.parse.urlencode({
  "url":"www.cudy.com/cdn/shop/files/"+prefix,
  "matchType":"prefix","output":"json","filter":"status:200"})
 url=f"https://index.commoncrawl.org/{idx}-index?{params}"
 try:
  body,_,_=get(url,18)
  out=[]
  for ln in body.splitlines():
   try:o=json.loads(ln)
   except:continue
   u=o.get("url") or o.get("original")
   if u:out.append((u,o.get("timestamp","")))
  return idx,prefix,out,None
 except Exception as e:return idx,prefix,[],repr(e)

with ThreadPoolExecutor(max_workers=4) as ex:
 futs=[ex.submit(cc_one,i,p) for i in INDEXES for p in PREFIXES]
 for fut in as_completed(futs):
  idx,prefix,items,err=fut.result()
  print("CC",idx,prefix,len(items),"ERR="+err if err else "")
  for u,ts in items:add(u,"commoncrawl:"+idx,ts)

def wb_one(prefix):
 params=urllib.parse.urlencode({
  "url":"www.cudy.com/cdn/shop/files/"+prefix+"*","output":"json",
  "fl":"timestamp,original,statuscode,digest","filter":"statuscode:200","collapse":"urlkey"})
 try:
  body,_,_=get("https://web.archive.org/cdx/search/cdx?"+params,20)
  data=json.loads(body); out=[]
  if data:
   h=data[0]
   for row in data[1:]:
    o=dict(zip(h,row))
    if o.get("original"):out.append((o["original"],o.get("timestamp","")))
  return prefix,out,None
 except Exception as e:return prefix,[],repr(e)
with ThreadPoolExecutor(max_workers=3) as ex:
 for fut in as_completed([ex.submit(wb_one,p) for p in PREFIXES]):
  p,items,err=fut.result()
  print("WB",p,len(items),"ERR="+err if err else "")
  for u,ts in items:add(u,"wayback",ts)

rx=re.compile(r'https?://(?:www\.)?cudy\.com/cdn/shop/files/[^"\'<>\\\s]+',re.I)
for page in PAGES:
 try:
  body,_,_=get(page,18)
  hits=rx.findall(body); print("PAGE",page,len(hits))
  for u in hits:add(u,"cudy_page:"+page)
 except Exception as e:print("PAGE_FAIL",page,repr(e))

def verify(u):
 try:
  _,st,h=get(u,15,"HEAD")
  return st,h.get("Content-Length",""),h.get("ETag",""),h.get("Last-Modified","")
 except Exception as e:return getattr(e,"code","ERR"),"","",""

records=[]
for u,m in found.items():
 fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
 lo=fn.lower()
 score=(8 if "r25" in lo else 0)+(7 if "lt500d" in lo else 0)+(5 if "lt500" in lo else 0)+(6 if "2.5." in lo else 0)+(2 if "flash" in lo else 0)
 records.append({"filename":fn,"url":u,"score":score,"sources":" | ".join(sorted(m["sources"])),"seen":" | ".join(sorted(m["seen"]))})
records.sort(key=lambda x:(-x["score"],x["filename"].lower(),x["url"]))

with ThreadPoolExecutor(max_workers=4) as ex:
 mp={ex.submit(verify,r["url"]):r for r in records}
 for fut in as_completed(mp):
  r=mp[fut]; st,ln,et,lm=fut.result()
  r.update(http_status=st,content_length=ln,etag=et,last_modified=lm)

fields=["filename","url","score","http_status","content_length","etag","last_modified","sources","seen"]
with open("fu_7-R25-LT500-CDN-FAST-INDEX.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
hits=[r for r in records if "2.5." in r["filename"].lower()]
with open("fu_7-R25-LT500-CSP25-FAST-HITS.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(hits)
s={"unique_urls":len(records),"csp25_hits":len(hits),"hits":[{"filename":r["filename"],"url":r["url"],"status":r["http_status"]} for r in hits]}
open("fu_7-R25-LT500-CDN-FAST-SUMMARY.json","w",encoding="utf-8").write(json.dumps(s,indent=2,ensure_ascii=False))
print(json.dumps(s,indent=2,ensure_ascii=False))

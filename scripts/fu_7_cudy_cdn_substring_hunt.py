#!/usr/bin/env python3
import csv,json,urllib.parse,urllib.request,re
from collections import defaultdict

UA="OpenCudy-FU7-CDN-Substring/1.0"
QUERIES={
 "R25": r".*R25.*",
 "CSP25": r".*2\.5\..*",
 "FLASHZIP": r".*flash\.zip.*",
}
def get(url,timeout=120):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace")
def query(regex):
 p=urllib.parse.urlencode([
  ("url","www.cudy.com/cdn/shop/files/*"),
  ("output","json"),
  ("fl","timestamp,original,statuscode,mimetype,digest,length"),
  ("filter","statuscode:200"),
  ("filter","original:"+regex),
  ("collapse","urlkey"),
 ])
 url="https://web.archive.org/cdx/search/cdx?"+p
 body=get(url)
 data=json.loads(body)
 if not data:return []
 hdr=data[0]
 return [dict(zip(hdr,r)) for r in data[1:]]

allrows=defaultdict(lambda:{"query_tags":set(),"timestamps":set(),"statuscode":"","mimetype":"","digest":"","length":""})
errors={}
for tag,regex in QUERIES.items():
 try:
  rows=query(regex)
  print(tag,len(rows))
  for o in rows:
   u=o.get("original","")
   if not u:continue
   r=allrows[u]
   r["query_tags"].add(tag)
   if o.get("timestamp"):r["timestamps"].add(o["timestamp"])
   for k in ("statuscode","mimetype","digest","length"):
    if o.get(k):r[k]=o[k]
 except Exception as e:
  errors[tag]=repr(e)
  print(tag,"ERROR",repr(e))

out=[]
for u,r in allrows.items():
 fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
 lo=fn.lower()
 out.append({
  "filename":fn,
  "url":u,
  "tags":"|".join(sorted(r["query_tags"])),
  "timestamp":"|".join(sorted(r["timestamps"])),
  "statuscode":r["statuscode"],
  "mimetype":r["mimetype"],
  "digest":r["digest"],
  "length":r["length"],
  "is_r25":"YES" if "r25" in lo else "NO",
  "is_25":"YES" if "2.5." in lo else "NO",
  "is_flashzip":"YES" if "flash.zip" in lo else "NO",
 })
out.sort(key=lambda x:(x["filename"].lower(),x["url"]))
fields=list(out[0].keys()) if out else ["filename","url","tags","timestamp","statuscode","mimetype","digest","length","is_r25","is_25","is_flashzip"]
with open("fu_7-CUDY-CDN-SUBSTRING-INDEX.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
r25=[x for x in out if x["is_r25"]=="YES"]
csp=[x for x in out if x["is_25"]=="YES"]
cross=[x for x in out if x["is_r25"]=="YES" and x["is_25"]=="YES"]
flash=[x for x in out if x["is_flashzip"]=="YES"]
for name,rows in [
 ("fu_7-CUDY-CDN-R25-SUBSTRING.csv",r25),
 ("fu_7-CUDY-CDN-CSP25-SUBSTRING.csv",csp),
 ("fu_7-CUDY-CDN-R25-CSP25-CROSS.csv",cross),
 ("fu_7-CUDY-CDN-ALL-FLASHZIP.csv",flash),
]:
 with open(name,"w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
summary={
 "errors":errors,
 "unique_urls":len(out),
 "r25":len(r25),
 "csp25":len(csp),
 "r25_csp25":len(cross),
 "flashzip":len(flash),
 "r25_csp25_rows":cross,
}
open("fu_7-CUDY-CDN-SUBSTRING-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

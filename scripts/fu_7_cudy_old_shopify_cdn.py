#!/usr/bin/env python3
import csv,json,urllib.parse,urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed

UA="OpenCudy-FU7-Old-Shopify-CDN/1.0"
BASE="cdn.shopify.com/s/files/1/0673/4748/0820/files/"
TASKS=[
 ("LT500_PREFIX", {"url":BASE+"LT500*"}),
 ("R25_FILTER", {"url":BASE+"*","filter2":"original:.*R25.*"}),
 ("CSP25_FILTER", {"url":BASE+"*","filter2":"original:.*2\\.5\\..*"}),
 ("FLASH_FILTER", {"url":BASE+"*","filter2":"original:.*flash\\.zip.*"}),
]
def get(url,timeout=120):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace")
def run(tag,spec):
 params=[
  ("url",spec["url"]),("output","json"),
  ("fl","timestamp,original,statuscode,mimetype,digest,length"),
  ("filter","statuscode:200"),("collapse","urlkey")
 ]
 if spec.get("filter2"):params.append(("filter",spec["filter2"]))
 url="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
 try:
  data=json.loads(get(url))
  if not data:return tag,[],None
  h=data[0]
  return tag,[dict(zip(h,r)) for r in data[1:]],None
 except Exception as e:return tag,[],repr(e)

found=defaultdict(lambda:{"tags":set(),"times":set(),"statuscode":"","mimetype":"","digest":"","length":""})
errors={}
with ThreadPoolExecutor(max_workers=2) as ex:
 futs=[ex.submit(run,t,s) for t,s in TASKS]
 for fut in as_completed(futs):
  tag,rows,err=fut.result()
  print(tag,len(rows),"ERR="+err if err else "")
  if err:errors[tag]=err
  for o in rows:
   u=o.get("original","")
   if not u:continue
   r=found[u];r["tags"].add(tag)
   if o.get("timestamp"):r["times"].add(o["timestamp"])
   for k in ("statuscode","mimetype","digest","length"):
    if o.get(k):r[k]=o[k]

out=[]
for u,r in found.items():
 fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
 lo=fn.lower()
 out.append({
  "filename":fn,"url":u,"tags":"|".join(sorted(r["tags"])),"timestamp":"|".join(sorted(r["times"])),
  "statuscode":r["statuscode"],"mimetype":r["mimetype"],"digest":r["digest"],"length":r["length"],
  "is_r25":"YES" if "r25" in lo else "NO",
  "is_25":"YES" if "2.5." in lo else "NO",
  "is_flashzip":"YES" if "flash.zip" in lo else "NO"
 })
out.sort(key=lambda x:(x["filename"].lower(),x["url"]))
fields=["filename","url","tags","timestamp","statuscode","mimetype","digest","length","is_r25","is_25","is_flashzip"]
def write(name,rows):
 with open(name,"w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
write("fu_7-CUDY-OLD-SHOPIFY-INDEX.csv",out)
r25=[x for x in out if x["is_r25"]=="YES"]
csp=[x for x in out if x["is_25"]=="YES"]
cross=[x for x in out if x["is_r25"]=="YES" and x["is_25"]=="YES"]
flash=[x for x in out if x["is_flashzip"]=="YES"]
write("fu_7-CUDY-OLD-SHOPIFY-R25.csv",r25)
write("fu_7-CUDY-OLD-SHOPIFY-CSP25.csv",csp)
write("fu_7-CUDY-OLD-SHOPIFY-R25-CSP25.csv",cross)
write("fu_7-CUDY-OLD-SHOPIFY-FLASHZIP.csv",flash)
summary={"errors":errors,"unique":len(out),"r25":len(r25),"csp25":len(csp),"r25_csp25":len(cross),"flashzip":len(flash),"cross":cross}
open("fu_7-CUDY-OLD-SHOPIFY-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

#!/usr/bin/env python3
import csv,json,re,urllib.parse,urllib.request,os,hashlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

UA="OpenCudy-FU7-Dev-CDN-Archive/1.0"
SCOPES=[
 ("alias","www.cudy.com/cdn/shop/files/*"),
 ("oldshop","cdn.shopify.com/s/files/1/0673/4748/0820/files/*"),
]
FILTERS={
 "beta":r"original:.*[Bb][Ee][Tt][Aa].*",
 "alpha":r"original:.*[Aa][Ll][Pp][Hh][Aa].*",
 "debug":r"original:.*[Dd][Ee][Bb][Uu][Gg].*",
 "test":r"original:.*[Tt][Ee][Ss][Tt].*",
 "dev":r"original:.*[Dd][Ee][Vv].*",
 "2.1.15Beta":r"original:.*2\.1\.15[Bb]eta.*",
 "2.5.10b":r"original:.*2\.5\.10[bB].*",
 "2.5.11b":r"original:.*2\.5\.11[bB].*",
 "2.5.14b":r"original:.*2\.5\.14[bB].*",
 "2.3.12Beta":r"original:.*2\.3\.12[Bb]eta.*",
}

def fetch(url,timeout=100):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read(),r.status,dict(r.headers)

def cdx(scope,flt):
 params=[
  ("url",scope),("output","json"),
  ("fl","timestamp,original,statuscode,mimetype,digest,length"),
  ("filter","statuscode:200"),("filter",flt),("collapse","urlkey")
 ]
 u="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
 try:
  b,_,_=fetch(u,140); data=json.loads(b.decode("utf-8","replace"))
  if not data:return []
  h=data[0];return [dict(zip(h,x)) for x in data[1:]]
 except Exception as e:
  print("CDX_FAIL",scope,flt,repr(e));return []

tasks=[]
with ThreadPoolExecutor(max_workers=3) as ex:
 for sname,scope in SCOPES:
  for tag,flt in FILTERS.items():
   tasks.append((sname,tag,ex.submit(cdx,scope,flt)))
 found=defaultdict(lambda:{"tags":set(),"scope":set(),"timestamps":set(),"meta":{}})
 for sname,tag,fut in tasks:
  rows=fut.result()
  print("CDX",sname,tag,len(rows))
  for o in rows:
   u=o.get("original","")
   if not u:continue
   r=found[u];r["tags"].add(tag);r["scope"].add(sname)
   if o.get("timestamp"):r["timestamps"].add(o["timestamp"])
   r["meta"]=o

rows=[]
for u,r in found.items():
 fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
 lo=fn.lower()
 likely_fw=lo.endswith((".bin",".zip",".img",".trx",".itb",".tar.gz",".tgz")) or "firmware" in lo or "flash" in lo or "sysupgrade" in lo
 rows.append({
  "filename":fn,"url":u,"tags":"|".join(sorted(r["tags"])),"scopes":"|".join(sorted(r["scope"])),
  "timestamps":"|".join(sorted(r["timestamps"])),"mimetype":r["meta"].get("mimetype",""),
  "length":r["meta"].get("length",""),"digest":r["meta"].get("digest",""),
  "likely_firmware":"YES" if likely_fw else "NO",
 })
rows.sort(key=lambda x:(x["likely_firmware"]!="YES",x["filename"].lower(),x["url"]))

fields=["filename","url","tags","scopes","timestamps","mimetype","length","digest","likely_firmware"]
with open("fu_7-CUDY-DEV-CDN-ARCHIVE-INDEX.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
fw=[r for r in rows if r["likely_firmware"]=="YES"]
with open("fu_7-CUDY-DEV-CDN-ARCHIVE-FIRMWARE.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(fw)

# Attempt recovery for every firmware-like archived URL
os.makedirs("fu_7-CUDY-DEV-CDN-RECOVERED",exist_ok=True)
recovered=[]
seen_sha=set()
for r in fw:
 candidates=[r["url"]]
 for ts in r["timestamps"].split("|"):
  if ts:candidates.append(f"https://web.archive.org/web/{ts}id_/{r['url']}")
 for u in candidates:
  try:data,st,h=fetch(u,90)
  except Exception:continue
  if len(data)<1024 or b"<html" in data[:512].lower() or b"<!doctype" in data[:512].lower():continue
  sha=hashlib.sha256(data).hexdigest()
  if sha in seen_sha:continue
  seen_sha.add(sha)
  base=re.sub(r'[^A-Za-z0-9._()+ -]','_',r["filename"]) or "artifact.bin"
  p=os.path.join("fu_7-CUDY-DEV-CDN-RECOVERED",base)
  if os.path.exists(p):
   stem,ext=os.path.splitext(p);p=stem+"-"+sha[:8]+ext
  open(p,"wb").write(data)
  recovered.append({"filename":os.path.basename(p),"source":u,"size":len(data),"sha256":sha,"tags":r["tags"]})
  print("RECOVERED",os.path.basename(p),len(data),sha)
  break
with open("fu_7-CUDY-DEV-CDN-RECOVERED-MANIFEST.csv","w",newline="",encoding="utf-8") as f:
 fields2=["filename","source","size","sha256","tags"];w=csv.DictWriter(f,fieldnames=fields2);w.writeheader();w.writerows(recovered)
summary={"indexed_urls":len(rows),"firmware_like":len(fw),"recovered":len(recovered),"recovered_files":recovered}
open("fu_7-CUDY-DEV-CDN-ARCHIVE-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

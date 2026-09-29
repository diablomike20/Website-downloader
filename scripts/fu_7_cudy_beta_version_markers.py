#!/usr/bin/env python3
import re,html,json,csv,time,urllib.request,urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed

UA="OpenCudy-FU7-Beta-Markers/1.0"
SOURCES=[
 ("csp25","https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}",90),
 ("upgrade","https://www.cudy.com/blogs/faq/how-to-upgrade-the-firmware-of-cudy-router?page={}",60),
 ("zerotier","https://www.cudy.com/en-gb/blogs/faq/how-to-remote-connect-cudy-router-via-zerotier?page={}",30),
 ("wifi7","https://www.cudy.com/blogs/news/introducing-cudy-wi-fi-7?page={}",15),
 ("downgrade","https://www.cudy.com/en-us/blogs/faq/how-to-downgrade-the-firmware-to-the-older-version-of-mesh-system?page={}",30),
 ("adblock","https://www.cudy.com/blogs/news/try-the-new-ad-block-feature-on-your-wr3000-router-beta-test-invitation-10?page={}",10),
]
# Cudy styles seen: 2.5.11b, 2.3.12Beta, 2.1.15Beta-20240701-080530, 2.5.28b
VER_RE=re.compile(r'(?i)\b(\d+\.\d+\.\d+(?:beta|b)(?:[-_ ]?\d{8}[-_]\d{6})?)\b')
MODEL_RE=re.compile(r'\b(?:WR|LT|M|RE|AP|P|TR|C|X|R)[A-Z0-9+_-]{1,15}(?:\s*(?:V|v)?\d+(?:\.\d+)?)?\b')
FILE_RE=re.compile(r'(?i)\b([A-Za-z0-9_+.-]{2,100}(?:beta|\d+b)[A-Za-z0-9_+.-]*\.(?:bin|zip|img|trx|itb))\b')

def get(url,timeout=30):
 req=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read().decode("utf-8","replace")

def clean(s):
 s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
 s=re.sub(r'(?s)<[^>]+>',' ',s)
 return re.sub(r'\s+',' ',html.unescape(s)).strip()

hits=[]
for kind,tpl,maxp in SOURCES:
 misses=0
 for p in range(1,maxp+1):
  try:txt=clean(get(tpl.format(p)))
  except Exception as e:
   misses+=1
   if misses>=6 and p>10:break
   continue
  misses=0
  for m in VER_RE.finditer(txt):
   a=max(0,m.start()-1200);b=min(len(txt),m.end()+1600)
   ctx=txt[a:b]
   models=sorted(set(MODEL_RE.findall(ctx)))
   hits.append({"source":kind,"page":p,"marker":m.group(1),"models":" | ".join(models),"context":ctx})
  for m in FILE_RE.finditer(txt):
   a=max(0,m.start()-1000);b=min(len(txt),m.end()+1200)
   ctx=txt[a:b]
   models=sorted(set(MODEL_RE.findall(ctx)))
   hits.append({"source":kind,"page":p,"marker":m.group(1),"models":" | ".join(models),"context":ctx})
  time.sleep(.02)

# dedup marker/context
seen=set();uniq=[]
for h in hits:
 k=(h["marker"].lower(),h["source"],h["page"],h["context"][:800].lower())
 if k in seen:continue
 seen.add(k);uniq.append(h)

markers=defaultdict(lambda:{"models":set(),"sources":set(),"contexts":[]})
for h in uniq:
 a=markers[h["marker"]]
 a["models"].update(x.strip() for x in h["models"].split("|") if x.strip())
 a["sources"].add(f'{h["source"]}:p{h["page"]}')
 if len(a["contexts"])<4:a["contexts"].append(h["context"])

agg=[]
for marker,a in markers.items():
 agg.append({"marker":marker,"models":" | ".join(sorted(a["models"])),"sources":" | ".join(sorted(a["sources"])),"context":" || ".join(a["contexts"])})
agg.sort(key=lambda x:x["marker"].lower())

# Query archived Cudy CDN by each marker. Match marker in URL only; no guessing filenames.
SCOPES=["www.cudy.com/cdn/shop/files/*","cdn.shopify.com/s/files/1/0673/4748/0820/files/*"]
def cdx(marker,scope):
 flt="original:.*"+re.escape(marker)+".*"
 params=[("url",scope),("output","json"),("fl","timestamp,original,statuscode,mimetype,digest,length"),("filter","statuscode:200"),("filter",flt),("collapse","urlkey")]
 u="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
 try:
  d=json.loads(get(u,60))
  if not d:return []
  hdr=d[0];return [dict(zip(hdr,r)) for r in d[1:]]
 except:return []

archive=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 jobs={(ex.submit(cdx,m["marker"],s)): (m["marker"],s) for m in agg for s in SCOPES}
 for fut in as_completed(jobs):
  marker,scope=jobs[fut]
  rows=fut.result()
  for o in rows:
   archive.append({"marker":marker,"scope":scope,**o})

with open("fu_7-CUDY-BETA-VERSION-HITS.csv","w",newline="",encoding="utf-8") as f:
 fields=["source","page","marker","models","context"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(uniq)
with open("fu_7-CUDY-BETA-VERSION-MARKERS.csv","w",newline="",encoding="utf-8") as f:
 fields=["marker","models","sources","context"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(agg)
with open("fu_7-CUDY-BETA-VERSION-ARCHIVE.csv","w",newline="",encoding="utf-8") as f:
 fields=["marker","scope","timestamp","original","statuscode","mimetype","digest","length"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(archive)
summary={"unique_markers":len(agg),"markers":[{"marker":x["marker"],"models":x["models"]} for x in agg],"archive_url_hits":len(archive),"archive_hits":archive}
open("fu_7-CUDY-BETA-VERSION-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

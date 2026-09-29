#!/usr/bin/env python3
import os,re,json,csv,urllib.parse,urllib.request,hashlib,time

UA="OpenCudy-FU7-FAQ-Link-Recover/1.0"
TARGETS=[
 {
  "name":"P5-R21-1.15.15-20230616-112055-sysupgrade",
  "pages":[
    "https://www.cudy.com/blogs/faq/how-to-fix-t-mobile-wi-fi-calling-issues-on-p5",
    "https://www.cudy.com/en-ca/blogs/faq/how-to-fix-t-mobile-wi-fi-calling-issues-on-p5",
  ]
 },
 {
  "name":"LT450-R9-1.15.5beta-20221121-180014-flash.bin",
  "pages":["https://www.cudy.com/blogs/faq/beta-firmware-fix-lt18-lt450-lt500-lt500d-and-t-mobile-configuration-issue"]
 },
 {
  "name":"LT500-R9-1.15.5beta-20221121-180014-flash.bin",
  "pages":["https://www.cudy.com/blogs/faq/beta-firmware-fix-lt18-lt450-lt500-lt500d-and-t-mobile-configuration-issue"]
 },
]

def fetch(url,timeout=60):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read(),r.status,dict(r.headers)

def get_snapshots(page):
 params=[
  ("url",page),("output","json"),
  ("fl","timestamp,original,statuscode,digest"),
  ("filter","statuscode:200"),
  ("collapse","digest")
 ]
 u="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
 try:b,_,_=fetch(u,100);d=json.loads(b.decode("utf-8","replace"))
 except Exception as e:
  print("CDX_PAGE_FAIL",page,repr(e));return []
 if not d:return []
 h=d[0];return [dict(zip(h,x)) for x in d[1:]]

def anchors_near(html,marker):
 text=html.decode("utf-8","replace")
 poslist=[]; low=text.lower();m=marker.lower();start=0
 while True:
  i=low.find(m,start)
  if i<0:break
  poslist.append(i);start=i+len(m)
 out=[]
 for p in poslist:
  frag=text[max(0,p-5000):p+5000]
  for mm in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',frag,re.I|re.S):
   href=mm.group(1).replace("&amp;","&")
   label=re.sub(r'<[^>]+>',' ',mm.group(2))
   label=re.sub(r'\s+',' ',label).strip()
   # collect any nearby anchor, but prioritize ones containing target/beta/file
   out.append((href,label))
 return out

allrows=[]; candidates={}
for t in TARGETS:
 marker=t["name"];cand=[]
 for page in t["pages"]:
  snaps=get_snapshots(page)
  print("SNAPS",marker,page,len(snaps))
  # newest and oldest + up to 30 evenly as returned
  for s in snaps[:50]:
   ts=s.get("timestamp","")
   if not ts:continue
   u=f"https://web.archive.org/web/{ts}id_/{page}"
   try:body,_,_=fetch(u,60)
   except Exception as e:continue
   txt=body.decode("utf-8","replace")
   if marker.lower() not in txt.lower():continue
   anchors=anchors_near(body,marker)
   for href,label in anchors:
    full=urllib.parse.urljoin(page,href)
    score=0
    hl=(href+" "+label).lower()
    if marker.lower() in hl:score+=10
    if "beta" in hl:score+=4
    if any(x in hl for x in (".bin",".zip","drive.google.com","cdn","download")):score+=3
    allrows.append({"marker":marker,"page":page,"timestamp":ts,"href":full,"label":label,"score":score})
    if score>=3:cand.append(full)
 # exact/direct archived URLs found in anchor results
 candidates[marker]=list(dict.fromkeys(cand))

# Save links
with open("fu_7-CUDY-BETA-FAQ-LINKS.csv","w",newline="",encoding="utf-8") as f:
 fields=["marker","page","timestamp","href","label","score"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allrows)

# Try best candidate URLs and their Wayback CDX snapshots
os.makedirs("fu_7-CUDY-BETA-FAQ-RECOVERED",exist_ok=True)
recs=[]
for marker,urls in candidates.items():
 expanded=list(urls)
 for orig in urls:
  params=[("url",orig),("output","json"),("fl","timestamp,original,statuscode"),("filter","statuscode:200")]
  try:b,_,_=fetch("https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params),80);d=json.loads(b.decode())
  except:continue
  if d:
   h=d[0]
   for rr in d[1:10]:
    o=dict(zip(h,rr));ts=o.get("timestamp","");oo=o.get("original","")
    if ts and oo:expanded.append(f"https://web.archive.org/web/{ts}id_/{oo}")
 seen=set()
 for u in expanded:
  if u in seen:continue
  seen.add(u)
  try:data,st,h=fetch(u,60)
  except Exception as e:
   recs.append({"marker":marker,"url":u,"result":"FAIL","size":"","sha256":"","saved_as":""});continue
  sha=hashlib.sha256(data).hexdigest()
  head=data[:1024].lower()
  if len(data)<1024 or b"<html" in head or b"<!doctype" in head:
   recs.append({"marker":marker,"url":u,"result":"NON_BINARY","size":len(data),"sha256":sha,"saved_as":""});continue
  fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
  if not fn or "." not in fn:
   fn=re.sub(r'[^A-Za-z0-9._-]','_',marker)+".bin"
  fn=re.sub(r'[^A-Za-z0-9._()+ -]','_',fn)
  p=os.path.join("fu_7-CUDY-BETA-FAQ-RECOVERED",fn)
  if os.path.exists(p):p=os.path.join("fu_7-CUDY-BETA-FAQ-RECOVERED",sha[:8]+"-"+fn)
  open(p,"wb").write(data)
  recs.append({"marker":marker,"url":u,"result":"SAVED","size":len(data),"sha256":sha,"saved_as":os.path.basename(p)})
  print("SAVED",marker,os.path.basename(p),len(data),sha,u)
  break

with open("fu_7-CUDY-BETA-FAQ-RECOVERED-MANIFEST.csv","w",newline="",encoding="utf-8") as f:
 fields=["marker","url","result","size","sha256","saved_as"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(recs)
summary={
 "anchor_rows":len(allrows),
 "candidate_counts":{k:len(v) for k,v in candidates.items()},
 "saved":[r for r in recs if r["result"]=="SAVED"],
}
open("fu_7-CUDY-BETA-FAQ-RECOVERY-SUMMARY.json","w",encoding="utf-8").write(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))

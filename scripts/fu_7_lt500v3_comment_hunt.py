#!/usr/bin/env python3
import html,re,time,urllib.request,json,csv
BASE="https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}"
UA="OpenCudy-FU7-LT500V3-Comments/1.0"
NEEDLES=["LT500D 3.0","LT500 3.0","LT500D V3","LT500 V3"]
def fetch(u):
 req=urllib.request.Request(u,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=30) as r:
  return r.read().decode("utf-8","replace")
def clean(s):
 s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
 s=re.sub(r'(?s)<[^>]+>',' ',s)
 return re.sub(r'\s+',' ',html.unescape(s)).strip()
rows=[]
for p in range(1,61):
 try: txt=clean(fetch(BASE.format(p)))
 except Exception as e:
  print("FAIL",p,repr(e)); continue
 lo=txt.lower()
 for n in NEEDLES:
  start=0
  nl=n.lower()
  while True:
   i=lo.find(nl,start)
   if i<0: break
   ctx=txt[max(0,i-900):min(len(txt),i+1600)]
   rows.append({"page":p,"needle":n,"context":ctx})
   start=i+len(n)
 time.sleep(.03)
# dedup exact context
seen=set();uniq=[]
for r in rows:
 k=r["context"][:1000]
 if k in seen: continue
 seen.add(k);uniq.append(r)
with open("fu_7-LT500V3-COMMENT-HITS.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=["page","needle","context"]);w.writeheader();w.writerows(uniq)
open("fu_7-LT500V3-COMMENT-HITS.json","w",encoding="utf-8").write(json.dumps(uniq,indent=2,ensure_ascii=False))
print(json.dumps({"raw":len(rows),"unique":len(uniq)},indent=2))
for r in uniq:
 print("\n---",r["page"],r["needle"],"---\n",r["context"][:2400])

#!/usr/bin/env python3
import html,re,time,urllib.request,csv,json

BASE="https://www.cudy.com/blogs/news/cudy-software-platform-updates?page={}"
UA="OpenCudy-FU7-LT500-Comment-Hunt/1.0"
TERMS=("lt500d","lt500","r25")
def fetch(u):
 req=urllib.request.Request(u,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=30) as r:
  return r.read().decode("utf-8","replace")
def clean(s):
 s=re.sub(r'(?is)<script.*?</script>|<style.*?</style>',' ',s)
 s=re.sub(r'(?s)<[^>]+>',' ',s)
 s=html.unescape(s)
 return re.sub(r'\s+',' ',s).strip()
hits=[]
empty=0
for p in range(1,81):
 u=BASE.format(p)
 try: raw=fetch(u)
 except Exception as e:
  print("FAIL",p,repr(e)); continue
 txt=clean(raw)
 low=txt.lower()
 # Stop only after several pages beyond known comment pagination with no useful comment-page marker.
 if "comments" not in low and p>60:
  empty+=1
 else: empty=0
 for term in TERMS:
  pos=0
  while True:
   i=low.find(term,pos)
   if i<0:break
   ctx=txt[max(0,i-700):min(len(txt),i+1200)]
   hits.append({"page":p,"term":term,"context":ctx})
   pos=i+len(term)
 if p%10==0: print("PAGE",p,"hits",len(hits))
 if empty>=5:break
 time.sleep(.05)
# Deduplicate near-identical contexts
seen=set(); uniq=[]
for h in hits:
 key=re.sub(r'\s+',' ',h["context"].lower())
 key=key[:900]
 if key in seen: continue
 seen.add(key); uniq.append(h)
with open("fu_7-LT500-CSP25-COMMENT-HITS.csv","w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=["page","term","context"]);w.writeheader();w.writerows(uniq)
open("fu_7-LT500-CSP25-COMMENT-HITS.json","w",encoding="utf-8").write(json.dumps(uniq,indent=2,ensure_ascii=False))
print(json.dumps({"raw_hits":len(hits),"unique_hits":len(uniq),"pages_scanned":p},indent=2))
for h in uniq:
 print("\n--- PAGE",h["page"],h["term"],"---\n",h["context"][:1800])

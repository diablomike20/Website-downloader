#!/usr/bin/env python3
import csv, hashlib, html, json, os, re, shutil, subprocess, urllib.parse, urllib.request, zipfile
from pathlib import Path

UA="OpenCudy-RE-ZeroTier-Stable-Hunt/1.0"
ROOT=Path("RE-ZEROTIER-STABLE-HUNT")
DL=ROOT/"downloads"; EXT=ROOT/"extracted"; FOUND=ROOT/"found"
for p in (ROOT,DL,EXT,FOUND): p.mkdir(parents=True,exist_ok=True)

BASELINE_TOTAL=2140557
BASE_PRESENT={"libc.so","libgcc_s.so.1","ld-musl-mipsel-sf.so.1","ld-musl-mipsel.so.1"}

# Only official public Cudy download centers / stable product families.
PAGES=[
 "https://www.cudy.com/pages/download-center/lt400-1-0",
 "https://www.cudy.com/pages/download-center/lt400-2-0",
 "https://www.cudy.com/pages/download-center/lt400-3-0",
 "https://www.cudy.com/pages/download-center/lt400e-1-0",
 "https://www.cudy.com/pages/download-center/lt400-outdoor-1-0",
 "https://www.cudy.com/pages/download-center/lt450-1-0",
 "https://www.cudy.com/pages/download-center/lt450-2-0",
 "https://www.cudy.com/pages/download-center/lt500-1-0",
 "https://www.cudy.com/pages/download-center/lt500-2-0",
 "https://www.cudy.com/pages/download-center/lt500-3-0",
 "https://www.cudy.com/pages/download-center/lt500e-1-0",
 "https://www.cudy.com/pages/download-center/lt500-outdoor-1-0",
 "https://www.cudy.com/pages/download-center/lt700-1-0",
 "https://www.cudy.com/pages/download-center/lt700-2-0",
 "https://www.cudy.com/pages/download-center/lt700e-1-0",
 "https://www.cudy.com/pages/download-center/wr1200-1-0",
 "https://www.cudy.com/pages/download-center/wr1200-2-0",
 "https://www.cudy.com/pages/download-center/wr1200-3-0",
 "https://www.cudy.com/pages/download-center/wr1300-1-0",
 "https://www.cudy.com/pages/download-center/wr1300-2-0",
 "https://www.cudy.com/pages/download-center/wr1300-3-0",
 "https://www.cudy.com/pages/download-center/wr1300-4-0",
 "https://www.cudy.com/pages/download-center/tr1200-1-0",
 "https://www.cudy.com/pages/download-center/tr1200-2-0",
 "https://www.cudy.com/pages/download-center/m1200-1-0",
 "https://www.cudy.com/pages/download-center/m1200-2-0",
 "https://www.cudy.com/pages/download-center/m1300-1-0",
 "https://www.cudy.com/pages/download-center/m1300-2-0",
 "https://www.cudy.com/pages/download-center/wr1300-5-0",
 "https://www.cudy.com/pages/download-center/wr3000-1-0",
 "https://www.cudy.com/pages/download-center/wr3000-2-0",
 "https://www.cudy.com/pages/download-center/wr3000-3-0",
 "https://www.cudy.com/pages/download-center/lt300-1-0",
 "https://www.cudy.com/pages/download-center/lt300-2-0",
 "https://www.cudy.com/pages/download-center/lt300-3-0",
]

CDN_RE=re.compile(r'''(?i)(?:https?:)?//(?:www\.)?cudy\.com/cdn/shop/files/[^"'<>\s]+?(?:\.zip|\.bin)(?:\?[^"'<>\s]*)?''')
FW_NAME_RE=re.compile(r'''(?i)\b([A-Za-z0-9_+().-]{3,180}(?:flash|sysupgrade)[A-Za-z0-9_+().-]*\.(?:zip|bin))\b''')
STABLE_BAD=re.compile(r'(?i)(beta|alpha|debug|develop|developer|test|preview|intermediate|middle|transition|recovery|\d+b(?:[-_.]|$)|rc\d*)')

def fetch(url,timeout=90):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()

def stable_name(fn):
    return not STABLE_BAD.search(fn)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def safe(s): return re.sub(r'[^A-Za-z0-9._()+ -]+','_',s)[:220]

def collect_urls():
    urls=set(); log=[]
    for page in PAGES:
        try:t=fetch(page,60).decode("utf-8","replace")
        except Exception as e:
            log.append({"page":page,"status":"FAIL","error":repr(e)});continue
        t=html.unescape(t).replace("\\/","/")
        log.append({"page":page,"status":"OK","bytes":len(t)})
        for m in CDN_RE.finditer(t):
            u=m.group(0)
            if u.startswith("//"):u="https:"+u
            u=u.replace("&amp;","&")
            fn=urllib.parse.unquote(urllib.parse.urlsplit(u).path.rsplit("/",1)[-1])
            if stable_name(fn) and ("flash" in fn.lower() or "sysupgrade" in fn.lower()):
                urls.add(u)
        for fn in FW_NAME_RE.findall(t):
            fn=urllib.parse.unquote(fn)
            if stable_name(fn):
                urls.add("https://www.cudy.com/cdn/shop/files/"+fn)
    (ROOT/"RE-STABLE-PAGE-LOG.json").write_text(json.dumps(log,indent=2,ensure_ascii=False))
    return sorted(urls)

def dl(url):
    fn=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/",1)[-1])
    out=DL/safe(fn)
    try:
        b=fetch(url,120)
        if len(b)<1024 or b[:1024].lstrip().lower().startswith((b"<html",b"<!doctype")):return None
        out.write_bytes(b);return out
    except Exception as e:
        print("DOWNLOAD_FAIL",url,repr(e));return None

def run(cmd,t=120):
    try:return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=t).stdout
    except Exception as e:return "ERROR "+repr(e)

def offsets(p):
    b=p.read_bytes();out=[];i=0
    while True:
        i=b.find(b"hsqs",i)
        if i<0:return out
        out.append(i);i+=4

def findlib(root,name):
    for p in root.rglob(name):
        if p.exists():return p
    pref=name.split(".so")[0]+".so"
    for p in root.rglob(pref+"*"):
        if p.exists():return p
    return None

def psize(p):
    try:
        if p.is_symlink():
            q=(p.parent/os.readlink(p)).resolve()
            return q.stat().st_size if q.exists() else 0
        return p.stat().st_size
    except:return 0

urls=collect_urls()
(ROOT/"RE-STABLE-OFFICIAL-URLS.txt").write_text("\n".join(urls)+"\n")
downloads=[]
for u in urls:
    p=dl(u)
    if p:downloads.append((u,p))

images=[]
for src,p in downloads:
    if zipfile.is_zipfile(p):
        d=EXT/(safe(p.name)+".contents");d.mkdir(parents=True,exist_ok=True)
        try:
            with zipfile.ZipFile(p) as z:z.extractall(d)
        except:continue
        for q in d.rglob("*"):
            if q.is_file() and q.suffix.lower() in (".bin",".img",".trx",".itb",".fw",".rom"):
                images.append((src,q))
    else:images.append((src,p))

seen=set(); uniq=[]
for src,p in images:
    try:h=sha(p)
    except:continue
    if h in seen:continue
    seen.add(h);uniq.append((src,p,h))

records=[]
for idx,(src,img,ih) in enumerate(uniq):
    for off in offsets(img)[:4]:
        sq=EXT/f"{idx}-{off:x}.squashfs"
        with open(img,"rb") as f:f.seek(off);sq.write_bytes(f.read())
        root=EXT/f"{idx}-{off:x}.rootfs"
        if root.exists():shutil.rmtree(root)
        run(["unsquashfs","-no-progress","-d",str(root),str(sq)],180)
        if not root.exists():continue
        zts=[p for p in root.rglob("zerotier-one") if p.is_file()]
        for zt in zts:
            dyn=run(["readelf","-d",str(zt)],30)
            needed=re.findall(r"Shared library: \[(.*?)\]",dyn)
            libs=[];extra=0
            for n in needed:
                lp=findlib(root,n);sz=psize(lp) if lp else 0;base=n in BASE_PRESENT
                libs.append({"name":n,"size":sz,"path":str(lp.relative_to(root)) if lp else "MISSING","baseline_present":base})
                if not base:extra+=sz
            zh=sha(zt);logical=zt.stat().st_size+extra
            rel=""
            for rp in (root/"etc/openwrt_release",root/"etc/rom_version",root/"etc/openwrt_version"):
                if rp.exists():
                    try:rel+=rp.read_text("utf-8",errors="ignore").strip()+" | "
                    except:pass
            records.append({
              "source_url":src,"image":img.name,"image_sha256":ih,"release":rel[:500],
              "zerotier_path":str(zt.relative_to(root)),"zerotier_size":zt.stat().st_size,
              "zerotier_sha256":zh,"needed":needed,"libraries":libs,
              "extra_dependency_bytes":extra,"estimated_logical_payload":logical,
              "saving_vs_R25":BASELINE_TOTAL-logical
            })

# Deduplicate ZT binary builds while preserving all stable provenance.
by={}
for r in records:
    h=r["zerotier_sha256"]
    if h not in by:by[h]=r|{"sources":[r["source_url"]+" :: "+r["image"]]}
    else:by[h]["sources"].append(r["source_url"]+" :: "+r["image"])
rows=sorted(by.values(),key=lambda r:(r["estimated_logical_payload"],r["zerotier_size"]))

summary={"official_stable_urls":len(urls),"downloaded_packages":len(downloads),"unique_images_scanned":len(uniq),
         "distinct_zerotier_builds":len(rows),"baseline_payload":BASELINE_TOTAL,"results":rows}
(ROOT/"RE-ZEROTIER-STABLE-HUNT-RESULT.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False))

with open(ROOT/"RE-ZEROTIER-STABLE-HUNT-RESULT.csv","w",newline="",encoding="utf-8-sig") as f:
    fields=["rank","zerotier_size","extra_dependency_bytes","estimated_logical_payload","saving_vs_R25","zerotier_sha256","needed","sources"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for i,r in enumerate(rows,1):
        w.writerow({"rank":i,"zerotier_size":r["zerotier_size"],"extra_dependency_bytes":r["extra_dependency_bytes"],
                    "estimated_logical_payload":r["estimated_logical_payload"],"saving_vs_R25":r["saving_vs_R25"],
                    "zerotier_sha256":r["zerotier_sha256"],"needed":" | ".join(r["needed"]),"sources":" | ".join(r["sources"])})

md=["# RE ZeroTier stable donor hunt","",
    f"Official stable URLs collected: **{len(urls)}**",
    f"Downloaded stable packages: **{len(downloads)}**",
    f"Unique firmware images scanned: **{len(uniq)}**",
    f"Distinct ZeroTier binaries: **{len(rows)}**","",
    "| Rank | zerotier-one | extra deps | estimated payload | saving vs R25 | SHA256 |",
    "|---:|---:|---:|---:|---:|---|"]
for i,r in enumerate(rows,1):
    md.append(f"| {i} | {r['zerotier_size']} | {r['extra_dependency_bytes']} | {r['estimated_logical_payload']} | {r['saving_vs_R25']} | `{r['zerotier_sha256'][:16]}…` |")
md += ["","## Stable provenance"]
for i,r in enumerate(rows,1):
    md.append(f"### {i}. {r['zerotier_sha256']}")
    md.append(f"- NEEDED: {', '.join(r['needed'])}")
    for s in r["sources"]:md.append(f"- {s}")
(ROOT/"RE-ZEROTIER-STABLE-HUNT-RESULT.md").write_text("\n".join(md)+"\n")
print(json.dumps({"stable_urls":len(urls),"downloaded":len(downloads),"images":len(uniq),"zt_builds":len(rows),"best":rows[0] if rows else None},indent=2,ensure_ascii=False))

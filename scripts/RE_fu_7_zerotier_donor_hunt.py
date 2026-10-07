#!/usr/bin/env python3
import csv, hashlib, html, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request, zipfile
from pathlib import Path

UA="OpenCudy-RE-ZeroTier-Donor-Hunt/1.0"
ROOT=Path("RE-ZEROTIER-DONOR-HUNT")
DL=ROOT/"downloads"
EXT=ROOT/"extracted"
FOUND=ROOT/"found"
for p in (ROOT,DL,EXT,FOUND): p.mkdir(parents=True,exist_ok=True)

BASELINE={
 "name":"LT500D V2 / R25 stock",
 "zerotier_one_size":791080,
 "extra_lib_sizes":{
  "libstdc++.so.6":1303867,
  "libminiupnpc.so.17":37279,
  "libnatpmp.so.1":8331
 },
 "logical_total":2140557
}
BASE_PRESENT={"libc.so","libgcc_s.so.1","ld-musl-mipsel-sf.so.1","ld-musl-mipsel.so.1"}

PAGES=[
 "https://www.cudy.com/blogs/faq/how-to-remote-connect-cudy-router-via-zerotier",
 "https://www.cudy.com/pages/download-center/lt400-2-0",
 "https://www.cudy.com/pages/download-center/lt400-3-0",
 "https://www.cudy.com/pages/download-center/lt400e-1-0",
 "https://www.cudy.com/pages/download-center/lt400-outdoor-1-0",
 "https://www.cudy.com/pages/download-center/lt500-2-0",
 "https://www.cudy.com/pages/download-center/lt500-3-0",
 "https://www.cudy.com/pages/download-center/lt500e-1-0",
 "https://www.cudy.com/pages/download-center/lt500-outdoor-1-0",
 "https://www.cudy.com/pages/download-center/lt450-1-0",
 "https://www.cudy.com/pages/download-center/lt450-2-0",
 "https://www.cudy.com/pages/download-center/wr1200-1-0",
 "https://www.cudy.com/pages/download-center/wr1200-2-0",
 "https://www.cudy.com/pages/download-center/wr1200-3-0",
 "https://www.cudy.com/pages/download-center/wr1300-1-0",
 "https://www.cudy.com/pages/download-center/wr1300-2-0",
 "https://www.cudy.com/pages/download-center/wr1300-3-0",
 "https://www.cudy.com/pages/download-center/lt300-2-0",
 "https://www.cudy.com/pages/download-center/lt300-3-0",
 "https://www.cudy.com/pages/download-center/lt15e-1-0",
 "https://www.cudy.com/pages/download-center/lt15v-1-0",
 "https://www.cudy.com/pages/download-center/lt12-1-0",
 "https://www.cudy.com/pages/download-center/lt18-1-0",
 "https://www.cudy.com/pages/download-center/lt700-1-0",
 "https://www.cudy.com/pages/download-center/lt700-2-0",
 "https://www.cudy.com/pages/download-center/lt700e-1-0",
 "https://www.cudy.com/pages/download-center/lt500v-1-0",
 "https://www.cudy.com/pages/download-center/lt400v-1-0",
]

EXACT_URLS=[
 "https://www.cudy.com/cdn/shop/files/LT500V2-R25-1.15.28-20230410-094349-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT450-LT500-LT500DV2-R25-2.1.1-20240419-090237-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT400A-R6-1.15.27-20230404-114529-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT400A-R6-2.1.9-20240522-111245-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT400E-R61-2.1.10-20240527-092607-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT400Outdoor-R40-1.15.34-20230525-155951-flash.zip",
 "https://www.cudy.com/cdn/shop/files/LT400Outdoor-R40-2.1.9-20240522-110221-flash.zip",
]
FW_PREFIX=re.compile(r"(?i)^(LT300|LT400|LT450|LT500|LT700|LT12|LT15|LT18|WR1200|WR1300|WR3000|TR1200|P2)")
CDN_RE=re.compile(r"""(?i)(?:https?:)?//(?:www\.)?cudy\.com/cdn/shop/files/[^"'<>\s]+?(?:\.zip|\.bin)(?:\?[^"'<>\s]*)?""")

def fetch(url, timeout=90, binary=True):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read() if binary else r.read().decode("utf-8","replace")

def safe(s):
    return re.sub(r"[^A-Za-z0-9._()+ -]+","_",s)[:220] or "artifact"

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def collect_official_urls():
    urls=set(EXACT_URLS)
    page_log=[]
    for base in PAGES:
        # some Cudy blog/list pages are paginated; download centers generally are not
        variants=[base]
        if "/blogs/" in base:
            variants += [base+"?page="+str(i) for i in range(1,8)]
        for u in variants:
            try:
                t=fetch(u,60,False)
            except Exception as e:
                page_log.append({"url":u,"status":"FAIL","error":repr(e)})
                continue
            page_log.append({"url":u,"status":"OK","bytes":len(t)})
            t=html.unescape(t).replace("\\/","/")
            for m in CDN_RE.finditer(t):
                x=m.group(0)
                if x.startswith("//"): x="https:"+x
                x=x.replace("&amp;","&")
                fn=urllib.parse.unquote(urllib.parse.urlsplit(x).path.rsplit("/",1)[-1])
                if FW_PREFIX.search(fn) and ("flash" in fn.lower() or fn.lower().endswith(".bin")):
                    urls.add(x)
            # Shopify/download pages often expose the exact filename in text/JSON
            # without a direct href. Canonical /cdn/shop/files/<filename> is a
            # proven Cudy distribution mechanism, so recover those names too.
            for fn in re.findall(r"(?i)\\b([A-Za-z0-9_+().-]{3,180}(?:flash|sysupgrade)[A-Za-z0-9_+().-]*\\.(?:zip|bin))\\b",t):
                fn=urllib.parse.unquote(fn)
                if FW_PREFIX.search(fn):
                    urls.add("https://www.cudy.com/cdn/shop/files/"+fn)
    (ROOT/"official-page-log.json").write_text(json.dumps(page_log,indent=2,ensure_ascii=False))
    return sorted(urls)

def download_url(url, tag):
    fn=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/",1)[-1]) or (tag+".bin")
    out=DL/(safe(tag+"__"+fn))
    if out.exists() and out.stat().st_size>1024: return out
    try:
        data=fetch(url,100,True)
        low=data[:1024].lstrip().lower()
        if len(data)<1024 or low.startswith((b"<!doctype html",b"<html")):
            return None
        out.write_bytes(data)
        return out
    except Exception as e:
        print("DOWNLOAD_FAIL",url,repr(e))
        return None

def download_latest_fu7_artifacts():
    token=os.environ.get("GH_TOKEN","")
    repo=os.environ.get("GITHUB_REPOSITORY","diablomike20/Website-downloader")
    if not token: return []
    arts=[]
    try:
        for page in range(1,21):
            req=urllib.request.Request(
                f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=100&page={page}",
                headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json",
                         "X-GitHub-Api-Version":"2022-11-28","User-Agent":UA})
            with urllib.request.urlopen(req,timeout=60) as r:
                batch=json.load(r).get("artifacts",[])
            if not batch: break
            arts.extend(batch)
            if len(batch)<100: break
    except Exception as e:
        print("ARTIFACT_LIST_FAIL",repr(e))
    arts=[a for a in arts if not a.get("expired")]
    arts.sort(key=lambda a:a.get("created_at",""),reverse=True)
    wanted=[
      "fu_7-CUDY-DEV-FIRMWARE-CLEAN-MASTER",
      "fu_7-CUDY-DEV-FIRMWARE-MASTER",
      "fu_7-CUDY-DEV-BUILD-BATCH-01",
      "fu_7-CUDY-DEV-CDN-ARCHIVE-HUNT",
      "fu_7-RECOVERED-CUDY-BETAS",
      "fu_7-CUDY-BETA-FAQ-RECOVERY",
    ]
    chosen=[]
    used=set()
    for a in arts:
        n=a.get("name","")
        if n in wanted and n not in used:
            chosen.append(a);used.add(n)
    # FU7 handoff-proven clean firmware master. Keep as deterministic fallback
    # while it remains available (30-day Actions retention).
    if not any(int(a.get("id",0))==11068611598 for a in chosen):
        chosen.append({"id":11068611598,"name":"fu_7-CUDY-DEV-FIRMWARE-CLEAN-MASTER-HANDOFF-ID"})
    out=[]
    for a in chosen:
        url=f"https://api.github.com/repos/{repo}/actions/artifacts/{a['id']}/zip"
        p=DL/(f"FU7_ARTIFACT_{a['id']}__{safe(a['name'])}.zip")
        req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json",
                                               "X-GitHub-Api-Version":"2022-11-28","User-Agent":UA})
        try:
            with urllib.request.urlopen(req,timeout=120) as r: p.write_bytes(r.read())
            out.append(p)
            print("FU7_ARTIFACT",a["id"],a["name"],p.stat().st_size)
        except Exception as e: print("ARTIFACT_DOWNLOAD_FAIL",a.get("id"),n,repr(e))
    return out

def extract_zip_recursive(p, dest, depth=0):
    if depth>4:return
    try:
        with zipfile.ZipFile(p) as z:
            z.extractall(dest)
    except Exception:
        return
    for q in list(Path(dest).rglob("*.zip")):
        if q.resolve()==Path(p).resolve(): continue
        nd=q.parent/(q.name+".contents")
        if nd.exists(): continue
        nd.mkdir(parents=True,exist_ok=True)
        extract_zip_recursive(q,nd,depth+1)

def squashfs_offsets(p):
    data=p.read_bytes()
    out=[]; start=0
    while True:
        i=data.find(b"hsqs",start)
        if i<0:break
        out.append(i); start=i+4
    return out

def read_text(p):
    try:return p.read_text("utf-8",errors="ignore")
    except:return ""

def run(cmd, timeout=90):
    try:return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout).stdout
    except Exception as e:return "ERROR "+repr(e)

def find_lib(root,name):
    exact=[]
    for p in root.rglob(name):
        if p.is_file() or p.is_symlink(): exact.append(p)
    if exact:return exact[0]
    # SONAME may point to versioned file
    stem=name.split(".so")[0]+".so"
    for p in root.rglob(stem+"*"):
        if p.is_file() or p.is_symlink(): return p
    return None

def resolved_size(p):
    try:
        if p.is_symlink():
            target=(p.parent/os.readlink(p)).resolve()
            return target.stat().st_size if target.exists() else 0
        return p.stat().st_size
    except:return 0

def extract_rootfs(image, label, idx):
    offs=squashfs_offsets(image)
    roots=[]
    for off in offs[:4]:
        sq=EXT/(safe(label)+f"__{idx}__{off:x}.squashfs")
        with open(image,"rb") as f:
            f.seek(off); sq.write_bytes(f.read())
        root=EXT/(safe(label)+f"__{idx}__{off:x}.rootfs")
        if root.exists():shutil.rmtree(root)
        out=run(["unsquashfs","-no-progress","-d",str(root),str(sq)],150)
        if root.exists() and any(root.iterdir()): roots.append((off,root,out))
    return roots

def zt_version(binary):
    s=run(["strings","-a",str(binary)],60)
    lines=[x.strip() for x in s.splitlines()]
    near=[x for x in lines if "zerotier" in x.lower() and re.search(r"\b\d+\.\d+\.\d+\b",x)]
    if near:
        m=re.search(r"\b\d+\.\d+\.\d+\b",near[0]); return m.group(0) if m else near[0][:120]
    # conservative fallback: candidate semantic versions; report only if unique-ish
    vals=[]
    for x in lines:
        vals += re.findall(r"\b(?:0|1|2)\.\d+\.\d+\b",x)
    vals=sorted(set(vals))
    return vals[0] if len(vals)==1 else "UNKNOWN"

def inspect_root(root, source, image, off):
    zts=[]
    for p in root.rglob("*"):
        if p.is_file() and p.name=="zerotier-one": zts.append(p)
    if not zts:return []
    recs=[]
    release=""
    for rp in [root/"etc/openwrt_release",root/"etc/openwrt_version",root/"etc/rom_version"]:
        if rp.exists(): release += read_text(rp).strip()+" | "
    for zt in zts:
        elf=run(["readelf","-h",str(zt)],30)
        dyn=run(["readelf","-d",str(zt)],30)
        needed=re.findall(r"Shared library: \[(.*?)\]",dyn)
        libs=[]; extra=0
        for n in needed:
            p=find_lib(root,n)
            sz=resolved_size(p) if p else 0
            base=(n in BASE_PRESENT)
            libs.append({"name":n,"path":str(p.relative_to(root)) if p else "MISSING","size":sz,"baseline_present":base})
            if not base: extra+=sz
        logical=zt.stat().st_size+extra
        sha=sha256_file(zt)
        copydir=FOUND/sha[:16]
        copydir.mkdir(parents=True,exist_ok=True)
        shutil.copy2(zt,copydir/"zerotier-one")
        for l in libs:
            if l["baseline_present"] or l["path"]=="MISSING":continue
            p=root/l["path"]
            try:
                real=p.resolve()
                shutil.copy2(real,copydir/safe(real.name))
            except: pass
        recs.append({
          "source":source,"image":image.name,"squashfs_offset":off,
          "release":release[:500],"zerotier_path":str(zt.relative_to(root)),
          "zerotier_size":zt.stat().st_size,"zerotier_sha256":sha,
          "version":zt_version(zt),"elf_header":" | ".join(x.strip() for x in elf.splitlines() if any(k in x for k in ("Class:","Data:","Machine:","Flags:"))),
          "needed":needed,"libraries":libs,"extra_dependency_bytes":extra,
          "estimated_logical_payload":logical,
          "savings_vs_R25":BASELINE["logical_total"]-logical,
        })
    return recs

official=collect_official_urls()
(ROOT/"official-firmware-urls.txt").write_text("\n".join(official)+"\n")
downloads=[]
for i,u in enumerate(official[:90]):
    p=download_url(u,"official")
    if p:downloads.append(p)
downloads += download_latest_fu7_artifacts()

# expand every ZIP and gather likely firmware/raw images
candidates=[]
for p in downloads:
    if zipfile.is_zipfile(p):
        d=EXT/(safe(p.name)+".contents")
        d.mkdir(parents=True,exist_ok=True)
        extract_zip_recursive(p,d)
        for q in d.rglob("*"):
            if not q.is_file():continue
            if q.suffix.lower() in (".bin",".img",".trx",".itb",".fw",".rom") or b"hsqs" in q.read_bytes()[:16*1024*1024]:
                candidates.append((p.name,q))
    else:candidates.append((p.name,p))

# de-duplicate images by SHA
uniq=[];seen=set()
for src,p in candidates:
    try:h=sha256_file(p)
    except:continue
    if h in seen:continue
    seen.add(h);uniq.append((src,p,h))

records=[]
for idx,(src,p,h) in enumerate(uniq):
    try:
        roots=extract_rootfs(p,src+"__"+p.name,idx)
    except Exception as e:
        print("ROOTFS_FAIL",p,repr(e));continue
    for off,root,_ in roots:
        records += inspect_root(root,src,p,off)

# dedupe ZeroTier builds by hash, preserve all provenance
by={}
for r in records:
    h=r["zerotier_sha256"]
    if h not in by: by[h]=r|{"all_sources":[r["source"]+" :: "+r["image"]]}
    else: by[h]["all_sources"].append(r["source"]+" :: "+r["image"])
rows=list(by.values())
rows.sort(key=lambda r:(r["estimated_logical_payload"],r["zerotier_size"]))

(ROOT/"RE-ZEROTIER-DONOR-HUNT-RESULT.json").write_text(json.dumps({
 "baseline":BASELINE,"official_urls":official,"unique_images_scanned":len(uniq),
 "zerotier_builds_found":len(rows),"results":rows
},indent=2,ensure_ascii=False))

with open(ROOT/"RE-ZEROTIER-DONOR-HUNT-RESULT.csv","w",newline="",encoding="utf-8-sig") as f:
    fields=["rank","version","zerotier_size","extra_dependency_bytes","estimated_logical_payload","savings_vs_R25",
            "zerotier_sha256","needed","release","all_sources"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for i,r in enumerate(rows,1):
        w.writerow({
          "rank":i,"version":r["version"],"zerotier_size":r["zerotier_size"],
          "extra_dependency_bytes":r["extra_dependency_bytes"],
          "estimated_logical_payload":r["estimated_logical_payload"],
          "savings_vs_R25":r["savings_vs_R25"],"zerotier_sha256":r["zerotier_sha256"],
          "needed":" | ".join(r["needed"]),"release":r["release"],
          "all_sources":" | ".join(r["all_sources"])
        })

md=["# RE ZeroTier donor hunt","",f"Unique firmware images scanned: **{len(uniq)}**",f"Distinct ZeroTier binaries found: **{len(rows)}**","",
    f"R25 baseline logical payload: **{BASELINE['logical_total']} bytes**","",
    "| Rank | Version | zerotier-one | extra deps | estimated payload | saving vs R25 | SHA256 |",
    "|---:|---|---:|---:|---:|---:|---|"]
for i,r in enumerate(rows,1):
    md.append(f"| {i} | {r['version']} | {r['zerotier_size']} | {r['extra_dependency_bytes']} | {r['estimated_logical_payload']} | {r['savings_vs_R25']} | `{r['zerotier_sha256'][:16]}…` |")
if not rows: md += ["","**No complete zerotier-one runtime was found in the scanned firmware set.**"]
md += ["","## Provenance"]
for i,r in enumerate(rows,1):
    md.append(f"### {i}. {r['version']} — {r['zerotier_sha256']}")
    md.append(f"- NEEDED: {', '.join(r['needed']) or 'none/unknown'}")
    md.append(f"- Sources: {'; '.join(r['all_sources'])}")
(ROOT/"RE-ZEROTIER-DONOR-HUNT-RESULT.md").write_text("\n".join(md)+"\n")

print(json.dumps({"unique_images_scanned":len(uniq),"zerotier_builds_found":len(rows),
                  "best":rows[0] if rows else None},indent=2,ensure_ascii=False))

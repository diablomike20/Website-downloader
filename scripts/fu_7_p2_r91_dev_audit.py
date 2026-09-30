#!/usr/bin/env python3
import csv, hashlib, json, os, re, shutil, subprocess, sys, urllib.request, zipfile, tarfile
from pathlib import Path

ARTIFACT_ID = "11066088105"
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GH_TOKEN"]
ROOT = Path(".")
SRC = ROOT/"src"
WORK = ROOT/"work"
REPORT = ROOT/"report"
for d in (SRC, WORK, REPORT, REPORT/"rootfs"):
    d.mkdir(parents=True, exist_ok=True)

def sh(args, **kw):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw)

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def download_artifact():
    url=f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT_ID}/zip"
    subprocess.run([
        "curl","-L","--fail","--retry","2",
        "-H",f"Authorization: Bearer {TOKEN}",
        "-H","Accept: application/vnd.github+json",
        "-H","X-GitHub-Api-Version: 2022-11-28",
        url,"-o",str(SRC/"artifact.zip")
    ],check=True)
    with zipfile.ZipFile(SRC/"artifact.zip") as z:
        z.extractall(SRC/"artifact")

def recursive_unpack():
    roots=[SRC/"artifact"]
    seen=set()
    for depth in range(5):
        new=[]
        for root in roots:
            for p in root.rglob("*"):
                if not p.is_file() or p in seen: continue
                low=p.name.lower()
                if low.endswith(".zip"):
                    seen.add(p)
                    d=WORK/(re.sub(r"[^A-Za-z0-9._-]+","_",p.name)+f".d{depth}")
                    d.mkdir(parents=True, exist_ok=True)
                    try:
                        with zipfile.ZipFile(p) as z:z.extractall(d)
                        new.append(d)
                    except Exception:
                        pass
                elif low.endswith((".tar",".tgz",".tar.gz")):
                    seen.add(p)
                    d=WORK/(re.sub(r"[^A-Za-z0-9._-]+","_",p.name)+f".d{depth}")
                    d.mkdir(parents=True, exist_ok=True)
                    try:
                        with tarfile.open(p) as t:t.extractall(d)
                        new.append(d)
                    except Exception:
                        pass
        roots.extend(new)
        if not new: break

def collect_payloads():
    payloads=[]
    seen_sha=set()
    for root in (SRC/"artifact", WORK):
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".bin",".img",".itb"):
                s=sha256_file(p)
                if s not in seen_sha:
                    seen_sha.add(s); payloads.append(p)
    payloads.sort(key=lambda p:p.name)
    (REPORT/"payloads.txt").write_text("\n".join(map(str,payloads))+"\n")
    return payloads

def identify(payloads):
    rows=[]
    for p in payloads:
        ft=sh(["file","-b",str(p)]).stdout.strip()
        data=p.read_bytes()
        magics={
            "squashfs_le":[m.start() for m in re.finditer(b"hsqs",data)],
            "squashfs_be":[m.start() for m in re.finditer(b"sqsh",data)],
            "uboot_uimage":[m.start() for m in re.finditer(b"\x27\x05\x19\x56",data)],
            "fit_fdt":[m.start() for m in re.finditer(b"\xd0\x0d\xfe\xed",data)],
            "ubi":[m.start() for m in re.finditer(b"UBI#",data)]
        }
        rows.append({"path":str(p),"name":p.name,"size":p.stat().st_size,"sha256":sha256_file(p),"file":ft,"magics":magics})
        (REPORT/(p.name+".binwalk.txt")).write_text(sh(["binwalk",str(p)]).stdout)
        st=sh(["strings","-a","-n","5",str(p)]).stdout
        (REPORT/(p.name+".strings.txt")).write_text(st,errors="replace")
        rx=re.compile(r"developer|development|debug|factory|engineering|diagnostic|diag|packet.?capture|pcap|tcpdump|telnet|dropbear|ssh|uart|console|shell|terminal|hidden|feature.?flag|capabilit|resolver|description\.lua|gui\.lua|rpcd|ubus|fw_(?:print|set)env|mtd|signature|verify|md5|rsa|test.?mode|eng.?mode|factory.?mode|logread|sysupgrade|upgrade",re.I)
        hits=[f"{i+1}:{line}" for i,line in enumerate(st.splitlines()) if rx.search(line)]
        (REPORT/(p.name+".keyword-strings.txt")).write_text("\n".join(hits[:5000]),errors="replace")
    json.dump(rows,open(REPORT/"payload-identification.json","w"),indent=2)
    with open(REPORT/"payload-identification.tsv","w") as f:
        f.write("name\tsize\tsha256\tfile\tmagics\n")
        for r in rows:
            f.write(f"{r['name']}\t{r['size']}\t{r['sha256']}\t{r['file']}\t{json.dumps(r['magics'])}\n")
    return rows

def extract_ubi(rows):
    roots=[]
    for r in rows:
        src=Path(r["path"])
        offs=r["magics"].get("ubi",[])
        if not offs: continue
        off=offs[0]
        sliced=WORK/(src.name+f".ubi_off_{off}.bin")
        with open(src,"rb") as fi, open(sliced,"wb") as fo:
            fi.seek(off); shutil.copyfileobj(fi,fo,1024*1024)
        info=sh(["ubireader_display_info",str(sliced)])
        (REPORT/(src.name+".ubi-info.txt")).write_text(info.stdout)
        outimg=WORK/(src.name+".ubi-volumes")
        outimg.mkdir(parents=True,exist_ok=True)
        ex=sh(["ubireader_extract_images","-o",str(outimg),str(sliced)])
        (REPORT/(src.name+".ubi-extract.log")).write_text(ex.stdout)
        for vol in outimg.rglob("*"):
            if not vol.is_file(): continue
            try:
                head=vol.read_bytes()[:4]
            except: continue
            if head==b"hsqs":
                out=REPORT/"rootfs"/(src.name+"__ubi__"+vol.name)
                rc=sh(["unsquashfs","-no-exit-code","-d",str(out),str(vol)])
                (REPORT/"rootfs"/(out.name+".unsquashfs.log")).write_text(rc.stdout)
                if out.exists() and any(out.iterdir()): roots.append(out)
            elif head==b"UBI#":
                pass
        # ubireader_extract_files may directly extract UBIFS-based volumes too.
        outf=REPORT/"rootfs"/(src.name+"__ubireader_files")
        exf=sh(["ubireader_extract_files","-o",str(outf),str(sliced)])
        (REPORT/"rootfs"/(src.name+".ubireader-files.log")).write_text(exf.stdout)
        if outf.exists():
            for d in outf.rglob("*"):
                if d.is_dir() and any(d.iterdir()):
                    # collect only directories that look like Linux roots
                    if (d/"etc").exists() and ((d/"www").exists() or (d/"usr").exists()):
                        roots.append(d)
    # de-dup
    seen=set(); out=[]
    for r in roots:
        s=str(r)
        if s not in seen:seen.add(s);out.append(r)
    return out

def extract_squashfs(rows):
    roots=[]
    for r in rows:
        src=Path(r["path"])
        for idx,off in enumerate(r["magics"]["squashfs_le"]):
            chunk=WORK/(src.name+f".sqfs.{idx}")
            with open(src,"rb") as fi, open(chunk,"wb") as fo:
                fi.seek(off)
                shutil.copyfileobj(fi,fo,1024*1024)
            out=REPORT/"rootfs"/(src.name+f"__sqfs_{idx}_off_{off}")
            rc=sh(["unsquashfs","-no-exit-code","-d",str(out),str(chunk)])
            (REPORT/"rootfs"/(out.name+".unsquashfs.log")).write_text(rc.stdout)
            if out.exists() and any(out.iterdir()):
                roots.append(out)
    return roots

RX = re.compile(r"developer|development|debug|factory|engineering|diagnostic|packet.?capture|pcap|tcpdump|telnet|dropbear|ssh|uart|console|shell|terminal|hidden|feature.?flag|capabilit|resolver|description\.lua|gui\.lua|rpcd|ubus|fw_(?:print|set)env|mtd|signature|verify|md5|rsa|test.?mode|eng.?mode|factory.?mode|logread",re.I)
UIRX = re.compile(r"entry\(|alias\(|call\(|template\(|cbi\(|developer|factory|debug|diag|packet|capture|terminal|shell|ssh|telnet|logread|upgrade|firmware|feature|capabilit",re.I)

def audit_rootfs(roots):
    files=[]
    interest=[]
    keyword=[]
    ui=[]
    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file(): continue
            rel=str(p)
            files.append(rel)
            low=rel.lower()
            if any(x in low for x in ("/www/","/usr/lib/lua/","/usr/share/rpcd/","/etc/config/","/etc/init.d/","/usr/bin/","/usr/sbin/","/lib/upgrade/","description.lua","gui.lua","feature","developer","factory","debug","diag")):
                interest.append(rel)
            try:
                if p.stat().st_size <= 5_000_000:
                    text=p.read_text("utf-8",errors="ignore")
                    hs=[f"{i+1}:{line}" for i,line in enumerate(text.splitlines()) if RX.search(line)]
                    if hs:
                        keyword.append("===== "+rel+" =====")
                        keyword.extend(hs[:80])
                    if ("/usr/lib/lua/" in low or "/www/" in low) and p.stat().st_size<=3_000_000:
                        us=[f"{i+1}:{line}" for i,line in enumerate(text.splitlines()) if UIRX.search(line)]
                        if us:
                            ui.append("===== "+rel+" =====")
                            ui.extend(us[:120])
            except Exception:
                pass
    (REPORT/"rootfs-files.txt").write_text("\n".join(sorted(files)))
    (REPORT/"rootfs-interesting-files.txt").write_text("\n".join(sorted(interest)))
    (REPORT/"rootfs-keyword-hits.txt").write_text("\n".join(keyword))
    (REPORT/"ui-route-hits.txt").write_text("\n".join(ui))

def tree(root):
    d={}
    for p in root.rglob("*"):
        if p.is_file():
            rel=str(p.relative_to(root))
            d[rel]=(p.stat().st_size,sha256_file(p))
    return d

def compare_roots(roots):
    stable=[p for p in roots if "2.4.22-20251204-184925" in p.name]
    beta=[p for p in roots if "2.4.29b-20260422-101502" in p.name]
    out={"stable_roots":[str(x) for x in stable],"beta_roots":[str(x) for x in beta],"only_beta":[],"only_stable":[],"changed":[]}
    if stable and beta:
        a=tree(stable[0]); b=tree(beta[0])
        out["only_beta"]=sorted(set(b)-set(a))
        out["only_stable"]=sorted(set(a)-set(b))
        out["changed"]=sorted(k for k in set(a)&set(b) if a[k]!=b[k])
    json.dump(out,open(REPORT/"router-rootfs-diff.json","w"),indent=2)
    return out

def make_summary(rows,diff):
    parts=[]
    parts.append("===== PAYLOAD IDENTIFICATION =====")
    parts.append((REPORT/"payload-identification.tsv").read_text(errors="ignore"))
    parts.append("\n===== INTERESTING ROOTFS FILES =====")
    parts.append("\n".join((REPORT/"rootfs-interesting-files.txt").read_text(errors="ignore").splitlines()[:1000]))
    parts.append("\n===== KEYWORD HITS =====")
    parts.append("\n".join((REPORT/"rootfs-keyword-hits.txt").read_text(errors="ignore").splitlines()[:2500]))
    parts.append("\n===== UI ROUTE HITS =====")
    parts.append("\n".join((REPORT/"ui-route-hits.txt").read_text(errors="ignore").splitlines()[:2000]))
    parts.append("\n===== ROUTER ROOTFS DIFF =====")
    parts.append(json.dumps(diff,indent=2))
    (REPORT/"fu_7-P2-R91-DEV-AUDIT.txt").write_text("\n".join(parts),errors="replace")

download_artifact()
recursive_unpack()
payloads=collect_payloads()
rows=identify(payloads)
roots=extract_squashfs(rows)
roots.extend(extract_ubi(rows))
# Raw beta-only string delta independent of filesystem extraction.
stable=[r for r in rows if "2.4.22-20251204-184925" in r["name"]]
beta=[r for r in rows if "2.4.29b-20260422-101502" in r["name"]]
if stable and beta:
    sa=set((REPORT/(stable[0]["name"]+".strings.txt")).read_text(errors="ignore").splitlines())
    sb=set((REPORT/(beta[0]["name"]+".strings.txt")).read_text(errors="ignore").splitlines())
    only=sorted(sb-sa)
    (REPORT/"beta-only-strings.txt").write_text("\n".join(only))
    rx=re.compile(r"developer|development|debug|factory|engineering|diagnostic|diag|packet.?capture|pcap|tcpdump|telnet|dropbear|ssh|uart|console|shell|terminal|hidden|feature|capabilit|resolver|rpcd|ubus|mtd|signature|verify|md5|rsa|test.?mode|eng.?mode|factory.?mode|logread|root|admin|support|at\+|gcom|modem|cellular",re.I)
    (REPORT/"beta-only-interesting-strings.txt").write_text("\n".join(x for x in only if rx.search(x)))
audit_rootfs(roots)
diff=compare_roots(roots)
make_summary(rows,diff)
print("PAYLOADS",len(rows))
print("ROOTFS",len(roots))
print("ONLY_BETA",len(diff["only_beta"]),"ONLY_STABLE",len(diff["only_stable"]),"CHANGED",len(diff["changed"]))
for r in rows: print(r["name"],r["size"],r["sha256"],r["magics"])

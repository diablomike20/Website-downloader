
# fu_6 — Cudy LT500D / OpenCudy teljes projekt-dokumentáció

## 0. Dokumentum célja és scope-ja

Ez a dokumentum a **teljes OpenCudy projektet** írja le, nem csak a legutóbbi C200P/firmware-vadászatot. A projekt az évek/iterációk során több párhuzamos szakágra vált szét:

- donor firmware reverse engineering;
- web/emulator forensics;
- frontend / UI fidelity;
- target backend/integration;
- OPKG/package manager;
- theme/branding;
- Developer/engineering felület;
- fizikailag tesztelt R25 engineering állapotok;
- firmware-unlock / OTA / cloud / CSP2.5 kutatás;
- emulator archívum és automatikus forensics.

Az aktuális P0 ugyan a **R25 CSP2.5 exact firmware-artifact**, de az utódnak a teljes projekt kontextusát ismernie kell, mert az artifact auditja, a későbbi OpenCudy integráció és a target safety mind a korábbi ágak eredményeire épül.

---

# 1. Fő projektcél

A hosszú távú cél:

> **Cudy LT500D / R25 hardveren olyan OpenCudy rendszert létrehozni, amely a gyári Cudy/LEDE felület és funkcionális jelentés lehető legnagyobb donor-fidelityjét tartja meg, miközben a kívánt modernebb OpenWrt 23.05.5 runtime/integrációs célokkal együtt fejleszthető és auditálható.**

A történelmi frontend/integration ág alapelve:

- **gyári Cudy/LEDE UI = UX / donor etalon**
- **OpenWrt 23.05.5 = target runtime**
- nem redesign;
- nem stock OpenWrt LuCI kinézet;
- nem kitalált donor funkció;
- ahol donor evidence van, azt követni kell;
- ahol nincs evidence, `UNKNOWN`, `BLOCKED_BY_*`, `Unavailable`, `Integration required`, stb.

A firmware-unlock ág ettől részben elkülönül: ott a fizikai R25 gyári/engineering firmware-lineage, Cudy CSP2.5, OTA/cloud mechanika és exact firmware-artifact kutatása a cél.

---

# 2. Hardver és target-truth

## 2.1 Elsődleges target

**Cudy LT500D V2.0**

Bizonyított fő identity:

- board/devtype: `R25`
- régió: EU
- country: DE
- SoC: MediaTek MT7628AN
- RAM: 128 MiB
- flash: 16 MiB NOR
- modem: `EC200AELV1LAR02A03M08`
- működő cellular interface: `usb0`
- `bdinfo checkuuid = OK`

A fizikai R25 **mindig authoritative target**.

## 2.2 Stock R25 referencia

Kanonikus stock firmware:

`LT500V2-R25-2.4.16-20250804-150319`

Stock outer flash SHA-256:

`57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

Stock extracted rootfs ZIP SHA-256:

`f587fa2c36d479e0a6223191546f9db5df6482ff2099d761ddd646d9b89a6fb0`

Platform:

- LEDE 17.01.5
- ramips / mt76x8
- mipsel_24kc

Ez a **stock R25 truth** package/kernel/modem/web/backend összevetésekhez.

## 2.3 R100 CSP2.5 donor

Kanonikus donor:

`LT300V3-R100-2.5.12-20260518-234632`

Package SHA-256:

`8cd02de01b9db1caff6046d65768c9ce6f2c8db0913f6f7faa831971b5e46653`

Inner flash:
- MD5 `7c8cf596029d0ce5940c5bafbb7a0fbd`
- SHA-256 `03641ed863911618155ddb55ed2c45f4c23abd330a4e171bff4491ffcda49a82`

**R100 donor only.** Mechanika, új CSP2.5 userspace, naming, activation és generációs változások vizsgálatára használható; **soha nem bizonyít official R25 firmware-t**.

## 2.4 Hybrid / „R125” engineering állapot

A fizikai R25-en később CSP2.5 eredetű hybrid userspace futott:

- `system.board.rom = R25`
- `/etc/rom_version = 2.5.12-20260518-234632`
- `bdinfo checkuuid = OK`

Helyes megfogalmazás:

`TARGET_VERIFIED: fizikai R25 + CSP2.5 2.5.12 hybrid userspace/version state`

Helytelen:

`official R25 2.5.12 firmware`

Az official R25 2.5.12 státusz **nem bizonyított**.

A hybrid testbed fontos labor, de **nem artifact truth source**.

---

# 3. Evidence discipline

A projektben használt fő evidence-osztályok:

- `TARGET_VERIFIED` — fizikai R25 targeten mért.
- `SOURCE_VERIFIED` — donor/source/rootfs/binary által közvetlenül bizonyított.
- `R25_SOURCE_VERIFIED` — kifejezetten stock R25 source-ból bizonyított.
- `WEB_VERIFIED` — publikus weboldalból bizonyított.
- `EMULATOR_VERIFIED` — Cudy emulator source/runtime snapshotból bizonyított.
- `CROSS_DONOR_CORROBORATED` — más Cudy modellen megerősített mechanika.
- `ARCHITECTURAL_LEAD` — hasznos szerkezeti nyom, de nem target truth.
- `STRONG ARCHITECTURAL INFERENCE` — több független nyom által támogatott inference.
- `SOURCE_GAP` — a forrás nem áll rendelkezésre vagy nem bizonyítja.
- `UNKNOWN / NOT FOUND` — nincs bizonyíték/találat.
- `TARGET_REQUIRED` — fizikailag a routeren kell mérni.

Alapelv:

> Emulator/donor/private/support inference nem válik automatikusan target-truthvá.

---

# 4. Szakágak és ownership

## 4.1 EM — Emulator/Web Forensics

Feladata:
- donor emulator HTML/JS/XHR útvonalak;
- route/page/field/endpoint inventory;
- dashboard states;
- More Details route;
- polling/get semantics;
- DOM/visual evidence;
- statikus emulator mock backend megfejtése.

Nem feladata:
- firmware binary RE;
- target backend implementáció.

## 4.2 RE — Reverse Engineering

Feladata:
- firmware/rootfs;
- Lua controller/model/view/helper;
- shell;
- binary;
- UCI;
- modem stack;
- endpoint/backend chain;
- hidden/developer funkciók donor-source oldala.

Nem feladata:
- általános UI redesign;
- kumulatív build ownership.

## 4.3 WS — Workspace / Frontend

Feladata:
- donor-fidelity frontend;
- route/navigation;
- komponensek;
- target-adapter;
- state handling;
- failure isolation;
- visual structure.

Nem hozhat létre saját backend truthot.

## 4.4 Integration / Boss

Feladata:
- target backend/CGI;
- konfliktusfeloldás;
- branch merge;
- cumulative Truth build;
- release-chain QA;
- végső integration gate.

---

# 5. Frontend / Integration lineage

A projekt több generáción át fejlődött: V63/V66/V67/V68, majd V69.

## 5.1 V68 → V69

Fontos baseline:

`RE-LT500D-V68-WIP-LEDE-DASHBOARD-TRUTH-02.zip`

SHA-256:

`5ec53ce32cd2c3b7aaedc2195b9d1a17fcf863a14304088d1646191ed193340d`

V69 Truth-01:

`RE-LT500D-V69-WIP-LEDE-DASHBOARD-TRUTH-01.zip`

SHA-256:

`589da324661e30038f8762bb3e71b9f622efa9617cc9145d4287e80b532ac757`

Későbbi, történelmileg legfrissebb dokumentált kumulatív V69 build:

`RE-LT500D-V69-WIP-LEDE-DASHBOARD-TRUTH-04.zip`

SHA-256:

`e8e2f65fedb5d30a445a221f6f868c4fc50b861a9c441693d9ea4bf5932c36e0`

Truth-04:
- háromutas merge WS Big Bundle-02-vel;
- EQOS/Firmware/EM63 korábbi javítások megtartva;
- 11 módosított fájl;
- 8 új fájl;
- 0 törlés;
- WISP Status/Settings + 2.4/5 GHz host scan/join struktúra;
- SMS Inbox/New Message/Outbox;
- WAN DHCP/PPPoE/Static/L2TP/PPTP read-only formok;
- donor-source Devices oszlopok + Device Information;
- nem bizonyított write/runtime actionök letiltva.

Regression:
- frontend audit PASS;
- backend audit PASS;
- registry audit PASS;
- Devices/route PASS;
- state-completion PASS;
- CGI syntax + 0755 PASS;
- `FINAL_TRUTH04_ZIP_AUDIT=PASS`.

Ez történelmi integration truth; a firmware-unlock/hybrid target későbbi fizikai állapotai nem azonosak ezzel a 23.05.5 frontend build-vonallal.

---

# 6. WS / frontend részletes eredmények

A V69 WS branch ténylegesen a Truth-02 source-on dolgozott.

## 6.1 WISP state fidelity

Donor raw state mapping:

- `start` / `init` → Initialize
- `scan` → Scanning
- `connect` → Connecting
- `fail` → Connection failed
- `success` → Connected
- `stop` → Not connected
- `roam` → Roaming

Donor raw state elsőbbséget kapott a target netifd fallbackkel szemben.

## 6.2 Diagnostics

Korábban túl sok funkció lett donor-truthként feltételezve.

Korrigált állapot:
- `/admin/tools` shell WEB_VERIFIED;
- deep DOM ahol nem bizonyított: `BLOCKED_BY_EM`;
- nincs kitalált Ping/Traceroute/NSLookup/System Log tile, ha donor evidence nem zárja le.

Későbbi emulator evidence viszont bizonyított Diagnostic Tools struktúrákat is adott; ezek verzióspecifikus donor evidence-ként kezelendők.

## 6.3 Frontend async/stale handling

`async:false` eltávolítva.

Bevezetve:
- loading;
- error;
- stale response protection;
- request-generation guard;
- last-valid state.

Cél: egy panel hibája ne törje a többi jó adatot.

## 6.4 Devices band identity

Megszűnt az iface-névből való frontend találgatás:

`ra0 / rai0 / wlan* / phy* / radio*`

Ha backend nem ad explicit band evidence-t:
- 2.4/5 GHz counter: `—`
- client: `WiFi (band unavailable)`

Ez backend/adapter responsibility.

## 6.5 Registry történelmi V69 állapot

V69 frontend gate:
- 36 Advanced position;
- 6 Developer category;
- 16 Developer feature.

Ez **V69 historical frontend baseline**. A későbbi Developer V3 külön ág már 8 / 24 + 54 catalog struktúráig jutott.

WS artifactok:
- `WS-LT500D-V69-FRONTEND-OVERLAY-01.zip`
  SHA `728640dbce53590df9cbf4953656f37ccf7314600dc5a37df2f3c31492f411aa`
- `WS-LT500D-V69-FRONTEND-WORKTREE-01.zip`
  SHA `9cd090de357a3ee57ca601c4126b2e0501fb73ba564833bab92fbc640f1cd0f4`
- `WS-LT500D-V69-FRONTEND-BIG-BUNDLE-02.zip`
  SHA `0a0c8bbf2bcafaeb3ca43b33377740a504ca611b760f95936393c626f9459fe8`

---

# 7. RE / integration engineering alapelvek

## 7.1 CGI permission invariant

Egy executable CGI:
- source-ban 0755;
- ZIP metadata-ban 0755;
- clean extraction után 0755;
- target install után 0755.

Boot-time chmod csak defense-in-depth. Hibás artifactot nem tesz PASS-szá.

## 7.2 JSON CGI purity

JSON CGI stdout:

`CGI headers + blank line + pontosan egy JSON value`

Minden diagnosztika STDERR.

Audit:
- Content-Type;
- header/body boundary;
- JSON első byte;
- parse;
- trailing contamination;
- timeout;
- exit status.

## 7.3 Devices normalization

Target backend:
- normalized MAC authoritative merge key;
- collect evidence → normalize → group by MAC → per-field authority → one row;
- hostapd/iwinfo association > bridge FDB interface inference;
- DHCP hostname nem írhatja felül explicit `luci.devname` override-ot;
- DHCP lease ≠ online proof;
- neighbour STALE ≠ session alive;
- bridge membership ≠ Wi-Fi station interface authority;
- egy MAC → egy device record.

---

# 8. OPKG / Package Manager ág

A stock Cudy R25-ben nincs bizonyított gyári Package Manager menüpont. Ez **OpenCudy engineering extension**.

Végső UI ownership:

`Advanced → System → Package Manager`

## 8.1 H09 baseline

`RE-LT500V2-R25-ENG08-OPKG-V2-HARDENED-09`

Bizonyított:
- exact OPKG commit/build lineage `9f61f7ac`;
- mipsel_24kc;
- persistent JFFS2 overlay;
- 1 MiB safety reserve;
- Installed-Size parser;
- native filesystem-space gate;
- cached-feed size resolver;
- `--noaction` plan;
- actual payload extraction;
- list-upgradable eligibility;
- protected transaction gate;
- manager flash-space gate;
- HOLD;
- release HOLD;
- named upgrade preflight;
- actual upgrade;
- actual remove;
- cleanup/restoration.

H09:
- SOURCE VERIFIED
- STATIC VERIFIED
- TARGET VERIFIED
- LIFECYCLE VERIFIED

Core/factory locked:
- rpcd
- uclient-fetch
- libuclient
- libubox
- luci-base
- libblobmsg-json

Nincs `Upgrade All`.
Nincsenek force flag-ek.

## 8.2 FIX-03 Installed parser bug

Mért állapot:
- `opkg list-installed = 41`
- `/usr/lib/opkg/status = 41`
- `opkg list-upgradable = 6`
- GUI Installed = 0

Root cause:
az öreg pinned OPKG kétmezős:

`package - version`

formátumát a parser eldobta.

FIX-03:
- 2-field + régi 3/4-field támogatás;
- Installed counter wired;
- verifier fix.

Hashes:
- TAR.GZ `3c12ef5317baf100dae5b51067fa5efc5c0812483a0815fe69f6c9d773a2903f`
- ZIP `6f86f3bb386d0c7ca7020791affa9014fad0c474eeb9dac57234a2a31de2faed`

Elvárt:
- Installed 41
- Package DB 41
- Available updates 6

Stock Cudy rootfs marad package/kmod ownership elsődleges truth; a későbbi inventory workaround nem írhatja felül.

---

# 9. Theme / Branding H11

A stock világban `dark` és `light` theme eredetileg ugyanazon bootstrap theme/alias körből indult.

H11 feladata:
- valódi dark theme;
- Cudy/Material jellegű referencia;
- kontrollált scope;
- nem globális újratervezés.

H11-02 javította a target gate-et:
- nem exact string `LT500D`;
- LT500D family + board R25 identity.

Target runtime:
- H11 install runtime TARGET_VERIFIED;
- Dark theme TARGET_OBSERVED;
- Footer OpenCudy TARGET_OBSERVED.

Visual branding viszont PARTIAL:
- System Status: raw `2.4.16-20250804-150319`;
- Firmware page: raw `2.4.16-20250804-150319`;
- Dashboard System: `2.4.16 DE`.

Tehát H11 működik, de a teljes branding consistency nem volt lezárva.

---

# 10. Developer / Engineering oldal

## 10.1 Kronológia

V1:
- Terminal
- Sandbox/Telnet
- SSH
- engineering status

V2:
- 6 kategória
- 16 feature
- read-only backend hardening

V2 READONLY-02:
- target-verified read-only baseline
- service/runtime/hardware/snapshot bővítés

V3 FULL-01:
- **8 kategória**
- **24 core engineering feature**
- **54 native hidden/conditional catalog entry**

## 10.2 V3 ownership

Csak két production file:
- `/usr/lib/lua/luci/controller/re_developer.lua`
- `/usr/lib/lua/luci/view/system/developer.htm`

Nem veszi át:
- OPKG
- theme/branding
- network
- wireless
- firewall
- cellular/4G
- kernel
- firmware ownershipot.

## 10.3 24 core példák

- Terminal
- Telnet
- SSH
- Identity
- Hardware
- Kernel/Uptime
- Storage
- MTD
- Interfaces
- Routes
- Cellular
- USB/Modem
- Services
- OPKG State
- Cudy Framework
- Wireless Runtime
- Kernel Modules
- Listeners
- Boot/Cron
- Overlay Changes
- VPN Runtime
- Hidden Feature Lab
- System+Kernel Log
- Engineering Snapshot

## 10.4 54 native catalog példák

- Wireless Chart
- Probe List
- Wireless Log
- MLO
- MAC Repeater
- WPS
- Port Mirroring
- QoS variánsok
- Port Config
- Remote Web
- DTU
- Custom DNS
- TTL
- DMZ
- ALG
- Speed Test
- PoE Passthrough
- Samba
- Printing
- Watchcat
- LED/Button
- Cudy native Terminal/Sandbox
- VPN-oldalak

53/54 hivatkozott source path ténylegesen jelen volt; SNMP az ismert residue-kivétel.

**Source path present ≠ target működés bizonyított.**

## 10.5 Developer safety boundary

Továbbra is tiltott:
- TR-069/CWMP;
- Raw AT aktív használata;
- Modem Reset aktív használata;
- arbitrary privileged API;
- arbitrary service/ubus/path/route endpoint;
- MTD write/erase;
- GPIO write;
- firmware/sysupgrade Developerből.

---

# 11. Firmware-Unlock / CSP2.5 ág fő célja

P0:

> exact LT500/LT500D V2 / R25 CSP2.5 firmware, vagy legalább exact build identity + filename/URL/support proof.

Szükséges áttörés legalább egyik formában:
- exact `rom_version`;
- exact timestamp;
- exact filename;
- exact URL;
- MD5/SHA256;
- support-delivery artifact.

---

# 12. Stock R25 OTA mechanika

## 12.1 API family

i18n TEST:
- `https://i18n-test.cudycloud.com/device/v1/auth`
- `https://i18n-test.cudycloud.com/device/v1/checkupdate`

i18n PROD:
- `https://i18n.cudycloud.com/device/v1/auth`
- `https://i18n.cudycloud.com/device/v1/checkupdate`

CN TEST:
- `https://cn-api-test.cudycloud.com/device/v1/auth`
- `https://cn-api-test.cudycloud.com/device/v1/checkupdate`

CN PROD:
- `https://cn-api.cudycloud.com/device/v1/auth`
- `https://cn-api.cudycloud.com/device/v1/checkupdate`

Event:
- `https://event-test.cudycloud.com/device/v1/event`
- `https://event-i18n.cudycloud.com/device/v1/event`

## 12.2 Request identity

HTTP/transport oldalon:
- fuuid
- raw `/etc/rom_version` mint `vr`
- devtype = `system.board.rom`
- lan
- token

JSON:
- mac
- firmwarevr
- region
- optional modulevr
- optional isfull

Old R25 source:
`${firmwarevr/Beta/}`

R100 CSP2.5:
`${firmwarevr/b/}`

TEST selector:
- `bdinfo rdtest == 1` vagy
- `/etc/rom_alpha` létezik.

Nincs külön explicit beta/gray/canary/cohort field a stock requestben.

---

# 13. OTA boundary és Probe-97

Régi boundary:
- 0.0.0 → 2.4.16
- 1.15.28 → 2.4.16
- 2.1.1 → 2.4.16
- 2.4.15 → 2.4.16
- 2.4.16 timestamp variánsok → no update
- 2.4.17 → no update
- 9.9.9 → no update

Döntő Probe-97:

Exact strings:
- OLD `2.1.1-20240419-090237`
- STOCK `2.4.16-20250804-150319`
- REAL/HYBRID `2.5.12-20260518-234632`

3x3:
- HTTP `vr` = OLD/STOCK/REAL
- JSON `firmwarevr` = OLD/STOCK/REAL

Minden auth sikerült.

TEST + PROD:
- JSON OLD → 2.4.16 object
- JSON STOCK → empty
- JSON REAL → empty

Következtetés:

> A tesztelt identityn a JSON `firmwarevr` vezérli a firmware selectiont; a HTTP `vr` három vizsgált értéke nem mutatott selection-hatást.

Ezért random firmwarevr enumerationnek nincs értelme.

---

# 14. Négy független stock OTA publication object

i18n TEST:
`https://d1jvyy13vm72kv.cloudfront.net/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_48004.bin`

i18n PROD:
`https://d1jvyy13vm72kv.cloudfront.net/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_20729.bin`

CN TEST:
`https://cn-cf.cudycloud.com/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_95221.bin`

CN PROD:
`https://cn-cf.cudycloud.com/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_30196.bin`

Mind:
- 12,124,315 bytes
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`
- SHA-256 `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`
- byte-identical retail stock R25 2.4.16-tal.

---

# 15. Support/private distribution

Dokumentált Cudy gyakorlat:
- LT500/LT500D firmware support emailben;
- CSP2.5 beta más modelleken supporton keresztül.

Historical példák:
- 2024-08-26 LT500 V1 → support email firmware;
- 2024-09-23 LT500 V2 / 2.1.1 issue → support contact;
- 2025-04-29 LT500D cellular issue → email solution;
- 2025-07-28 T-Mobile beta firmware kérés → email solution;
- 2026-02-03 LT500 V1 firmware kérés → technical support;
- 2026-08 CSP2.5 comments: egyes modellekhez beta support emailben, másokhoz explicit nincs beta.

Classification:
- LT500/LT500D private firmware delivery VERIFIED.
- CSP2.5 private beta delivery other models VERIFIED.
- exact R25 CSP2.5 support build UNKNOWN / NOT FOUND.

---

# 16. Activation mechanika

R100 source:
- `/usr/sbin/activate`
  SHA `a0dbc74614d8215106eae442ec4e6305aa49ebd8fb8e399fb9e1fff557797d93`
- `/etc/init.d/activate`
  SHA `f3eead49944df74dc83966d9e2ef190f6749768c2548e85b2532db6fc7b49193`
- `/etc/rc.d/S99activate`
- START=99

Gate:
1. checkuuid OK
2. serial nonempty
3. country != CN
4. `system.@system[0].activate` unset

Endpoint:
- TEST if real `/etc/rom_alpha`: `https://event-test.cudycloud.com/device/v1/activate`
- otherwise: `https://event-i18n.cudycloud.com/device/v1/activate`

Flow:
- serial + rom_version;
- encryption helper;
- wait `.timeclock`;
- sleep 86400;
- dtime;
- nonce;
- signature;
- POST data/nonce/vr/dtime/sign;
- max 3 network attempts;
- nonempty response;
- ret==0 → `activate=1`, UCI commit.

Proven:
- source mechanism;
- hybrid R25 naturally ran service;
- process-list earlier showed `sleep 86400`.

Not proven:
- activation beta cohort enrollment;
- activation → OTA eligibility;
- official R25 registration;
- R25 beta requirement.

**Do not manually trigger synthetic activation.**

---

# 17. Live R25 MTD6 audit — later binary evidence

Latest mounted audit input:
- physical R25 live mtd6
- size 16,252,928 bytes
- SHA-256 `d4e30da79e322d13e707c15c95f7f007b916b7d20871ca79a192182506ad408c`

Layout:
- uImage starts 0
- name R25
- timestamp 2025-08-04 07:04:59 UTC
- payload 2,456,845
- CRC valid
- SquashFS 0x257D4D
- kernel/uImage region byte-identical stock R25 2.4.16-tal

Live SquashFS:
- 2751 inodes
- mkfs `2026-05-18 15:39:35 UTC`
- block 262144
- XZ
- bytes_used 9,793,644
- SHA `2bc140aee1ff127b04961a3c1082a394bc7b2d31cd8dc10e741a6a98a625b005`
- rootfs_data 0xBB0000

Fontos:
- live rootfs mkfs timestamp pontosan R100 CSP2.5 2.5.12 rootfs timestamp;
- de live rootfs nem byte-identical R100;
- rebuilt/distinct CSP2.5-derived rootfs.

fwtool metadata live MTD-ből:
- FWx0 NOT FOUND
- DEADC0DE NOT FOUND
- supported_devices NOT FOUND
- R100 NOT FOUND

Ez nem bizonyítja, hogy eredeti hybrid image-ben nem volt metadata, mert a trailer a későbbi JFFS2 írható zónába eshetett és felülíródhatott.

Recovered JFFS2:
- `/upper/etc/rom_version` = `2.5.12-20260518-234632`
- system config: LT500D, Europe/Budapest, R25
- nincs historic/previous/activate option a recovered current configban
- `/upper/etc/fwinfo.json` = firmware empty
- timestamp ~2026-09-29 00:57–00:58 local, a GUI update checkkel korrelál.

Ez binary-level BEFORE-ACTIVATION evidence az empty firmware objectre.

Engineering lineage backup pathok is látszanak, tehát a hybrid nem untouched official R25 image.

---

# 18. Cudy emulator forensic project — miért készült

A firmware hunt közben felmerült:
- az emulatorok real Cudy frontend source-ot tartalmazhatnak;
- a backend statikus/mocked;
- exact firmware build identityk szivároghatnak;
- hidden/unlisted CDN artifact neve kikövetkeztethető lehet exact buildből.

Ezért a `diablomike20/Website-downloader` forkban egy Cudy-specifikus, unlimited forensic downloader készült.

Repo:
`https://github.com/diablomike20/Website-downloader`

Branch:
`fu_6-cudy-forensic`

PR:
`#1`

Latest documented head:
`901c10a553969169a996370ea8a91f51aad7b02f`

---

# 19. Crawler követelmények és működés

- GET-only.
- raw response bytes byte-exact mentése.
- SHA-256 inventory.
- nincs mesterséges request/byte/time limit Cudy módban.
- CLI 0 = unlimited.
- href/src/action.
- CSS `url(...)`.
- LuCI route stringek.
- static `.html`.
- simple `$.post`.
- `<base href>` támogatás.
- Cudy query-path mapping.
- LuCI route → static emulator snapshot mapping.
- HTML entity decoding.
- cbi_xhr_load data/query mapping.
- AC_Cloud SPA mock API mapping.
- exact raw URL path collision disambiguation.
- external direct dependency leaf capture.
- no recursive crawl unrelated external site-ra.
- destructive live action route nem invoked.
- statikus snapshot megtartható.
- per-model failure isolation.
- all mode: `fu_6-failures.json`.

Offline archive jelenleg raw fidelity; nem minden route átírva önálló teljes browser replayhez. Későbbi replay server külön feature lehet.

---

# 20. Crawler hibák és javítások

## 20.1 HTML escaped modal route bug

`&quot;/cgi-bin/luci/...&quot;` route-ok kimaradtak.

Fix:
- HTML entity decode discovery előtt.

Eredmény C200P:
359 visited → 565 visited
104 route → 166 route

## 20.2 Dotted model path collision

Példák:
- WR1300V4.0
- WR3000v2.0
- WR3000v3.0

Directory URL fájlként mentődött, később asset mkdir `ENOTDIR`.

Fix:
trailing slash → `index`, modell directory megmarad.

## 20.3 Képek/fontok `.bin` hibája

Eredeti rossz output:

`logo-blue.png__q_HASH.bin`

Root cause:
query hash az extension után került, majd a név extensionlessnek látszott.

Fix:
`logo-blue__q_HASH.png`
`logo__q_HASH.svg`
`iconfont__q_HASH.woff2`

MIME extension fallback is hozzáadva.

## 20.4 Legacy model-prefixed LuCI route

`/emulator/LT500/cgi-bin/luci/...` stringek felismerése.

## 20.5 cbi_xhr_load query snapshot

Pl.:

`/autoupgrade` + `updatecheck=&nomodal=`

→

`/autoupgrade/updatecheck/nomodal.html`

## 20.6 AC_Cloud SPA mock API

A cloud frontend requestjei:

`.../web/v1/...`

emulatorban:

`./mock_api/web/v1/...json`

A crawler most ezeket is menti.

---

# 21. Latest all-emulator archive

Latest headen futott:
- 90 model
- 90 completed
- 0 failed
- 34,769 file
- 527,278,057 raw bytes
- AC_Cloud: 325 file
- master LuCI routes: 12,431

GitHub run:
`36532425169`

Artifact:
- ID `11018311218`
- final ZIP size `128021977`
- uploaded artifact ZIP SHA-256:
  `83e407ddbc1389355e4418f3f9a605b32227946cc7e8f680b05b33e5060bc02a`

Ez frissebb, mint a korábbi 27,840 file / 10,522 route archive.

---

# 22. C200P emulator evidence

Emulator identity:
- model C200P V1.0
- board R74
- FW `2.5.14-20260618-150931`

Build strings a teljes C200P crawlban:
- 2.0.8-20240312-100828
- 2.5.14-20260611-121254
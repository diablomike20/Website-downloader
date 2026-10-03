# Firmware Unlock 9 — teljes projekt master dokumentáció

**Állapotdátum:** 2026-10-03  
**Előd:** Firmware Unlock 8  
**Utód chat neve:** Firmware Unlock 9  
**Nyelv:** magyar  
**Dokumentum célja:** teljes technikai és munkafolyamat-handoff úgy, hogy az új chatnak ne kelljen nulláról rekonstruálnia sem az LT500D/OpenCudy, sem a donor-forensics, sem a most elsődlegessé tett Belkin F9K1103 v1 / LEDE 17.01.5 szakágat.

---

# 0. Rövid végrehajtói összefoglaló

A projekt eredetileg a **Cudy LT500D V2 / R25** gyári Cudy 2.4.16 / LEDE 17.01.5 firmware teljes reverse engineeringjéből, unlockjából és OpenCudy fejlesztéséből indult.

Az R25 ágon már van:
- fizikailag bizonyított engineering runtime lineage;
- stabil 4G baseline;
- SSH/Dropbear engineering access;
- Telnet/debug access kutatás;
- OPKG teljes lifecycle;
- Developer UI lineage;
- factory/debug token és maintenance architektúra mély RE;
- külön OpenWrt 23.05.5 donor-fidelity frontend/integration ág;
- CSP2.5 donor-forensics;
- több Cudy dev/beta/internal firmware donor;
- P2/R91/RG500 és C200P mély statikus összehasonlítás.

**2026-10-02 végén új elsődleges szakág indult:**
Belkin F9K1103 v1 / N750 DB hardveren Cudy-szerű/OpenCudy rendszer létrehozása.

A felhasználó végső prioritása:
1. **előbb legyen működő, reprodukálható natív F9K1103 v1 LEDE 17.01.5 build;**
2. csak utána kerüljön rá Cudy UI/userspace;
3. a működő F9K1109 v1 OpenWrt 19.07.0 image maradjon hardver-reference, ne végleges port-alap.

Ez a prioritás minden korábbi „folytassuk előbb az R25 RE-t” irányt felülír, de az R25 ág összes bizonyítéka és artifactja megmarad.

---

# 1. Projektágak és tulajdonosi határok

## 1.1 Cudy LT500D / R25 physical engineering ág

Cél:
- stock hardverviselkedés megtartása;
- módosítható engineering firmware;
- SSH/Telnet/debug;
- OPKG;
- Developer UI;
- 4G megőrzése;
- OTA/vendor policy kontroll;
- CWMP/TR-069 kizárása;
- gyári Cudy WebGUI és szolgáltatások lehető legnagyobb megtartása.

## 1.2 OpenWrt 23.05.5 donor-fidelity frontend/integration ág

Cél:
- gyári LEDE/Cudy WebGUI élmény reprodukciója OpenWrt 23.05.5 alatt;
- standalone frontend `/www/cudy-static`;
- donor-fidelity;
- target adapterek;
- frontend/backend ownership tiszta szétválasztása.

Ez külön truth-lineage. Nem szabad automatikusan összemosni a fizikai R25 C27 engineering runtime-mal.

## 1.3 Cudy donor-forensics / firmware hunt ág

Cél:
- más Cudy modellek firmware-einek begyűjtése;
- beta/dev/internal/recovery/support-private lineage;
- CSP2.5 evolúció;
- hidden/support/debug architektúra;
- donor-szintű összehasonlítás.

Fő modellek:
- LT300V3 / R100;
- C200P / R74;
- P2 / R91;
- WR1200 V2 / R26;
- WR1300;
- WR2100;
- WR3000;
- egyéb Cudy emulator/archive modellek.

## 1.4 Belkin F9K1103 v1 / LEDE szakág — jelenlegi P0

Cél:
- saját F9K1103 v1 target LEDE 17.01.5 alatt;
- nem RT-N56U vagy F9K1109 image átnevezése;
- saját DTS, board detection, network, MAC, image recipe;
- build SUCCESS;
- statikus validáció;
- később explicit user döntéssel physical boot;
- csak utána Cudy userspace/UI port.

Repo:
`diablomike20/Belkin-F9K1103-Firmware`

---

# 2. Evidence vocabulary — kötelező terminológia

**TARGET_VERIFIED**  
Fizikai eszközön bizonyított.

**LIFECYCLE_VERIFIED**  
Teljes fizikai életciklus/folyamat bizonyított, nem csak egyszeri állapot.

**TARGET_OBSERVED**  
Fizikai targeten látott állapot, de nem teljes gate.

**SOURCE_VERIFIED**  
Közvetlen source/rootfs/script bizonyíték.

**R25_SOURCE_VERIFIED**  
Kifejezetten a stock R25 firmware-ből származó source/binary bizonyíték.

**STATIC_VERIFIED**  
Offline strukturális/hash/build/bináris ellenőrzés PASS.

**BINARY_STATIC_VERIFIED**  
Natív bináris import/string/control-flow/disassembly alapján igazolt.

**INSTRUCTION_LEVEL_VERIFIED**  
Lua bytecode/disassembly vagy natív disassembly alapján konkrét végrehajtási szemantika igazolt.

**WEB_VERIFIED / FIRST_PARTY_WEB_VERIFIED**  
Publikus webes/gyártói bizonyíték.

**EMULATOR_VERIFIED**  
Cudy emulator runtime/source evidence.

**CROSS_DONOR_CORROBORATED**  
Más Cudy modellen megerősített, de nem target truth.

**ARCHITECTURAL_LEAD**  
Hasznos irány, de nem lezárt bizonyíték.

**TARGET_REQUIRED**  
Fizikai teszt nélkül nem zárható le.

**UNKNOWN / NOT FOUND**  
Nincs lezárt bizonyíték.

Soha ne emelj evidence-szintet csak azért, mert „logikusnak tűnik”.

---

# 3. Elsődleges Cudy fizikai target — R25 truth

Model:
**Cudy LT500D V2.0**

Board/devtype:
**R25**

Region:
**EU**

Country:
**DE**

Hardver:
- MediaTek MT7628AN;
- MIPS24KEc;
- Linux 4.4.140;
- 128 MiB RAM;
- 16 MiB SPI NOR;
- 2.4 GHz: MT7628 vendor WLAN;
- 5 GHz: MT7663E-family, PCI 14c3:7663.

Cellular:
- Quectel EC200A-EL;
- firmware `EC200AELV1LAR02A03M08`;
- VID:PID 2c7c:6005;
- `cdc_ether -> usb0`;
- `network.4g` működik `usb0` felett.

A felhasználó jellemzően 4G/SIM módban használja.
**4G törése P0 regresszió.**

Identity:
- model LT500D V2.0;
- rom R25;
- wan_port 3;
- ports 4;
- `bdinfo region EU`;
- `bdinfo country DE`;
- `bdinfo checkuuid OK`.

A fizikai R25 az authoritative target truth.

---

# 4. Canonical stock R25 firmware

Fájl:
`LT500V2-R25-2.4.16-20250804-150319-flash.bin`

SHA-256:
`57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

Méret:
12,124,315 byte.

Base:
- LEDE 17.01.5;
- ramips/mt76x8;
- mipsel_24kc;
- Linux 4.4.140;
- Cudy 2.4.16.

Exact stock rootfs ZIP:
`squashfs-root-LT500V2-R25-2.4.16-20250804-150319-flash.zip`

SHA-256:
`f587fa2c36d479e0a6223191546f9db5df6482ff2099d761ddd646d9b89a6fb0`

Audit:
- 2637 entries;
- LEDE 17.01.5 / Cudy 2.4.16 / R25 / ramips-mt7628.

---

# 5. R25 flash/storage truth

Fő MTD:
- mtd0 u-boot: 0x000000 / 0x030000;
- mtd1 u-boot-env: 0x030000 / 0x010000;
- mtd2 factory: 0x040000 / 0x010000;
- mtd6 firmware: 0x050000 / 0xF80000;
- mtd3 debug: 0xFD0000 / 0x010000;
- mtd4 backup: 0xFE0000 / 0x010000;
- mtd5 bdinfo: 0xFF0000 / 0x010000;
- runtime: mtd7 kernel, mtd8 rootfs, mtd9 rootfs_data.

Mount:
- `/rom` SquashFS RO;
- `/overlay` JFFS2 RW;
- overlayfs merged root.

Kritikus:
**factory SquashFS önmagában nem egyenlő a stock runtime truth-tal.**

A stock firstboot/uci-defaults/OEM materializáció legitim változásokat hoz létre, például:
- runtime Wi-Fi script state;
- cellular `eth1 -> usb0` migration;
- IPTV CBI materialization;
- OEM config.

---

# 6. Physically proven OpenCudy lineage

## ENG08
- működő fizikai 4G baseline;
- stock/live-stock cellular helyreállítva;
- unlock elválasztva a felesleges cellular módosításoktól.

## H09 OPKG
SOURCE + STATIC + TARGET + LIFECYCLE VERIFIED.

Bizonyított:
- exact régi OPKG lineage;
- mipsel_24kc;
- persistent overlay;
- Installed-Size;
- 1 MiB safety reserve;
- native filesystem space gate;
- cached feed size resolver;
- dry-run/noaction;
- actual install;
- list-upgradable;
- protected transaction policy;
- HOLD / release HOLD;
- named upgrade;
- remove;
- cleanup/restoration.

Installed state későbbi baseline:
127 installed records:
- 41 userland/base;
- 86 stock-ROM kmod.

Core lock példák:
- rpcd;
- uclient-fetch;
- libuclient;
- libubox;
- luci-base;
- libblobmsg-json.

Nincs Upgrade All.
Nincs force.

UI ownership:
Advanced → System → Package Manager.

H09 frozen subsystem.

## H11-02
- install/runtime TARGET_VERIFIED;
- H09 integritás;
- JFFS2;
- 4G preserved;
- dark theme TARGET_OBSERVED;
- branding csak PARTIAL.

Ismert branding miss:
1. Dashboard System card;
2. System Status firmware row;
3. General → Firmware / Online Update raw version.

## Developer V2 READONLY-02
- target probe PASS;
- target verify PASS;
- non-mutating selftest PASS.

## Developer V3/V4
V3:
- 8 categories;
- 24 core engineering features;
- 54 native hidden/conditional catalog items.

V4 CLEAN:
- normál Cudy funkciók nem duplikálódnak Developerben;
- valódi maintenance/engineering felületek maradnak;
- security-sensitive actionök explicit gate;
- TR-069 nincs.

## Current cumulative runtime lineage
`RE-LT500V2-R25-OPENCUDY-CUMULATIVE-27-TARGET-INSTALLABLE.tar.gz`

C27:
- service PASS;
- auto_upgrade=0;
- CWMP off;
- OPKG 127/127/86;
- watchdog;
- 4G usb0;
- Developer V4 CLEAN-06.

C27 runtime package lineage, **nem final flash release**.

---

# 7. Candidate47 image truth

Sysupgrade candidate:
`RE-OPEN-CUDY-LT500V2-R25-C27-SYSUPGRADE-CANDIDATE-47.bin`

SHA-256:
`8d51bc017a3e275c0ce3a5c05a659a4a3c4f55bb96370d0fabc81f3d1470a060`

Méret:
12,058,779 byte.

Bizonyított:
- stock R25 uImage anchor;
- stock GUI upload elfogadás;
- `sysupgrade -T` PASS;
- format gate TARGET_VERIFIED.

Nem bizonyított:
- tényleges flash;
- boot;
- lifecycle.

Fullflash structural candidate:
`RE-OPEN-CUDY-LT500V2-R25-C27-FULLFLASH-CANDIDATE-47.bin`

SHA:
`7118cfd798da459fc7d5ea0350501ec4a5bd088e0449d953dabf15929f89694f`

**Candidate47-et soha ne nevezd bootoltnak.**

---

# 8. Unlock delta ledger — jelenlegi helyes modell

UNLOCK_REQUIRED:
- Dropbear local `bdinfo dbg` startup gate kezelése/bypass;
- Telnet startup gate kezelése engineering policy szerint;
- stabil engineering root;
- installed sysupgrade unlock;
- root password regeneration override neutralizálása ott, ahol a lineage megköveteli.

UNLOCK_PERSISTENCE:
- scheduled vendor automatic OTA suppression.

Project policy:
- TR-069/CWMP OFF / excluded.

Nem inherens unlock requirement:
- hcshd teljes eltávolítása;
- cellular script rewrite;
- antenna rewrite;
- minden Cudy cloud komponens letiltása;
- globális `bdinfo dbg=OK` hamisítás;
- modem firmware csere.

A későbbi auditok azt mutatták, hogy több unlock delta lokális init/policy/access változás volt; kernel/uImage és számos vendor binary stock-identical maradhat.

---

# 9. bdinfo / factory / debug / development — ne keverd össze

Külön fogalmak:
1. `bdinfo factory` — manufacturing/factory state;
2. `/etc/rom_develop` — runtime Test Only marker;
3. `/rom/etc/rom_develop` — immutable dev-image marker;
4. `bdinfo dbg` — factory debug/maintenance authorization;
5. OpenCudy Developer — saját engineering control plane;
6. `hcshd` — stock vendor maintenance daemon;
7. debug MTD — külön flash partition;
8. Linux debugfs — kernel debug filesystem.

**bdinfo-t normál kísérletben nem írunk.**

---

# 10. Exact R25 access architecture

Stock R25 source/rootfs:
- `/etc/init.d/dropbear` → `bdinfo dbg == OK` gate;
- `/etc/init.d/telnet` → ugyanilyen gate;
- `/lib/preinit/99_00_console` → debug inactive esetben console login policy;
- `/usr/libexec/login.sh` → debug active esetben direct ash path;
- hidden `admin/system/terminal`;
- `luci.forbidden` deny list;
- Terminal CBI `luci.util.exec`;
- Sandbox/Telnet CBI;
- retail firstboot root credential FUUID/HMAC-derived.

Ez R25 SOURCE truth.

---

# 11. R25 Factory Debug token — CP10 lezárt statikus RE

Exact `/usr/lib/libbdinfo.so` SHA:
`dc2ac9f10739eb1f690acf3fbd9e17d8f824673f7faa7173db3894faa4cfc15b`

`bdinfo_check_dbg()` statikusan visszafejtve.

R25 token family:
- flash UUID procfs identity;
- bdinfo HMAC;
- `@2025` literal;
- SHA-256;
- lowercase 64-hex runtime marker;
- `/etc/rom_dbg`;
- retail `/etc/rom_release` külön gate.

Fontos:
ez **R25 exact static truth**, nem C200P-ből átmásolt formula.

A handoff nem ad aktiválási receptet. A cél az architektúra megőrzése és dokumentálása.

---

# 12. R25-family valós vendor maintenance esemény

Egy régebbi LT500/R25 2.1.1 runtime logban valós vendor maintenance sequence jelent meg:
- retail release marker eltávolítása;
- device identity olvasása;
- debug marker létrehozása;
- ideiglenes root credential kezelés;
- Telnet/Dropbear indítás.

Ez:
- azonos R25 hardvercsalád;
- régebbi 2.1.1 firmware;
- valós runtime evidence.

Nem bizonyítja, hogy a 2.4.16 hcshd hardcode-olja ezt.
A hcshd import/topology alapján inkább authenticated vendor command transport.

---

# 13. Cudy management/control planes — FU8 CP11–14

A korai „egy lineáris backdoor chain” modell helytelen volt.

Jelenlegi rétegzett modell:

## 13.1 LuCI local application/RPC plane
- `rpc/sys`;
- `rpc/app`;
- `rpc/sysupgrade`;
- normál LuCI session auth.

## 13.2 cmagent plane
- külön natív daemon;
- MQTT + ubus;
- admin/mesh/local management;
- Lua modules;
- `service_call` handler ABI;
- module families: command, config, upgrade, sysreport, clients, timer, ledctl stb.

A stock R25-ben első-party belső callerjei is vannak:
- `/usr/sbin/sync_command`;
- `/usr/sbin/sync_config`;
- mesh/LuCI synchronization paths.

Ezért:
**cmagent command handler != árva backdoor residue.**
Normál vendor mesh/admin fabric része.

Developer UI-ban raw command API-ként nem tehető ki.

## 13.3 cmsd plane
- stock default: disabled;
- checkuuid/MAC start gates;
- binding/cloud application transport;
- natív MQTT/TLS/ubus;
- `/usr/lib/lua/cmsd`;
- module dispatch;
- `service_call`;
- `cmsd.apprpc` generic JSON-RPC → local `luci.app` bridge.

Exact pre-Lua credential decision:
**BINARY_PARTIAL / exact formula UNKNOWN**.

## 13.4 Mosquitto broker auth boundary
- anonymous access false;
- JWT/ACL/certificate policy;
- `auth_plugin_jwt.so`;
- plugin közvetlen `libbdinfo.so` dependency;
- provisioning identity a broker authentication boundary része.

Broker auth külön réteg a cmagent opcionális kliens-oldali JWT módjától.

## 13.5 hcshd
- külön procd service;
- külön UDP/socket maintenance plane;
- RSA gate;
- `system/popen` command sinks a binaryben;
- malformed passive emulation inputok RSA decrypt előtt/ott fail-elnek;
- ilyen hibás inputnál command sink nem futott.

Shared exact RSA public trust anchor:
`libbdinfo.so` és `hcshd` ugyanazt az egyik PEM trust anchort tartalmazza.

Hash:
`e68b3ce363587e59fa1cb3bccd445e395b2a1e52e6fff936b495e393106d9d60`

Ez közös vendor trust domain evidence.
Nem direkt process-call evidence.

## 13.6 Direkt hidak
Exact stock corpusban nem talált:
- cmagent → hcshd;
- cmsd → hcshd;
- rpc/app → hcshd;
- rpc/sys → hcshd.

Státusz:
`DIRECT_BRIDGE_NOT_FOUND_IN_EXACT_STATIC_CORPUS`

Nem ugyanaz, mint „biztosan nincs”.

## 13.7 Firewall/exposure
Stock:
- LAN input ACCEPT;
- WAN input REJECT;
- WAN forward REJECT;
- nincs explicit MQTT WAN allow;
- nincs hcshd WAN allow.

Ezért:
all-interface bind **nem egyenlő** WAN exposure-rel.

`WAN_EXPOSURE_STATIC_DEFAULT = BLOCKED_BY_POLICY`

Runtime packet path:
nem target-mérve.

---

# 14. Cudy app / cloud / TR-069 szétválasztás

Ne kezelj minden vendor management komponenst TR-069-ként.

A) CWMP/TR-069:
- remote provisioning;
- projektben kizárt.

B) device identity/cloud binding:
- FUUID/UUID;
- cmsd;
- selected cloud/session elements.

C) local app discovery/management:
- cmagent;
- mosquitto;
- mDNS/umdns-like local components.

Korai „tiltsunk le minden cloud-looking service-t” megközelítés hibás lehet, mert normál app/mesh/identity függőségeket törhet.

Kívánt policy:
- CWMP OFF;
- vendor firmware remote control OFF ahol szükséges;
- local app/mesh dependencies megőrzése;
- device identity megőrzése;
- csak bizonyítottan szükséges cloud/session funkciók.

---

# 15. 4G / Cellular truth

R25:
- `gcom`;
- `/dev/ttyUSB1`;
- AT control;
- EC200A-EL;
- cdc_ether;
- usb0 data.

ENG07→ENG08 fő tanulság:
a 4G törése nem az unlock szükségszerű következménye volt.

Cellular default:
**stock/live-stock R25 truth.**

Ne másolj P2 új 4G fájlokat R25-re csak azért, mert újabbak.

---

# 16. Performance / watchdog

Watchdog:
- `/dev/watchdog`, `/dev/watchdog0`;
- procd/PID1 ownership;
- ~30 s timeout;
- ~5 s feed.

Performance probe:
- 128 MB class memory;
- zram;
- normal idle CPU;
- cmagent/gcom/uhttpd/mosquitto/umdns stb. együtt fut;
- JFFS2 overlay boot/materialization események fontosak;
- nem bizonyított tartós multi-hour gcom/watchdog restart loop.

Performance monitoring ne nyisson újra lezárt unlock döntéseket evidence nélkül.

---

# 17. OpenWrt 23.05.5 donor-fidelity ág

Long-term UI target:
full LEDE/Cudy WebGUI parity OpenWrt 23.05.5 alatt.

Standalone:
`/www/cudy-static`

Primary donor:
Cudy/LEDE 2.4.16.

Secondary donor:
LT15E/R58 2.2.7.

CSP2.5 donor:
LT300V3/R100 2.5.12.

Roles:
- EM = emulator/web forensics;
- RE = firmware/source/binary;
- WS = frontend;
- Integration/Boss = target backend/CGI/merge/build/gates.

Historical V69:
`RE-LT500D-V69-WIP-LEDE-DASHBOARD-TRUTH-04.zip`

SHA:
`e8e2f65fedb5d30a445a221f6f868c4fc50b861a9c441693d9ea4bf5932c36e0`

V69 truth:
- WISP Status/Settings;
- scan/join structure;
- SMS Inbox/New/Outbox;
- WAN DHCP/PPPoE/Static/L2TP/PPTP readonly forms;
- Devices mapping;
- unproven writes disabled;
- frontend/backend/registry/state/CGI audits PASS.

Wireless/WISP donor-validated ág:
**ne írd újra konkrét audit-hiba nélkül.**

---

# 18. Backend/frontend invariants

Executable CGI:
- source 0755;
- ZIP metadata 0755;
- extraction után 0755;
- install után 0755.

JSON CGI:
stdout = headers + blank line + exactly one JSON value.
Diagnostics stderr.

Devices:
- normalized MAC merge key;
- one MAC → one row;
- hostapd/iwinfo association authoritative a Wi-Fi státuszhoz;
- DHCP hostname nem írhat felül explicit devname-et;
- DHCP lease nem online proof;
- neighbour STALE nem session-alive;
- bridge membership nem Wi-Fi association authority.

Cross-feature one-owner:
- cellular bearer/session → Cellular owner;
- WISP nem mutálja;
- firewall → firewall owner;
- accounting GET nem writer;
- VPN MAC policy one authoritative state.

---

# 19. OTA/CSP2.5 R25 kutatás

Stock OTA family:
- i18n TEST;
- i18n PROD;
- CN TEST;
- CN PROD.

R25 stock publication objectok:
mind byte-identical stock 2.4.16:
- size 12,124,315;
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`;
- SHA-256 stock hash.

Probe-97:
HTTP header `vr` és JSON `firmwarevr` 3×3 matrix.

Lezárt finding:
- JSON OLD → stock 2.4.16 offer;
- JSON STOCK → empty;
- JSON REAL → empty;
- header variation nem változtatta az eredményt.

**Ne ismételd Probe-97-et.**
**Ne random enumerate-elj firmwarevr/timestamp/suffix értékeket.**

Exact R25 CSP2.5 artifact:
**UNKNOWN / NOT FOUND.**

Public latest known R25:
2.4.16.

Private/support delivery precedent:
bizonyított általánosan LT500/LT500D/Cudy vonalon, de exact R25 CSP2.5 payload nincs.

---

# 20. R100 CSP2.5 donor

`LT300V3-R100-2.5.12-20260518-234632-flash.bin`

SHA:
`03641ed863911618155ddb55ed2c45f4c23abd330a4e171bff4491ffcda49a82`

Fontos:
CSP2.5 továbbra is régi Cudy LEDE 17.01.5/Linux 4.4.140/MT7628 lineage, nem modern OpenWrt migráció.

Feature leads:
- tcpdump/Packet Capture;
- encrypted DNS;
- AdShield;
- cloud management;
- mesh/update evolution;
- cellular vendor bővítés.

R100 donor truth, nem R25 truth.

Hybrid physical R25 2.5.12 state:
értékes lab evidence, de **nem official R25 2.5.12 firmware proof**.

---

# 21. C200P — FU8 kulcsdonor

Internal/unlisted emulator build:
`C200P-R74-2.5.14-20260618-150931-flash.zip`

Outer SHA:
`a4f5f6494bcbdf41bfcd8573a22531fbd2115b5cb2769f5f44da213a900a7e98`

Inner BIN SHA:
`8ba6c51d13d72d2871a1b5e8bbcb4318c2fd4234898f8c1e9e6c30502913e0e8`

Public successor:
2.5.15.

2.5.14→2.5.15 rootfs:
- added 1;
- removed 0;
- changed 62;
- unchanged 2464;
- egyetlen új fájl: `/lib/functions/curl.sh`.

Ez near-public predecessor evidence.

C200P support SSH / batchcmd Lua 5.1 bytecode instruction-level RE:
- support SSH state machine;
- device identity reads;
- support credential derivation;
- debug/release marker kezelés;
- Dropbear restart;
- nonlocal cmagent/MQTT path;
- batchcmd generic command loop.

**C200P exact formulákat R25-re nem szabad átmásolni.**
Ami közös:
- identity/HMAC/@2025 debug-token family;
- rom_release semantics;
- support/debug state architecture.
A credential policy termékgeneráció-specifikus.

---

# 22. P2/R91 donor lineage — FU8 CP09

P2 2.4.22:
`P2-R91-2.4.22-20251204-184925-sysupgrade.bin`
SHA:
`592c494eb5f44beabb427907003801845ea0d47d51db50b1d5b97d40e3166b58`

P2 2.4.29 stable:
`P2-R91-2.4.29-20260421-190344-sysupgrade.bin`
SHA:
`33c9650709eb012348c0d7df31cb3d41ceefbf7d9ca8cebd0b22e0e0524a789c`

P2 2.4.29b:
`P2-R91-2.4.29b-20260422-101502-sysupgrade.bin`
SHA:
`3f8dae3d42ad6ba7d1314022eac6bc007d03fac274196b2c802f2835ab21c3f9`

Public 2.4.22→2.4.29:
- 2730 → 2380 entries;
- unchanged 2289;
- changed 85;
- added 6;
- removed 356.

Added event/recovery layer:
- `/etc/hotplug.d/gcom/30-4g`;
- `/etc/hotplug.d/tty/30-4g`;
- `/usr/lib/4g/check.sh`;
- `/usr/lib/4g/reup.sh`.

Old generic WWAN layer nagyrészt eltűnik.

4-hour issue:
first-party release note verifies fix,
de explicit literal 4h timer patch **NOT FOUND**.
Event/recovery refactor causal szerepe plausible, nem izolált.

2.4.29 stable→2.4.29b:
nagyon keskeny Vodafone/temp delta + `/etc/rom_research`.
Ne keverd a public general recovery fixet a beta Vodafone ággal.

---

# 23. FU7/FU8 dev/beta payload lineage

Recovered:
- WR3000 beta;
- P2 2.4.22;
- P2 2.4.29b;
- P2 RG500 A09 modem;
- R91 2.4.23b CellularUpgrade;
- TR1200 beta;
- OpenWrt intermediary firmware corpus.

RG500 evidence:
factory/debug/fastboot/recovery/test infrastructure.
**Nem flash-kompatibilis EC200A-val.**

`/etc/rom_research` P2 beta marker:
beta-only empty marker,
de univerzális developer-unlock consumer nem bizonyított.

---

# 24. FU8 Checkpoint 10 — R25 ↔ C200P correlation

Lezárt:
- exact R25 access architecture;
- exact R25 debug-token RE;
- older R25-family vendor maintenance runtime sequence;
- C200P support SSH összevetés;
- credential policy non-universality.

Kulcs:
R25 retail root credential, old R25 support-session credential, C200P support credential **nem ugyanaz a formula**.

Unresolved CP10 után:
- exact 2.4.16 hcshd upstream caller;
- exact 2.4.16 support-session credential;
- exact `bdinfo_check_uuid()`;
- full relationship hcshd/hcsh/rpc/cmagent.

---

# 25. FU8 Checkpoint 11 — caller topology

Exact stock source alapján:
- LuCI RPC;
- cmagent;
- hcshd
külön plane.

Direkt cmagent→hcshd vagy RPC→hcshd source bridge nem talált.

Ez korrigálta az egyetlen lineáris vendor-maintenance lánc feltételezését.

---

# 26. FU8 Checkpoint 12 — management dependency map

További szétválasztás:
- LuCI RPC;
- cmagent;
- cmsd;
- hcshd.

`cmsd`:
- default OFF;
- külön bind-flow;
- `cmsd.apprpc` JSON-RPC → `luci.app`.

`bdinfo checkuuid` ≠ `bdinfo dbg`.

checkuuid:
provisioning/identity/service-start.

dbg:
debug/access policy.

---

# 27. FU8 Checkpoint 13 — auth/trust boundary

Broker:
JWT/ACL/cert layer.

`auth_plugin_jwt.so`:
direct `libbdinfo.so` dependency.

cmagent:
native Lua route/module dispatch verified.

cmsd:
native MQTT/TLS/ubus/Lua dispatch verified.

hcshd:
shared RSA trust anchor libbdinfo-val.

Exact hcshd legitimate sender:
UNKNOWN.

Exact cmsd pre-Lua credential formula:
UNKNOWN / BINARY_PARTIAL.

---

# 28. FU8 Checkpoint 14 — exposure + internal callers

Firewall static policy:
WAN input REJECT.

Nincs stock explicit MQTT/hcshd WAN allow.

cmagent command/config handlersnek vannak first-party internal callers.
Normál mesh/admin sync fabric.

OpenCudy consequence:
- ne töröld automatikusan;
- ne tedd raw shell API-vá;
- csak narrow explicit Developer actions.

---

# 29. Cudy donor firmware audit a Belkin-porthoz

2026-10-02:
külön donor corpus audit készült.

Run:
`36957672696`

Commit:
`3dbba5fd2e7629c7ec20ba636ca7260c727d6dc6`

Artifact:
`11206815616`

Artifact digest:
`67faaafe219143ec262d06419b815a819e23fb6ae7b67826bf927e096e3ca8b1`

Begyűjtött fő firmware-ek:
- LT500D R25 2.4.16;
- WR1200 V2/R26 1.17.4;
- WR1200 V2/R26 2.1.1;
- WR1200 V2/R26 2.2.8;
- WR1200 V2/R26 2.4.12;
- WR1200 V2/R26 2.4.23;
- WR1300 R10 1.13.6;
- WR2100 R11 1.14.25;
- OpenWrt 19.07.0 F9K1109 v1;
- OpenWrt 19.07.10 F9K1109 v1;
- OpenWrt 19.07.10 Cudy WR1000.

Kulcs finding:
a vizsgált Cudy stock firmware-ek ugyanazon **LEDE 17.01.5** userspace-generáció körül élnek.

WR1200 V2 2.4.12/2.4.23 UI különösen közel LT500D 2.4.16-hoz:
- UI path similarity kb. 81.5%;
- byte-identical common UI kb. 93.7%;
- common UI files: 445.

Következtetés:
Belkin Cudy userspace donor prioritás:
1. WR1200 V2/R26 2.4.x;
2. LT500D R25 2.4.16;
3. WR1300/WR2100 feature/switch donor;
4. WR1000 8/64 class referencia.

---

# 30. Belkin F9K1103 v1 — hardvertruth

Device:
**Belkin F9K1103 v1 / N750 DB**

Known board class:
- Ralink RT3883;
- 64 MB RAM;
- 8 MB flash;
- 2.4 GHz RT309x family / PCI companion architecture;
- RTL8367R-VB family gigabit switch;
- 2× USB 2.0;
- dual-band.

A projektben használt F9K1103-specific evidence:
- Padavan BN750DB/F9K1103 board definitions;
- modern OpenWrt F9K110x family support;
- stock-family uImage naming;
- F9K1103 stock firmware/emulation evidence for MAC variables.

Source precedence:
1. F9K1103-specific evidence;
2. F9K1109/F9K110x Belkin family;
3. RT-N56U RT3883 family;
4. generic assumptions last.

---

# 31. Fizikai Belkin jelenlegi OpenWrt truth

A felhasználó korrigálta:
a fizikai F9K1103-on futó OpenWrt image nem saját F9K1103 build.

Actual reference image:
`openwrt-19.07.0-ramips-rt3883-belkin_f9k1109v1-squashfs-sysupgrade.bin`

SHA-256 a donor workflow exact kontrollja szerint:
`b5bf1e194274cd4401969dac145ccfbc90f7b55a9a109253e9a5a5740941118c`

Ebből csak ezt következtethetjük:
- F9K1109 board support elég közel van ahhoz, hogy a fizikai eszközön működő referenciát adjon;
- switch/radio/flash/boot behavior értékes hardver-reference;
- nem szabad F9K1103 native truthnak nevezni.

OpenWrt 19 ezért:
**hardware reference, nem elsődleges Cudy runtime base.**

---

# 32. Miért lett LEDE 17.01.5 az elsődleges Belkin runtime base?

Mert:
1. LT500D/Cudy 2.4.16 = LEDE 17.01.5;
2. WR1200 Cudy 2.4.x = LEDE 17.01.5 lineage;
3. számos Cudy backend/LuCI/init contract ugyanazon régi LEDE platformból jön;
4. kevesebb userspace API-generációs eltérés várható;
5. Cudy frontend/backend portnál kevesebb compatibility adapter lehet szükséges.

Hardver driver/board support továbbra is a működő F9K1109/OpenWrt 19 és F9K110x reference-ekből backportolható.

Tehát:
```
F9K1109/OpenWrt19 = hardver-reference
F9K1103 DTS       = target board truth
LEDE 17.01.5      = runtime base
WR1200/LT500D     = Cudy userspace/UI donor
```

---

# 33. F9K1103 LEDE 17.01.5 port jelenlegi forrása

Repo:
`diablomike20/Belkin-F9K1103-Firmware`

Path:
`firmware/f9k1103-lede-17.01.5/`

README státusz:
PORT-WIP / build-verified intent / not physical boot verified.

Fő fájlok:
- `F9K1103.dts`;
- `build-lede-17.01.5.sh`;
- host compatibility patchek.

DTS:
- compatible F9K1103 / RT3883;
- RTL8367B-compatible SMI GPIO 1/2;
- reset GPIO abs25;
- WPS abs26;
- power GPIO0;
- LAN GPIO13;
- WAN GPIO12;
- USB GPIO9;
- SPI NOR;
- u-boot 0x000000–0x02ffff;
- env 0x030000–0x03ffff;
- factory 0x040000–0x04ffff;
- firmware 0x050000–0x7effff;
- user-cfg 0x7f0000–0x7fffff;
- Ethernet fixed gigabit RGMII;
- PCI Wi-Fi EEPROM factory+0x8000;
- WMAC EEPROM factory+0x0000;
- EHCI/OHCI enabled.

Network:
- LAN ports 0..3;
- WAN port 4;
- CPU port 5.

MAC:
- `HW_WAN_MAC`;
- `HW_LAN_MAC` from uboot-env.

Image:
- `IMAGE_SIZE := 7808k`;
- `UIMAGE_NAME := N750F9K1103VB`;
- intended loader-wrapped LZMA kernel;
- outer uImage compression none.

---

# 34. F9K1103 LEDE build history és aktuális blocker

Korábbi sok build eljutott egyre tovább.
Régi blocker:
lzma-loader outer PLATFORM collision → üres board/object nevek, pl. `cc -o .o`.

Ez **már nem az aktuális hiba**.

Legutóbbi:
Run `36959975523`
Job `110691296857`
Branch `lede-17.01.5-fix-board-token`
Head `3ef3cb7f6291d6b91ed09cf2a1cd15ece5fd5a86`
Result FAIL.

Sikeresen elkészül:
- DTB;
- patched kernel;
- LZMA kernel;
- loader sources;
- head.o;
- loader.o;
- cache.o;
- board-ralink.o;
- printf.o;
- LzmaDecode.o;
- data.o;
- linked `loader`.

Aktuális fail:
```
mipsel-openwrt-linux-musl-objcopy -O binary ... loader loader.bin
Warning: Writing section '.text' to huge (ie negative) file offset 0xffffffff81800000.
loader.bin[.text]: File truncated
```

A `PLATFORM="ralink"` jelenleg helyesen továbbadódik.

### FU9 első build-RE feladata

Ne találgass vakon.

1. Reproduce és mentsd:
   - `readelf -h loader`;
   - `readelf -S loader`;
   - `readelf -l loader`;
   - `objdump -h loader`;
   közvetlenül az objcopy előtt.
2. Vesd össze:
   - LEDE v17.01.5 lzma-loader;
   - OpenWrt v19.07.0 lzma-loader.
3. Külön vizsgáld a v19 változásait:
   - linker driver direct `ld` vs `gcc`;
   - `-nostartfiles`;
   - `-z max-page-size=4096`;
   - `.MIPS.abiflags` removal;
   - linker/objcopy section LMA/VMA kezelés.
4. Minimal patch.
5. GitHub Actions rebuild.
6. SUCCESS után:
   - image present;
   - size <= 0x7a0000;
   - uImage magic;
   - header CRC;
   - payload CRC;
   - name `N750F9K1103VB`;
   - SquashFS present;
   - initramfs present;
   - hashes.
7. Physical bootot csak explicit user döntéssel.

---

# 35. Belkin LEDE után következő Cudy-port architektúra

Csak LEDE build SUCCESS után.

Javasolt:
```
Belkin hardware
  ↓
native F9K1103 LEDE 17.01.5
  ↓
Belkin target adapters
  ↓
Cudy WR1200/LT500D userspace + WebGUI
```

Ne portold át vakon a Cudy hardver-specific binárisokat:
- MT7628 vendor Wi-Fi;
- MT7663;
- R25 bdinfo layout;
- cellular/gcom;
- R25 MTD assumptions;
- oem-check;
- Cudy-specific radio calibration.

Amit nagy eséllyel lehet donor-alapon újrahasználni:
- HTML/CSS/JS;
- LuCI controller/model/view nagy része;
- generic UCI semantics;
- LAN/DHCP/WAN;
- firewall/NAT;
- DDNS;
- VPN userland ahol package rendelkezésre áll;
- diagnostics;
- logs;
- UI registry;
- theme;
- Developer read-only surfaces adapterrel.

---

# 36. Firmware archive policy

A firmware-masterben:
- csak tényleges firmware/package/archive fájl;
- firmware lineage manifest;
- SHA-256;
- provenance/classification.

Search logok, HTML, RE reportok:
**nem keverendők** a firmware-only ZIP belsejébe.

Külön documentation ZIP tartalmazza:
- docs;
- reports;
- source extracts;
- artifact manifests;
- prompt.

---

# 37. Repo és workflow térkép

## Website-downloader
`diablomike20/Website-downloader`

FU6/FU7/FU8 forensics branch család.

Fontos run/artifact:
- FU7 clean firmware archives run 36645143237;
  - 11068611598 dev firmware clean master;
  - 11067574831 OpenWrt intermediary clean.
- C200P 2.5.15 capture run 36782112092.
- C200P rootfs diff run 36784922560.
- P2 stable capture run 36784740496 / artifact 11129026897.
- P2 adjacent diff run 36786437705.
- P2 public 2.4.22→2.4.29 run 36790617782.
- P2 backend ownership run 36791261165.
- R25 management/static workflows CP11–14 line.

## Belkin repo
`diablomike20/Belkin-F9K1103-Firmware`

Main:
Belkin target development.

Donor audit:
branch `cudy-donor-audit`.

LEDE active fix branch:
`lede-17.01.5-fix-board-token`.

---

# 38. Hard safety / preservation constraints

R25:
- ne írj bdinfo-t;
- ne generálj/használj random identity values;
- ne brute-force UUID/timestamp/suffix;
- ne hozz létre real rom_alpha-t;
- ne synthetic activation;
- ne flash-elj Candidate47-et explicit user döntés nélkül;
- ne flash-elj RG500 firmware-t EC200A-ra;
- ne törj 4G-t;
- TR-069 ne kerüljön vissza;
- ne transplant P2 files blindly.

Belkin:
- build és static validation előbb;
- fizikai flash/boot csak explicit user döntéssel;
- F9K1109 image-et hardware reference-ként kezeld;
- ne nevezd F9K1103 native buildnek;
- preserve recovery expectations;
- ne overwrite calibration/env/usercfg partíciót image recipe hibából.

---

# 39. Do-not-repeat register

NE ismételd:
- teljes R25 donor RE nulláról;
- Probe-97;
- random R25 2.5.x enumeration;
- timestamp spray;
- CloudFront suffix brute force;
- hidden emulator random-name brute force;
- R100 truth → R25 truth;
- hybrid 2.5.12 → official R25 claim;
- synthetic activation;
- bdinfo writes;
- normal features Developerbe áthelyezése;
- H09 OPKG refactor evidence nélkül;
- P2 blind transplant;
- Candidate-03 rerun;
- korábbi F9K1103 lzma-loader PLATFORM hiba újranyomozása, hacsak új regresszió nem bizonyítja.

---

# 40. Nyitott R25 feladatok — parkolt, de megőrzendő

- exact R25 CSP2.5 support artifact hunt;
- exact `bdinfo_check_uuid()` RE;
- exact hcshd legitimate upstream sender provenance;
- exact 2.4.16 support-session credential policy;
- H11 branding misses;
- Candidate47 physical boot gate;
- IPTV Hybrid-58 target gate;
- mature CSP2.5 contracts későbbi Integration-be;
- Developer/UI finomítások.

Ezek nem törlődtek, de a felhasználó aktuális P0-ja a Belkin LEDE build.

---

# 41. Nyitott Belkin feladatok — aktuális sorrend

P0.1:
Fix LEDE lzma-loader objcopy high-VMA failure.

P0.2:
LEDE workflow SUCCESS.

P0.3:
Static image validation + SHA manifest.

P0.4:
Inspect final rootfs footprint 8 MB class limit mellett.

P0.5:
Külön physical test mission prompt, csak ha a user kéri.

P1:
Cudy donor userspace minimum-port:
WR1200 V2 2.4.x + LT500D 2.4.16.

P1:
Belkin adapter layer:
- switch/VLAN;
- Wi-Fi;
- LAN/WAN;
- USB;
- LED/button;
- system status.

P2:
Cudy UI fidelity expansion.

P2:
Developer read-only subset.

---

# 42. Milyen eredmény számít „LEDE build kész”-nek?

Nem elég:
- workflow elindult;
- toolchain build;
- kernel build;
- valamilyen bin fájl létrejött.

Minimum COMPLETE:
- GitHub Actions conclusion SUCCESS;
- F9K1103-specific sysupgrade artifact ténylegesen létrejött;
- initramfs artifact létrejött;
- uImage magic PASS;
- uImage name PASS;
- header CRC PASS;
- data CRC PASS;
- size partition limit alatt;
- SquashFS megtalálható;
- build source commit rögzítve;
- SHA256SUMS;
- artifact letölthető;
- státusz továbbra is STATIC/BUILD VERIFIED, amíg physical boot nincs.

---

# 43. Mit jelent majd „Belkin Cudy port kész”?

Későbbi definíció, nem jelenlegi állapot.

Minimum:
- native F9K1103 LEDE boot;
- Ethernet LAN/WAN;
- switch/VLAN;
- 2.4/5 GHz;
- USB;
- LEDs/buttons;
- persistent overlay;
- LuCI;
- Cudy WebGUI;
- dashboard live data;
- General/Advanced pages;
- configuration writes target adapteren;
- no fake data;
- recovery path;
- firmware update safe path;
- resource footprint 8 MB flash / 64 MB RAM keretben.

---

# 44. Felhasználói kommunikációs protokoll

Magyarul válaszolj.

A user rövid végrehajtási szavai:
- hajrá;
- mehet;
- csináld;
- folytasd.

Ezek = tool work azonnal.

Ne kérj újra olyan információt, ami Project Sourcesban vagy handoffban benne van.

Hosszú buildnél:
- kevés update;
- GitHub Actions;
- exact run/job;
- failure esetén exact log;
- ne ígérj háttérmunkát.

---

# 45. Fájlnév / checkpoint konvenció

FU8 végső checkpoint:
**Checkpoint-14**.

A következő static checkpoint, ha az R25 vonal folytatódik:
**15**, ne készíts új CP14-et.

Az új chat neve:
**Firmware Unlock 9**.

FU9 artifactokhoz ajánlott prefix:
`fu_9-`

Belkin repository runtime source fájlokat ne nevezd át csak a prefix miatt.

---

# 46. Source precedence

Konfliktus esetén:

1. newest physical target evidence;
2. explicit newest user decision;
3. exact stock source/binary;
4. same-model older-version evidence;
5. close donor evidence;
6. generic architecture inference.

Belkin esetében:
1. F9K1103-specific evidence;
2. actual physical behavior;
3. F9K1109/F9K110x;
4. RT-N56U;
5. generic RT3883.

Cudy esetében:
1. exact R25 stock/physical;
2. same R25 older firmware;
3. C200P/P2/R100/WR donor.

---

# 47. Utolsó projektállapot egy mondatban

Az LT500D/OpenCudy R25 ág már egy mélyen dokumentált, fizikailag bizonyított engineering platform saját OPKG/4G/Developer és vendor-management RE eredményekkel; a projekt új P0-ja most egy **valódi F9K1103 v1 LEDE 17.01.5 build létrehozása**, amelynek utolsó buildje már túljutott a korábbi board-token problémán, és jelenleg a lzma-loader high-VMA `objcopy` truncation hibáján áll, ami után a WR1200/LT500D Cudy userspace port indulhat.

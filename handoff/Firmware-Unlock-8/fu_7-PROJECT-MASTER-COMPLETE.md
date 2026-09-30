# fu_7 — Cudy LT500D V2 / R25 — OpenCudy
# Complete master project documentation

Date: 2026-09-30
Successor: Firmware Unlock 8

---

# 0. Project purpose

OpenCudy is a multi-branch engineering project around the Cudy LT500D V2 / R25.

The project includes:

- stock Cudy R25 firmware reverse engineering;
- physical LT500D target unlock;
- stable SSH/Telnet engineering access;
- stock/live-stock 4G preservation;
- OPKG package management;
- Cudy app / cloud / local discovery separation;
- Cudy Factory Debug / maintenance reverse engineering;
- Developer UI;
- theme and branding;
- donor WebGUI/emulator forensics;
- OpenWrt 23.05.5 donor-fidelity frontend/backend integration;
- CSP2.5 donor mining;
- OTA / update selection / activation research;
- exact R25 CSP2.5 firmware hunt;
- cross-model Cudy beta/dev/internal/recovery firmware collection;
- P2/R91/RG500 engineering donor analysis;
- C200P internal/unlisted emulator firmware analysis.

The core engineering rule is:

Stock Cudy R25 behavior is the primary truth. Deviations remain only when unlock or engineering requirements demonstrably require them.

A source file existing in a donor does not prove R25 runtime capability, Developer placement, or target compatibility.

---

# 1. Primary physical target

Model: Cudy LT500D V2.0
Board/devtype: R25
Region: EU
Country: DE

Hardware:
- MediaTek MT7628AN
- MIPS24KEc
- Linux 4.4.140
- 128 MiB RAM
- 16 MiB NOR
- 5 GHz PCIe MT7663E family, PCI 14c3:7663
- 2.4 GHz MT7628 vendor Wi-Fi

Cellular:
- Quectel EC200A-EL
- modem firmware EC200AELV1LAR02A03M08
- USB VID:PID 2c7c:6005
- data path cdc_ether -> usb0
- network.4g works on usb0

Identity:
- system.board.model LT500D V2.0
- system.board.rom R25
- system.board.wan_port 3
- system.board.ports 4
- bdinfo region EU
- bdinfo country DE
- bdinfo checkuuid OK

The physical R25 router is authoritative target truth.

The user primarily uses the router in 4G/SIM mode. Breaking 4G is a P0 regression.

---

# 2. Canonical stock R25 firmware

Stock file:
LT500V2-R25-2.4.16-20250804-150319-flash.bin

SHA-256:
57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6

Base:
- LEDE 17.01.5
- ramips / mt76x8
- mipsel_24kc
- Linux 4.4.140

Known image concepts:
- full stock image contains Cudy full-flash wrapper/signature material;
- router firmware region contains legacy uImage + SquashFS + JFFS2 padding/trailer;
- supported device identity R25;
- uImage/kernel region has repeatedly been used as immutable compatibility anchor.

---

# 3. R25 flash/storage truth

Primary partition layout:

- mtd0 u-boot: offset 0x000000, size 0x030000
- mtd1 u-boot-env: offset 0x030000, size 0x010000
- mtd2 factory: offset 0x040000, size 0x010000
- mtd6 firmware: offset 0x050000, size 0xF80000
- mtd3 debug: offset 0xFD0000, size 0x010000
- mtd4 backup: offset 0xFE0000, size 0x010000
- mtd5 bdinfo: offset 0xFF0000, size 0x010000
- mtd7 kernel / mtd8 rootfs / mtd9 rootfs_data are runtime children.

Mount model:
- /dev/root mounted as /rom, SquashFS read-only
- /dev/mtdblock9 mounted as /overlay, JFFS2 read-write
- overlayfs merged as /

Important stock-truth rule:

Factory SquashFS alone is not complete stock runtime truth.

Authoritative baseline:
factory SquashFS + stock firstboot/uci-defaults materialization + normal runtime semantics.

Stock 99_oem legitimately performs materialization such as:
- runtime Wi-Fi script changes;
- cellular eth1 -> usb0 migration;
- IPTV CBI placement;
- other OEM state.

Never call all runtime differences modifications merely because they differ from immutable /rom.

---

# 4. Evidence vocabulary

TARGET_VERIFIED:
physically proven on the real R25.

LIFECYCLE_VERIFIED:
full physical lifecycle proven.

TARGET_OBSERVED:
physically observed but not necessarily a complete gate.

SOURCE_VERIFIED:
direct source/rootfs/binary proof.

R25_SOURCE_VERIFIED:
direct proof from stock R25 source.

STATIC_VERIFIED:
offline/static checks pass.

WEB_VERIFIED:
public web evidence.

EMULATOR_VERIFIED:
Cudy emulator source/runtime evidence.

CROSS_DONOR_CORROBORATED:
another Cudy model corroborates a mechanism.

ARCHITECTURAL_LEAD:
useful clue, not target truth.

TARGET_REQUIRED:
must be tested on physical target.

UNKNOWN / NOT FOUND:
no closed proof.

Never silently upgrade an evidence label.

---

# 5. Physically proven OpenCudy lineage

Important milestones:

ENG08:
- working physical 4G baseline;
- stock/live-stock cellular restored;
- unlock separated from cellular modifications.

H09:
- OPKG package manager TARGET_VERIFIED and LIFECYCLE_VERIFIED.

H11-02:
- installer/runtime TARGET_VERIFIED;
- H09 integrity preserved;
- JFFS2 preserved;
- 4G preserved;
- dark theme observed;
- branding remained partial.

Developer V2 READONLY-02:
- target probe PASS;
- target verify PASS;
- non-mutating command selftest PASS.

Developer V3:
- 8 categories;
- 24 core engineering features;
- 54 native hidden/conditional catalog entries;
- narrow ownership model.

Developer V4:
- CLEAN branch removed normal-UI duplication;
- later handoff identifies CLEAN-06 as the proven Developer branch.

Current physically proven cumulative runtime lineage:
RE-LT500V2-R25-OPENCUDY-CUMULATIVE-27-TARGET-INSTALLABLE.tar.gz

C27 target verification included:
- service state;
- auto_upgrade=0;
- CWMP policy off;
- OPKG reconstructed state 127/127/86;
- watchdog;
- 4G on usb0;
- Developer V4 CLEAN-06.

C27 is a cumulative runtime installable package lineage, not a claim that a final production flash image is complete.

---

# 6. Candidate 47 raw image

Sysupgrade candidate:
RE-OPEN-CUDY-LT500V2-R25-C27-SYSUPGRADE-CANDIDATE-47.bin

SHA-256:
8d51bc017a3e275c0ce3a5c05a659a4a3c4f55bb96370d0fabc81f3d1470a060

Size:
12058779 bytes

Proven:
- starts with unchanged stock R25 uImage;
- stock GUI accepted upload identity;
- sysupgrade -T returned success;
- image format gate is target-verified.

Not proven:
- actual flash;
- actual boot;
- long-term lifecycle.

Full-flash archival/structural candidate:
RE-OPEN-CUDY-LT500V2-R25-C27-FULLFLASH-CANDIDATE-47.bin

SHA-256:
7118cfd798da459fc7d5ea0350501ec4a5bd088e0449d953dabf15929f89694f

Candidate 47 must never be described as booted unless new physical evidence proves that.

---

# 7. Unlock delta ledger

Keep as UNLOCK_REQUIRED:
- Dropbear local bdinfo-dbg startup-gate bypass;
- Telnet startup-gate bypass under the OpenCudy engineering policy;
- stable engineering root access;
- installed sysupgrade unlock;
- neutralization of root password replacement where required by the chosen unlock lineage.

Keep as UNLOCK_PERSISTENCE:
- scheduled vendor automatic OTA suppression.

Explicit project policy:
- TR-069/CWMP excluded.

Not inherently required for unlock:
- disabling hcshd;
- rewriting cellular scripts;
- rewriting antenna GPIO logic;
- disabling every Cudy cloud component;
- globally forcing bdinfo dbg OK;
- changing modem firmware.

Later investigation showed:
- the kernel/uImage region remained stock-identical in relevant states;
- several vendor binaries remained stock-identical;
- main unlock deltas were localized init/policy/access gates.

---

# 8. bdinfo / factory / debug / development model

Do not confuse these:

1. bdinfo factory — manufacturing/factory state.
2. /etc/rom_develop — runtime Cudy Test Only marker.
3. /rom/etc/rom_develop — immutable development-image marker.
4. bdinfo dbg — factory debug/maintenance authorization.
5. OpenCudy Developer — project engineering control plane.
6. hcshd — separate stock maintenance daemon.
7. debug MTD partition — sysupgrade/log-related area, not the debug token.
8. Linux debugfs — unrelated.

Factory Debug algorithm was reverse engineered from the R25 libbdinfo implementation.

Observed token path includes:
- raw /proc/sys/dev/flash_uuid;
- bdinfo hmac;
- literal @2025;
- SHA-256;
- lowercase hex;
- exactly 64 bytes in /etc/rom_dbg.

The retail /etc/rom_release marker is a separate decision gate.

Later physical lifecycle evidence:
- baseline: dbg FAIL, rom_release present, rom_dbg absent;
- enable: dbg OK, runtime rom_release absent, rom_dbg size 64;
- disable: baseline restored;
- Telnet Debug ON gives direct root ash;
- Debug OFF gives login prompt;
- /etc/rom_develop can display the stock Test Only watermark.

Normal OpenCudy should not globally forge bdinfo dbg=OK.

bdinfo is provisioning/integrity state and ordinary experiments must not write it.

---

# 9. bdinfo integrity / tamper model

Project RE separated four different security layers:

1. bdinfo authenticity
   - RSA/MD5/DES-obfuscated provisioning concepts.
2. device identity consistency
   - checkuuid / fuuid / hmac / flash_uuid family.
3. debug/access policy
   - bdinfo dbg / SSH / Telnet / console / hidden Terminal.
4. firmware authenticity
   - oem-check / Cudy RSA / U-Boot recovery RSA.

Important correction:
bdinfo integrity mechanisms are not evidence that SquashFS/kernel is continuously tamper-checked at runtime.

Do not conflate tamper/integrity with service retry/churn.

---

# 10. OPKG H09

Exact old OPKG lineage:
9f61f7acf3845d2e09675b49fec5d783d57eb780, 2017-12-08

Architecture:
mipsel_24kc

Later physical inventory:
127 installed records:
- 41 userland/base reconstructed state;
- 86 stock-ROM kmod records.

H09 proved:
- Installed-Size parser;
- persistent overlay accounting;
- 1 MiB reserve;
- native filesystem-space gate;
- cached-feed size resolver;
- noaction/dry-run planning;
- actual payload extraction;
- list-upgradable eligibility;
- protected-package policy;
- HOLD;
- release HOLD;
- named upgrade;
- remove;
- cleanup/restoration.

Core examples locked:
- rpcd
- uclient-fetch
- libuclient
- libubox
- luci-base
- libblobmsg-json

No Upgrade All.
No force flags.

UI ownership:
Advanced -> System -> Package Manager

OPKG is not a Developer feature.

H09 is a frozen subsystem. Do not refactor it without a concrete regression reason.

---

# 11. Theme / Branding H11

H11 introduced controlled dark-theme/branding work.

Identity gate was corrected to:
- LT500D family identity
- R25 board identity

Physically observed:
- H11 install/runtime target verified;
- dark theme works;
- OpenCudy footer appears.

Known visual branding misses:
1. Dashboard System card remained partial.
2. System Status firmware row showed raw stock version.
3. General -> Firmware / Online Update showed raw stock version.

Therefore branding consistency remained PARTIAL, not full PASS.

---

# 12. Developer UI lineage

Early V1:
- Terminal;
- Sandbox/Telnet;
- SSH;
- engineering status.

V2:
- 6 categories;
- 16 features;
- read-only backend hardening.

V3:
- 8 categories;
- 24 core engineering features;
- 54 native hidden/conditional catalog entries.

V4 CLEAN:
- normal Cudy UI functions are not duplicated;
- genuine maintenance/engineering functions remain;
- donor hidden catalog remains as Source/RE evidence;
- security-sensitive actions remain explicitly gated;
- TR-069 absent.

Typical core engineering surfaces:
- Terminal
- Telnet
- SSH
- identity
- hardware
- kernel/uptime
- storage/MTD
- interfaces/routes
- cellular status
- USB/modem inventory
- services
- OPKG state
- Cudy framework
- wireless runtime
- modules/listeners
- boot/cron
- overlay changes
- VPN runtime
- logs
- engineering snapshot/export

Important correction:
Raw AT, Modem Reset, Wireless Chart, Probe List, logs, VPN and similar technical-looking pages may be normal donor features. A technical appearance does not make a feature Developer-only.

---

# 13. Cudy app / cloud / management separation

Do not treat every Cudy management component as TR-069.

Separate:

A) TR-069/CWMP remote provisioning:
- excluded by project policy.

B) Cudy device identity/cloud binding:
- FUUID/UUID, cmsd and selected cloud registration/session concepts may be needed for the Cudy app.

C) Local app discovery:
- cmagent + mosquitto + umdns-like local path.

The project learned that disabling all cloud-like components can break app identity/binding while adding no value to the TR-069 exclusion goal.

The desired architecture is:
- CWMP remote management OFF;
- vendor remote firmware control OFF where required by project policy;
- local app discovery ON;
- required device identity ON;
- only necessary cloud/session components preserved.

---

# 14. Cellular / 4G

Stock R25 modem-control chain:
gcom -> /dev/ttyUSB1 -> AT commands.

Working data path:
EC200A-EL -> cdc_ether -> usb0.

ENG07 -> ENG08 lesson:
4G breakage was a later runtime/rebuild problem, not a necessary unlock effect.

Normal rule:
cellular and antenna behavior start from stock/live-stock R25 truth.

Do not replace R25 4G scripts just because a newer donor contains newer code.

---

# 15. Watchdog and performance

Watchdog:
- /dev/watchdog and /dev/watchdog0;
- owned by PID1/procd;
- timeout 30 sec;
- feed frequency 5 sec;
- normal architecture.

A multi-hour target capture did not establish a persistent gcom/4G/watchdog/network restart loop.

Performance later improved according to the user.

Performance/retry is acceptance/regression monitoring, not an excuse to re-open already closed unlock decisions.

---

# 16. OpenWrt 23.05.5 donor-fidelity frontend/integration branch

Long-term UI goal:
full Cudy/LEDE WebGUI parity under OpenWrt 23.05.5.

Standalone target:
www/cudy-static

Primary donor:
LEDE/Cudy 2.4.16

Secondary donor:
LT15E / R58 / 2.2.7

CSP2.5 donor:
LT300V3 / R100 / 2.5.12

Permanent:
TR-069 excluded.

Roles:
- EM: emulator/web evidence.
- RE: firmware/source/binary/backend contracts.
- WS: frontend fidelity.
- Integration/Boss: target backend, CGI, merge, cumulative build, gates.

Historical cumulative V69:
RE-LT500D-V69-WIP-LEDE-DASHBOARD-TRUTH-04.zip

SHA-256:
e8e2f65fedb5d30a445a221f6f868c4fc50b861a9c441693d9ea4bf5932c36e0

Truth-04:
- controlled three-way merge;
- 11 modified files;
- 8 new files;
- 0 deletions;
- WISP Status/Settings and scan/join structure;
- SMS Inbox/New Message/Outbox;
- WAN DHCP/PPPoE/Static/L2TP/PPTP read-only donor forms;
- Devices columns and Device Information;
- unproven write/runtime actions disabled;
- final frontend/backend/registry/state/CGI audits PASS.

WS refinements:
- donor WISP state mapping;
- async:false removed;
- loading/error/stale/last-valid state model;
- request-generation guard;
- interface-name based Wi-Fi band guessing removed;
- backend must provide authoritative band evidence.

Historical V69 registry:
- 36 Advanced positions;
- 6 Developer categories;
- 16 Developer features.

Do not confuse this historical V69 registry with later physical-target Developer V3/V4.

---

# 17. Backend/integration invariants

Executable CGI:
- 0755 in source;
- 0755 in ZIP metadata;
- 0755 after clean extraction;
- 0755 after target install.

Boot-time chmod is defense-in-depth only.

JSON CGI purity:
stdout = CGI headers + blank line + exactly one JSON value.
Diagnostics go to stderr.

Devices:
- normalized MAC is authoritative merge key;
- one MAC -> one output row;
- hostapd/iwinfo association beats bridge FDB interface inference;
- DHCP hostname must not override explicit luci.devname;
- DHCP lease is not online proof;
- neighbour STALE is not session-alive proof;
- bridge membership is not Wi-Fi station authority.

Cross-feature one-owner:
- cellular bearer/session belongs to Cellular owner;
- WISP must not mutate it;
- firewall policy belongs to firewall owner;
- accounting status GET must not write state;
- VPN MAC policy has one authoritative state.

---

# 18. IPTV / Ethernet / Hybrid-58

R25 stock IPTV mode4 backend has 16 profiles.

Physical mapping evidence:
- wan_port=3;
- PHY0/1/2 LAN;
- PHY3 WAN;
- CPU6.

Stock cellular mode can fold port3 into LAN and change VLAN layout.

User normally uses 4G.
Stock IPTV Apply may be disruptive because it expects Ethernet-WAN semantics.

Hybrid-58 was prepared to preserve usb0 Internet while adapting IPTV behavior.

Status:
STATIC_VERIFIED / TARGET_REQUIRED unless later physical evidence supersedes it.

---

# 19. R25 OTA API

Stock OTA family includes i18n TEST/PROD and CN TEST/PROD.

Request identity includes headers such as:
- fuuid
- raw vr
- devtype
- lan
- token

JSON includes:
- mac
- firmwarevr
- region
- optional modulevr
- optional isfull

R25 2.4.16 beta normalization:
remove literal Beta from firmwarevr.

R100 CSP2.5 normalization:
remove lowercase b.

That is a real source-level generation change.

---

# 20. Probe-97 closed OTA finding

Exact strings:
OLD 2.1.1-20240419-090237
STOCK 2.4.16-20250804-150319
REAL/HYBRID 2.5.12-20260518-234632

3x3 split:
- HTTP vr varied OLD/STOCK/REAL
- JSON firmwarevr varied OLD/STOCK/REAL

Observed:
- JSON OLD -> stock 2.4.16 object
- JSON STOCK -> empty
- JSON REAL -> empty
- HTTP vr variation did not change tested selection.

Conclusion:
JSON firmwarevr drove the tested selection.

Do not repeat this matrix.
Do not resume random firmwarevr enumeration.

---

# 21. R25 publication objects

Four TEST/PROD/CN CloudFront objects for stock 2.4.16 were captured.

All:
- 12,124,315 bytes
- MD5 dc9ac8a6cae00621ab42536e35701d6a
- SHA-256 equal to retail stock image.

They prove staging/production publication behavior, not hidden CSP2.5 availability.

---

# 22. Activation

R100 CSP2.5 source proves an activation mechanism:
- S99activate;
- checkuuid/serial/country/activate gates;
- wait for .timeclock;
- sleep 86400;
- activation event endpoint;
- ret==0 -> activate=1.

Hybrid target previously naturally showed activation process and sleep-86400 state.

Not proven:
- activation means beta cohort;
- activation changes OTA eligibility;
- official R25 registration;
- activation is required for R25 CSP2.5.

Never manually trigger synthetic activation.

At a later point the user explicitly chose to leave the router untouched while natural activation/lifecycle could progress, and to continue static/web research instead.

---

# 23. R100 CSP2.5 donor

Donor:
LT300V3-R100-2.5.12-20260518-234632

Inner BIN SHA-256:
03641ed863911618155ddb55ed2c45f4c23abd330a4e171bff4491ffcda49a82

Critical finding:
CSP2.5 is still based on the old Cudy LEDE 17.01.5 / Linux 4.4.140 / MT7628 architecture rather than a migration to modern OpenWrt.

Real CSP2.5 features include:
- Packet Capture / tcpdump;
- https-dns-proxy / encrypted DNS;
- AdShield;
- cloud management UI;
- mesh/update evolution;
- expanded cellular vendor handling.

R100 is donor truth only.
It is not official R25 proof.

---

# 24. R25 CSP2.5 hybrid lab state

A physical R25 later ran a CSP2.5-derived hybrid state:
- system.board.rom R25;
- /etc/rom_version 2.5.12-20260518-234632;
- bdinfo checkuuid OK.

Correct label:
TARGET_VERIFIED physical R25 + CSP2.5-derived hybrid userspace/version state.

Incorrect label:
official R25 2.5.12 firmware.

Live MTD evidence showed:
- R25 stock kernel/uImage region;
- CSP2.5-derived rebuilt rootfs;
- 2.5.12 rom_version in overlay;
- engineering lineage traces.

This lab state is valuable but is not an artifact-proven official R25 CSP2.5 release.

---

# 25. Exact R25 CSP2.5 hunt

Current exact R25 CSP2.5 firmware artifact:
UNKNOWN / NOT FOUND.

Latest public known R25 package:
LT500V2-R25-2.4.16-20250804-150319-flash.zip

Verified distribution clues:
- LT500/LT500D private firmware delivery via support exists.
- CSP2.5 beta support-email delivery exists for other Cudy models.
- C200P proves an unlisted exact emulator build can persist as a canonical Cudy CDN object.

Already negative:
- R25 + R100 2.5.12 timestamp candidate;
- R25 + C200P 06-18 timestamp candidate;
- R25 + C200P AC_Cloud 06-22 candidate;
- R25 + public C200P 2.5.15 timestamp candidate;
- hidden LT500/LT500D emulator name variants;
- large public comment corpus exact R25/LT500 2.5 token.

Do not repeat random timestamp sprays.

Best next evidence:
- exact support attachment filename;
- screenshot showing full build;
- first-party page/theme JSON;
- indexed exact filename residue;
- forum/support mirror;
- AC_Cloud/JS source residual with LT500/R25 exact vr.

---

# 26. C200P exact unlisted/internal build

Emulator identity:
C200P V1.0 / R74 / 2.5.14-20260618-150931

Exact first-party ZIP:
C200P-R74-2.5.14-20260618-150931-flash.zip

Outer SHA-256:
a4f5f6494bcbdf41bfcd8573a22531fbd2115b5cb2769f5f44da213a900a7e98

Inner BIN SHA-256:
8ba6c51d13d72d2871a1b5e8bbcb4318c2fd4234898f8c1e9e6c30502913e0e8

Proven classification:
- first-party Cudy build: yes;
- valid flash package: yes;
- exact emulator build: yes;
- currently unlisted: yes.

Strong inference:
- pre-release/internal.

Not proven:
- developer/debug image;
- beta image.

Rootfs contains real Cudy cloud/SSH/cmsd/cmagent functionality.

The emulator Demo hoster, emulator_token_stub and mock APIs come from the emulator wrapper, not the firmware rootfs.

C200P is one of the highest-value CSP2.5 internal/pre-release donors for future hidden-feature analysis.

---

# 27. Emulator forensic archive

Website-downloader:
diablomike20/Website-downloader

Historical FU6 forensic branch:
fu_6-cudy-forensic

Latest documented full emulator archive:
- 90 models;
- 90 completed;
- 0 failed;
- 34,769 files;
- 527,278,057 raw bytes;
- AC_Cloud 325 files;
- master routes 12,431.

Artifact ID:
11018311218

Digest:
83e407ddbc1389355e4418f3f9a605b32227946cc7e8f680b05b33e5060bc02a

Crawler lessons:
- GET-only;
- raw byte fidelity;
- route extraction;
- HTML entity decode;
- dotted-model directory fix;
- real asset extension preservation;
- query collision disambiguation;
- cbi_xhr_load query snapshots;
- AC_Cloud mock API capture;
- per-model failure isolation.

---

# 28. Candidate-02 / CLEAN-MERGE-03 / Candidate-03

Candidate-02:
RE-R100-R25-CSP25-SYSUPGRADE-CANDIDATE-02.bin

SHA-256:
47290d1c168c7991decdbedfdf1a12821a5fe9df237b1510960c00eac5311a52

Known status:
- STATIC_VERIFIED;
- target unverified;
- preserves R25 kernel/modules/bdinfo/5GHz;
- contains selected CSP2.5 donor features;
- no successful boot claim.

R125-LT500D-CSP25-CLEAN-MERGE-03:
- prepared;
- LT500D-focused CSP2.5 merge concept;
- preserve R25 Cellular/Mesh/2.4G/5G/combined wireless/Guest/IPTV;
- include CSP2.5 features only where supported;
- exclude TR-069;
- exclude unsupported donor-only functions;
- prepared, not installed/run in the recorded state.

R125-CAPTIVE-PORTAL-CANDIDATE-03-BACKEND:
- backend-only;
- default disabled;
- intended without auth/LuCI/network writes/restarts;
- DID NOT INSTALL;
- NO BACKUP EXISTS;
- exact failure cause is not established;
- do not rerun blindly.

---

# 29. Firmware Unlock 7 — broad Cudy dev/beta hunt

FU7 broadened the hunt from R25-only to:
any Cudy model, any platform, any development-like firmware.

High-value categories:
- beta;
- alpha;
- dev;
- test;
- engineering;
- debug;
- internal;
- preview;
- RC;
- support-private;
- removed/unlisted;
- recovery;
- intermediate/transition;
- Drive/Mega/MediaFire/forum/4PDA mirrors.

Rule from the user:
finding one is not the stopping point; download all accessible payloads.

---

# 30. Clean firmware archive policy

An error was identified in an earlier archive:
search/index/HITS/SUMMARY metadata had been mixed into a firmware collection.

Correct policy now:
- firmware master contains actual firmware/dev/beta/recovery binaries only;
- one common manifest;
- SHA-256 deduplication;
- search logs/evidence stay separate;
- OpenWrt intermediary Drive stays in a separate archive.

Firmware Unlock 8 must keep this rule.

---

# 31. FU7 actual dev/beta payloads recovered

WR3000:
WR3000-R31-2.4.2Beta-20250429-181532-sysupgrade.bin
size 14,945,036
SHA-256:
13d49b81fabab3ccf5335509086dbb9811882dc279ee47f77116065228e2a6a6

P2 stable router:
P2-R91-2.4.22-20251204-184925-sysupgrade.bin
SHA-256:
592c494eb5f44beabb427907003801845ea0d47d51db50b1d5b97d40e3166b58

P2 modem image:
P2_RG500_A09.bin
SHA-256:
7402449ddc19db64e42e41031d35b4a36f01e4d8b19219fcf3c4c6def897f52b

P2 CellularUpgrade:
R91-2.4.23b-20251208-CellularUpgrade.bin
SHA-256:
9d27fb4535dff565cd8bb632933dc8a583f514bfcb2a027c740ddee0bc4f5f13

P2 beta router:
P2-R91-2.4.29b-20260422-101502-sysupgrade.bin
SHA-256:
3f8dae3d42ad6ba7d1314022eac6bc007d03fac274196b2c802f2835ab21c3f9

TR1200:
R46-2.1.10Beta-20240530-103557-flash.zip
SHA-256:
57cfd4f6f1b782f5216b27ccf07dfbf535b028a08dc06d179fca70224be33e42

---

# 32. FU7 exact leads not yet recovered

WR3600H/R69 exact filename leads:
- R69-2.3.11Beta-20250429-100114-sysupgrade.zip
- WR3600H-R69-2.3.15Beta-20250916-202013-sysupgrade.zip

Historical exact filenames:
- LT450-R9-1.15.5beta-20221121-180014-flash.bin
- LT500-R9-1.15.5beta-20221121-180014-flash.bin

Payload not recovered in FU7.

Support corpus beta markers:
- 2.3.11Beta
- 2.3.12Beta
- 2.5.0b
- 2.5.1b
- 2.5.4b
- 2.5.10b
- 2.5.10b-20260624-151245
- 2.5.11b
- 2.5.14b
- 2.5.16b
- 2.5.28b

Known model associations from support evidence included:
- M3000 -> 2.5.0b
- M1200 -> 2.5.11b
- M1500 -> 2.3.12Beta
- M1300 -> 2.5.14b
- WR3000 V1 -> support-private latest beta delivery evidence
- WR3000H -> support-private 2.5.x evidence
- WR6500H -> beta/support lead

---

# 33. FU7 OpenWrt intermediary Drive

The Cudy OpenWrt/intermediate Drive is kept separate from the dev/beta master.

Original batch:
41 top-level downloaded files.

The clean recursive binary extraction/deduplication run produced 42 unique firmware binaries.

Examples:
- LT500 V2.0_V3.0
- LT300 v3
- WR1300 variants
- WR3000 family
- AP family
- M family
- RE/TR/X6 families
- WBR3000UAX data

These are valuable recovery/transition/system-acceptance donors.
They are not automatically dev/beta firmware.

---

# 34. P2/R91 deep developer audit

FU7 statically unpacked:
- outer artifacts;
- P2 packages;
- UBI volumes;
- rootfs;
- raw strings;
- controllers/CBIs;
- stable/beta tree diff;
- RG500 modem image.

Comparison:
P2 2.4.22 stable vs P2 2.4.29b beta

Results:
- 5 beta-only files;
- 354 stable-only files;
- 218 changed common files.

Beta-only files:
- /etc/hotplug.d/gcom/30-4g
- /etc/hotplug.d/tty/30-4g
- /etc/rom_research
- /usr/lib/4g/check.sh
- /usr/lib/4g/reup.sh

/etc/rom_research:
- empty marker;
- beta-only;
- no direct reader/consumer was proven in the audit.

Therefore:
do not treat rom_research as a universal developer-unlock switch.

---

# 35. P2 hidden/internal controls actually present

Both the P2 stable and beta router rootfs contain real routed/implemented functions:

- admin/system/terminal
- admin/system/sandbox
- admin/system/preset
- admin/system/firstboot
- admin/diag
- admin/network/gcom/atcmd
- admin/network/gcom/magic
- admin/network/gcom/reset
- admin/network/gcom/upgrade
- AirDump registry routes

Web Terminal:
- command input;
- Run button;
- luci.util.exec execution.

Sandbox:
- Telnet enable flag;
- commits with /etc/init.d/telnet reload.

Preset:
- configuration capture;
- encrypted backup/preset logic;
- generated factory-preset behavior.

Diagnostics:
- /usr/lib/diag scripts;
- diagnostic archive;
- encrypted diagnosis package.

AT Command:
- real input and modem backend.

These functions are not beta-exclusive. Many already exist in stable donor branches and several have R25 equivalents.

---

# 36. P2 beta 4G lifecycle delta

Beta-only hotplug and scripts include:
- gcom event re-up behavior;
- tty removal device cleanup;
- 4G status check loop;
- online/offline checks;
- debug-info collection;
- reset/re-up calls;
- IMEI/reg status checks;
- SMS send/receive paths;
- traffic statistics and limits.

This is one of the most valuable P2 -> R25 comparison targets.

But:
do not copy these files to R25 blindly.

Correct next audit:
exact R25 /usr/lib/4g vs P2 2.4.29b /usr/lib/4g, function by function.

---

# 37. RG500 A09 engineering evidence

P2_RG500_A09.bin contains strong modem engineering evidence.

Observed strings/components include:
- Ctrl+C enter DEBUG MODE
- debug_mode
- debug_mode=1
- PINTEST OR FASTBOOT OR RECOVERY OR DEBUG
- PIN TEST MODE
- factorytest
- factory test
- pctool_mode_detect_uart
- dl_cmd_set_debuginfo
- quec_pin_test_mode
- fastboot source component
- multiple UART and console paths
- research/factory-purpose download wording
- debug/test mode paths

This is real modem engineering infrastructure.

R25 consequence:
- useful as cross-donor engineering evidence;
- NOT directly flash-compatible with EC200A;
- do not write RG500 firmware to the R25 modem.

---

# 38. How much P2/RG500 is useful on R25?

High usefulness / already native or analogous:
- Terminal
- Sandbox/Telnet
- Preset
- Firstboot/factory-reset policy
- Diagnostics
- AT Command
- Modem Reset

These are not reasons to copy P2 files; they are comparison/gating references because R25 already has much of the same Cudy architecture.

Potentially useful donor deltas:
- newer 4G check/reup lifecycle;
- gcom hotplug;
- tty hotplug;
- feature gating changes.

Requires adaptation:
- modem firmware upgrade flow;
- Magic Swap;
- platform-specific lifecycle scripts.

Not directly usable:
- RG500 engineering firmware itself;
- R91/MT7981 boot images;
- RG500 factory/fastboot payload on EC200A.

---

# 39. C200P deeper-audit direction

C200P exact internal/unlisted 2.5.14 build is especially valuable because:
- the exact emulator build exists as a real first-party firmware package;
- emulator frontend source can be compared to real firmware rootfs;
- public later C200P firmware provides a natural delta target.

High-value comparison:
- internal 2.5.14 vs public successor;
- file tree;
- controllers;
- models;
- views;
- feature registry/resolver;
- SSH capability;
- batchcmd;
- mesh_tcpdump;
- mesh_diag;
- cloud-management delta;
- internal-only routes;
- develop/research/release/debug markers.

Do not call it a developer firmware until direct proof appears.

---

# 40. User working protocol

Language:
Hungarian.

User expects action.

Meaning of:
- hajrá
- mehet
- csináld
- folytasd

= proceed immediately.

Do not respond with repeated plans instead of work.

If a task can be done statically, do it without asking for router access.

Periodically create downloadable checkpoints.

Never claim verification status above evidence.

When giving router commands, heading exactly:
SSH terminálba:

BusyBox/ash compatible commands.

---

# 41. Hard safety constraints

Do not:
- write bdinfo;
- create real /etc/rom_alpha;
- manually activate;
- flash unaudited candidates;
- reboot unnecessarily;
- break 4G;
- restore TR-069/CWMP;
- assume donor compatibility;
- rerun Candidate-03 blindly;
- repeat closed OTA matrices;
- rewrite working Wireless/WISP without a concrete bug.

---

# 42. Candidate-03 current caution

Most recent user truth:
- Candidate-03 did not install.
- There is no backup from Candidate-03.
- Exact failure cause has not been established.
- Do not infer that it partly installed.
- Do not invent rollback availability.
- Do not rerun until real failure evidence is available and the user explicitly wants it.

---

# 43. Current major open tasks

P0:
- preserve physical target;
- exact R25 CSP2.5 artifact/support build hunt.

P0 donor:
- C200P internal build deep audit.

P0 dev hunt:
- continue all-model Cudy dev/beta/internal/recovery search;
- download every accessible payload;
- update clean firmware master.

P1:
- exact R25 vs P2 4G lifecycle diff;
- classify backportable changes.

P1 integration:
- preserve V69 lineage;
- later feed mature CSP2.5 contracts to EM/RE/WS/Integration.

P1 UI:
- H11 three branding misses.

P1 network:
- IPTV Hybrid-58 physical gate if/when user chooses.

P1 image:
- Candidate47 actual boot lifecycle only by explicit decision.

---

# 44. Do-not-repeat register

Do not redo:
- full donor RE from zero;
- Probe-97 3x3 OTA matrix;
- random R25 2.5.x enumeration;
- timestamp spray;
- CloudFront numeric suffix brute force;
- hidden emulator random-name brute force;
- R100 truth -> R25 truth conversion;
- hybrid 2.5.12 called official;
- synthetic activation;
- real rom_alpha;
- bdinfo writes;
- normal features copied into Developer;
- H09 OPKG refactor without a regression;
- P2 files blindly transplanted into R25;
- RG500 image flashed to EC200A;
- Candidate-03 rerun without evidence;
- TR-069 restored.

---

# 45. One-sentence current state

OpenCudy now has a physically proven C27 R25 runtime lineage with working 4G/access/OPKG/factory-debug engineering, a separate mature V69 donor-fidelity OpenWrt23 frontend lineage, a CSP2.5 donor-forensics corpus, an exact C200P unlisted internal/pre-release firmware proof, and an active all-model Cudy dev/beta firmware hunt whose newest deep donor is P2/R91/RG500.

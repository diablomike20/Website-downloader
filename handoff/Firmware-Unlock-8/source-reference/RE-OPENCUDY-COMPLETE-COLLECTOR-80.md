# RE-OPENCUDY-COMPLETE-COLLECTOR-80

Date: 2026-09-27
Project: Cudy LT500D V2 / R25 – OpenCudy
Language: Hungarian user interaction preferred
Purpose: complete resumable engineering handoff + CSP 2.5 / LT500D 3.0 beta hunt state

---

## 0. READ THIS FIRST

This project is NOT starting from scratch. A large amount of donor reverse engineering, target verification and controlled firmware work has already been completed.

Core rules:

1. Stock Cudy R25 behavior is the primary truth.
2. Do not redo donor RE unless a concrete unresolved question requires it.
3. `STATIC_VERIFIED` is not `TARGET_VERIFIED`.
4. Do not touch real `bdinfo` as part of ordinary experiments.
5. Do not create real `/etc/rom_alpha` for probes; use temporary copies/paths.
6. Do not flash a newly found LT500D 3.0 / CSP 2.5 beta merely to see whether it boots.
7. TR-069/CWMP is intentionally excluded from OpenCudy.
8. User wants exact Cudy UI fidelity for normal features; hidden/engineering features go under Developer.
9. User prefers direct progress and tangible artifacts; do not waste target time on static tasks that can be done locally.
10. Any newly created RE artifact filename should begin with `RE-`.

Target SSH command sections must use the heading exactly:

`SSH terminálba:`

Target shell is BusyBox/ash. Prefer `mkdir`, `cp`, `chmod`, `rm`; do not assume GNU utilities or `install`.

---

## 1. PHYSICAL TARGET TRUTH

Physical router:

- Cudy LT500D V2.0 / R25
- stock LEDE 17.01.5 / Cudy 2.4.16
- `/etc/rom_version = 2.4.16-20250804-150319`
- SoC: MediaTek MT7628AN
- CPU: MIPS24KEc
- kernel: 4.4.140
- RAM: 128 MiB
- NOR: 16 MiB
- `system.board.model='LT500D V2.0'`
- `system.board.rom='R25'`
- `system.board.wan_port='3'`
- `system.board.ports='4'`
- `system.board.simdet='1'`
- `system.board.iptv_mode='4'`
- `bdinfo model=LT500D V2.0`
- `bdinfo board=LT500D`
- `bdinfo version=1.0`
- `bdinfo region=EU`
- `bdinfo country=DE`

Cellular:

- modem: Quectel EC200A-EL
- modem firmware: `EC200AELV1LAR02A03M08`
- USB VID:PID: `2c7c:6005`
- physical path: EC200A-EL -> `cdc_ether` -> `usb0`
- `network.4g` physically works on `usb0`

The user keeps this router in 4G/SIM mode. Do not destroy the 4G path while experimenting with Ethernet/IPTV.

---

## 2. R25 FLASH / STORAGE TRUTH

Known MTD layout:

- mtd0 u-boot: offset `0x000000`, size `0x030000`
- mtd1 u-boot-env: offset `0x030000`, size `0x010000`
- mtd2 factory: offset `0x040000`, size `0x010000`
- mtd6 firmware: offset `0x050000`, size `0xF80000`
- mtd3 debug: offset `0xFD0000`, size `0x010000`
- mtd4 backup: offset `0xFE0000`, size `0x010000`
- mtd5 bdinfo: offset `0xFF0000`, size `0x010000`
- mtd7 kernel, mtd8 rootfs, mtd9 rootfs_data are runtime/dynamic children

Mount model:

- `/dev/root /rom squashfs ro`
- `/dev/mtdblock9 /overlay jffs2 rw`
- `overlayfs:/overlay /` merged runtime filesystem

Important: immutable `/rom` plus stock firstboot/uci-defaults materialization defines real stock runtime truth. Do not compare only immutable factory rootfs against live state and call all changes modifications.

Stock `/etc/uci-defaults/99_oem` performs important legitimate firstboot mutations including:

- `/sbin/wifi` runtime addition `sync_config "$@"`
- cellular `eth1` -> `usb0` migration
- IPTV CBI placement
- other OEM runtime materialization

---

## 3. CURRENT OPENCUDY BASELINE

Latest physically proven cumulative installable baseline in this handoff:

`RE-LT500V2-R25-OPENCUDY-CUMULATIVE-27-TARGET-INSTALLABLE.tar.gz`

C27 target verification PASS included:

- service state
- `auto_upgrade=0`
- CWMP policy off
- OPKG reconstructed state 127/127/86
- watchdog
- 4G on usb0
- Developer CLEAN-06

Do not interpret C27 as a complete final OpenCudy firmware image; it is the current proven cumulative runtime package lineage.

Raw image candidate:

`RE-OPEN-CUDY-LT500V2-R25-C27-SYSUPGRADE-CANDIDATE-47.bin`

Candidate 47 stock GUI upload / format validation:

- stock GUI accepted upload identity
- `sysupgrade -T` returned success
- actual flash/boot lifecycle was deliberately NOT performed
- state: image format TARGET_VERIFIED, actual flash lifecycle DEFERRED/TARGET_REQUIRED

Do not claim Candidate 47 booted unless new physical evidence exists.

---

## 4. STOCK R25 FIRMWARE IDENTITY

Original stock image:

`LT500V2-R25-2.4.16-20250804-150319-flash.bin`

SHA-256:
`57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

Known format:

- kernel uImage at `0x50000`
- SquashFS rootfs
- SquashFS v4 / XZ / 256 KiB block
- kernel CRCs valid
- target R25

---

## 5. DEBUG / FACTORY / DEVELOPER MODEL — DO NOT CONFUSE THESE

There are multiple distinct concepts:

1. `bdinfo factory` — manufacturing/factory state.
2. `/etc/rom_develop` — runtime stock “Test Only” UI marker.
3. `/rom/etc/rom_develop` — immutable development-image marker.
4. `bdinfo dbg` — factory debug/maintenance authorization state.
5. OpenCudy Developer — engineering control plane added by this project.
6. `hcshd` — separate stock maintenance service.
7. MTD partition named `debug` — sysupgrade log area, not debug auth token.
8. Linux debugfs/proc debug — unrelated.

Factory Debug token algorithm was reverse engineered and physically lifecycle-tested.

Inputs include:

- `/proc/sys/dev/flash_uuid`
- bdinfo hmac/factory
- `/etc/rom_release`
- `/rom/etc/rom_develop`
- `/etc/rom_dbg`

Observed token derivation path includes SHA256 and suffix `@2025`.

Physical lifecycle verified:

- baseline: dbg FAIL, rom_release present, rom_dbg absent
- enable: dbg OK, runtime rom_release absent, rom_dbg size 64
- disable: baseline restored
- Telnet with Debug ON gives direct root ash; OFF gives login prompt
- runtime `/etc/rom_develop` physically displays stock `Test Only` watermark

Relevant artifacts are included in this package under `evidence/factory-debug/`.

---

## 6. ACCESS / SERVICES

OpenCudy local policy bypasses only the local stock startup gates where required; it does not rewrite global provisioning state.

Dropbear:
- stock gate is `bdinfo dbg == OK`
- OpenCudy startup bypass exists locally
- global `bdinfo dbg=FAIL` remains retail default

Telnet:
- same local startup gate concept
- stock `/usr/libexec/login.sh`: Debug ON -> direct root ash; otherwise `/bin/login`

Autoupgrade:
- stock cron path false-gated in OpenCudy baseline

CWMP:
- disabled by project policy
- TR-069 permanently excluded from OpenCudy

hcshd:
- stock startup restored
- UDP 56791
- no evidence it needed to be disabled

Watchdog:
- PID1/procd
- timeout 30 / feed 5
- no patch required

---

## 7. DEVELOPER UI CURRENT STATE

Developer V4 CLEAN-06 is the proven branch in this handoff.

Architecture:

- separate Developer registry/page
- stock normal features remain in normal Cudy UI
- engineering and hidden functions are classified, not blindly exposed
- security-sensitive actions disabled unless explicitly gated
- read-only logs retained
- TR-069 absent

Historical Developer V3 inventory included 24 engineering features and a large native hidden/conditional catalog. Important categories included diagnostics, wireless, network, services, system, VPN and cellular-sensitive functions.

Do not move normal donor features into Developer merely because they were hidden in one runtime profile.

---

## 8. NORMAL UI / FEATURE FIDELITY PRINCIPLES

Project goal: full Cudy/LEDE WebGUI fidelity under OpenWrt 23.05.5.

Normal feature areas already mapped include:

- Dashboard
- General Settings
- Cellular
- SMS
- WAN/WISP
- Wireless 2.4/5 GHz
- Devices
- LAN/DHCP/IPv6
- VPN
- Advanced Network/Security/System
- Diagnostics

Known normal Advanced inventory is 36 positions. Do not replace donor-native behavior with invented generic OpenWrt behavior where donor source exists.

Frontend failure behavior should use Loading / Unavailable / Integration Required, not fake data.

---

## 9. IPTV / 4G

R25 stock IPTV mode4 backend has 16 profiles.

Physical Ethernet mapping evidence:

- R25 `wan_port=3`
- base PHY 0/1/2 LAN, PHY3 WAN, CPU6
- stock cellular-mode `99_oem` folds port3 into LAN and changes VLAN layout
- physical port3 link was observed

Because the user stays on SIM/4G, stock IPTV Apply is potentially disruptive: it is designed around Ethernet-WAN behavior.

Hybrid-58 was created to preserve `usb0` Internet while adapting IPTV behavior. It is STATIC_VERIFIED/TARGET_REQUIRED unless later evidence in included reports upgrades that status.

Relevant IPTV reports 51-58 and Hybrid-58 artifact are included.

---

# PART II — CUDY OTA / LT500D 3.0 CSP 2.5 HUNT

## 10. STOCK R25 OTA CLIENT

Stock `/sbin/autoupgrade` chooses endpoints by country and TEST state.

TEST selector:

- `bdinfo rdtest == 1` OR
- `/etc/rom_alpha` exists

Non-CN:

- TEST: `i18n-test.cudycloud.com`
- PROD: `i18n.cudycloud.com`

CN:

- TEST: `cn-api-test.cudycloud.com`
- PROD: `cn-api.cudycloud.com`

Core paths:

- `/device/v1/auth`
- `/device/v1/checkupdate`

R25 check request:

HTTP headers:
- `fuuid`
- raw `vr`
- `devtype`
- `lan`
- token

JSON:
- `mac`
- `firmwarevr`
- `region`
- optional `modulevr`
- optional `isfull`

R25 2.4.16 beta normalization:

`json_add_string firmwarevr "${firmwarevr/Beta/}"`

This strips literal `Beta` from JSON firmware version while raw HTTP `vr` remains unchanged.

Stock `modulevr` contains an apparent bug:

`$(cat /var/run/4g/getcgmr >/dev/null 2>&1)`

so output is normally discarded.

---

## 11. OTA EXPERIMENT SAFETY MODEL

All OTA experiments performed in this chat used temporary copies only.

The methodology was:

- copy `/sbin/autoupgrade` under `/tmp`
- redirect `/etc/rom_alpha` to a temporary marker
- redirect `/etc/token` to a temporary token
- redirect `/etc/fwinfo.json`
- redirect status file
- redirect firmware download file
- optionally redirect `/etc/rom_version` to a temporary version file

Real bdinfo was never rewritten.
Real `/etc/rom_alpha` was not enabled for these probes.
No discovered image was flashed.

Continue this methodology.

---

## 12. TARGET-VERIFIED OTA FINDINGS

### 12.1 TEST vs PROD

Using old known R25 version `2.1.1-20240419-090237`:

TEST returned target:
`2.4.16-20250804-150319`

TEST URL:
`https://d1jvyy13vm72kv.cloudfront.net/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_48004.bin`

PROD URL:
`https://d1jvyy13vm72kv.cloudfront.net/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_20729.bin`

CN TEST:
`https://cn-cf.cudycloud.com/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_95221.bin`

CN PROD:
`https://cn-cf.cudycloud.com/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_30196.bin`

All four downloaded payload objects were byte-for-byte identical:

- size 12,124,315 bytes
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`
- SHA-256 `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

They are identical to the known retail stock 2.4.16 image.

TEST metadata predates PROD metadata, proving a real staging -> production publication path, but current staging payload was still the final retail image.

### 12.2 exact devtype

With an old firmware version:

- `R25` -> update offered
- `LT500` -> empty
- `LT500V2` -> empty
- `LT500D` -> empty
- `LT500V2-R25` -> empty

Exact `devtype=R25` is therefore a real observed eligibility selector.

### 12.3 version boundary

Observed:

- synthetic 0.0.0 -> 2.4.16 offered
- 1.15.28 -> 2.4.16 offered
- 2.1.1 -> 2.4.16 offered
- 2.4.15 -> 2.4.16 offered
- 2.4.16 with old timestamp -> empty
- exact 2.4.16 -> empty
- 2.4.16 with newer timestamp -> empty
- 2.4.17 -> empty
- 9.9.9 -> empty

Strong interpretation: the server treats semantic 2.4.16 as the update boundary; build timestamp does not make a same-version build “older”.

### 12.4 JSON firmwarevr vs HTTP vr

This was physically isolated.

- HTTP `vr=CURRENT`, JSON `firmwarevr=OLD` -> update offered
- HTTP `vr=OLD`, JSON `firmwarevr=CURRENT` -> no update

Therefore JSON `firmwarevr` drives version eligibility. HTTP `vr` is not sufficient by itself to trigger the update.

### 12.5 language/full/region

Observed matrices did not show a different firmware selection for:

- `auto`
- `en`
- `zh-cn`
- normal vs `isfull=1`
- EU vs CN region value within the forced endpoint experiment

Do not overgeneralize this beyond the tested conditions.

### 12.6 modem OTA

Temporary patched client sent real and synthetic module versions:

- `EC200AELV1LAR02A03M08`
- M07-like
- M01-like
- `0`

Both TEST and PROD continued to return:

`"module": {}`

No R25 EC200A modem OTA object has been discovered.

---

## 13. LT500D 3.0 / CSP 2.5 OFFICIAL STATE

Official Cudy software-platform update article:

`https://www.cudy.com/en-us/blogs/news/cudy-software-platform-updates`

LT500D 3.0 is listed in the CSP 2.5 support plan.

At the time of this handoff, public LT500D 3.0 download material still exposed 2.4.16, not a public 2.5.x package.

The public LT500D 3.0 filename observed:

`LT500V2-R25-2.4.16-20250804-150319-flash.zip`

The LT500D 2.0 download path also used the same R25 2.4.16 filename.

This means:

- V2 and V3 can share the same R25 router firmware at least on 2.4.16;
- a V3 modem/SKU change alone does not imply a different router board image;
- absence of public 2.5.x does not prove a support-only beta does not exist.

---

# PART III — LT300 V3 / R100 CSP 2.5.12 DONOR RE

## 14. USER-SUPPLIED CSP 2.5 DONOR

Source:

`LT300V3-R100-2.5.12-20260518-234632-flash.zip`

ZIP contains:

- vendor `md5.txt`
- `LT300V3-R100-2.5.12-20260518-234632-flash.bin`

flash.bin:

- size 10,551,452 bytes
- MD5 `7c8cf596029d0ce5940c5bafbb7a0fbd`
- SHA-256 `03641ed863911618155ddb55ed2c45f4c23abd330a4e171bff4491ffcda49a82`

A complete static extraction bundle is nested in this handoff:

`RE-LT300V3-R100-2.5.12-FIRMWARE-RE-78.zip`

It contains the original source image, carved regions, decompressed kernel, exact SquashFS, full extracted rootfs, manifests, comparison files and tools.

---

## 15. WHAT “DRIVES” LT300 V3 CSP 2.5.12

The most important answer to the user’s “kukkold meg mi hajtja” request:

### Bootloader

- U-Boot 1.1.3
- R100 board
- build date 2026-05-18

### Kernel / architecture

- Linux 4.4.140
- MIPS32r2 / MIPS24KEc
- MT7628AN family
- GCC 5.4.0 / LEDE-era toolchain
- kernel build strings expose Jenkins workspace path containing:
  `mtk_mt762x_router_v2.5/openwrt/17.01`

### Rootfs / userspace

- LEDE 17.01.5
- `DISTRIB_REVISION='2.5.12'`
- `DISTRIB_TARGET='ramips/mt7628'`
- `DISTRIB_ARCH='mipsel_24kc'`
- SquashFS 4.0
- XZ
- 256 KiB blocks
- 2,265 inodes
- `/etc/rom_version = 2.5.12-20260518-234632`

### Key conclusion

CSP 2.5.12 is NOT a migration to modern OpenWrt. It is a new Cudy software-platform generation still built on the old LEDE 17.01.5 / Linux 4.4.140 MT7628 stack.

This is extremely important for the OpenCudy project because new Cudy CSP 2.5 behavior can be donor-mined without assuming a modern OpenWrt architectural rewrite.

---

## 16. R100 HARDWARE

Embedded hardware evidence from kernel/device-tree analysis:

- board/model R100
- MT7628AN
- MIPS24KEc
- 64 MiB RAM
- 16 MiB SPI NOR
- Cudy partition scheme structurally very similar to R25
- 2 Ethernet ports
- single 2.4 GHz vendor Wi-Fi path
- vendor `mt7628.ko`

R100 Wi-Fi:

- MediaTek/Ralink vendor AP driver
- 2.4 GHz b/g/n
- HT20/HT40
- ra0 AP
- apcli0 WISP client
- guest/multi-SSID support

R25 differs mainly in RAM/ports/dual-band hardware expansion, not in the fundamental LEDE/MT7628 platform philosophy.

---

## 17. CSP 2.5 REAL FEATURE IMPLEMENTATION FOUND IN ROOTFS

The donor contains real implementation, not just marketing labels.

Confirmed examples:

### Packet Capture

- `/usr/sbin/tcpdump`
- LuCI model/view paths for tcpdump
- registry strings include `Packet Capture`

### Encrypted DNS / DoH

- `/usr/sbin/https-dns-proxy`
- `/etc/config/https-dns-proxy`
- stubby/getdns related stack

### AdShield

New paths include:

- `/usr/lib/lua/luci/apprpc/adshield.lua`
- `/usr/lib/lua/luci/controller/adshield.lua`
- CBI/model/view hierarchy
- `99-adshield` uci-default

### Cloud Management

New CBI/view/JS cloud management assets exist.

### Update / mesh evolution

- `meshupgrade`
- fwtool metadata integration
- newer automatic update workflow

The full path/hash tree diff against stock R25 2.4.16 is included in the reverse-engineered firmware package.

Tree comparison summary:

- R25 indexed entries: 2,636
- R100 indexed entries: 2,263
- R25-only: 634
- R100-only: 261
- common changed: 400
- common byte-identical: 1,602

Interpret these counts as cross-model + cross-version differences, not pure “2.4 -> 2.5” deltas.

---

## 18. CELLULAR FRAMEWORK EVOLUTION IN CSP 2.5

R100 CSP 2.5.12 contains generic Cudy cellular support including:

- `quectel.sh`
- `quectel2.sh`
- `quectel-5g.sh`
- `meig.sh`
- `simcom.sh`
- qdloader
- mdloader
- quectel-cm

The 2.5 donor expands Meig support further, including 5G-era models such as SRM825N/SRM810-related logic and additional upgrade handling.

Separately, stock R25 2.4.16 ALREADY contains Meig SLM770A support and modem upgrade logic. This is a major reason not to assume LT500D V3 requires a new board image simply because V3 may ship with MeigLink modem SKUs.

---

## 19. CRITICAL NEW OTA CLUE FROM CSP 2.5

This is the highest-priority new finding for the LT500D 3.0 beta hunt.

R25 / CSP 2.4.16 uses:

`json_add_string firmwarevr "${firmwarevr/Beta/}"`

R100 / CSP 2.5.12 uses:

`json_add_string firmwarevr "${firmwarevr/b/}"`

That is an actual source-level behavior change.

Interpretation:

CSP 2.5’s beta train likely uses a lowercase `b` marker style (`2.5.xb`, `2.5.0b`, etc.) rather than the older literal `Beta` normalization convention.

This is SOURCE_VERIFIED for the R100 2.5.12 donor.

It is NOT yet TARGET_VERIFIED as an R25 server-side beta selector.

This clue deserves first-class follow-up because previous R25 beta probes tested literal `Beta` placements, not a carefully isolated CSP 2.5 lowercase-`b` lineage model based on donor source.

---

## 20. OTHER CSP 2.5 OTA CHANGES

Compared to R25 2.4.16, R100 2.5.12 `/sbin/autoupgrade`:

- modernizes TLS cipher list
- changes download temp name from `firmware.bin` to `firmware.img`
- checks for a dedicated `upgrade` MTD partition
- adds stricter curl connect/low-speed limits
- integrates `fwtool` metadata
- runs `meshupgrade` before auto sysupgrade
- retains the same Cudy TEST/PROD API family
- retains the apparent `modulevr` command-substitution bug

Therefore the backend family did not fundamentally change between the R25 2.4.16 and R100 2.5.12 generations.

This strengthens the value of R100 as an OTA protocol donor.

---

## 21. CLOUD CONTROL EVOLUTION

R100 CSP 2.5 `cmsd-control` adds concepts including:

- `protype` header
- `autocloud` header
- `/device/v1/reset`
- hoster tracking
- refined cloud reset/refresh behavior

Do not conflate this with OTA eligibility until evidence links them.

Previous `cmagent deviceid == OTA hardware revision selector` hypothesis was weakened: live R25 `cmagent` operates against local `127.0.0.1:8883`, and the static identity/JWT path fits local Cudy Mesh MQTT authentication better than direct OTA selection.

---

# PART IV — CURRENT HYPOTHESES / EVIDENCE DISCIPLINE

## 22. WHAT IS PROVEN

TARGET_VERIFIED / physically observed:

- R25 TEST endpoint works using temporary test selector path.
- TEST and PROD return separate metadata records.
- four TEST/PROD/CN payload objects for 2.4.16 are byte-identical.
- exact `devtype=R25` matters in tested matrix.
- JSON `firmwarevr` controls update eligibility.
- same semantic 2.4.16 with different timestamps does not create an update.
- modulevr variants tested did not expose modem OTA.
- real target stayed on stock 2.4.16 after probes.

SOURCE_VERIFIED:

- R100 CSP 2.5.12 remains LEDE 17.01.5 / Linux 4.4.140.
- R100 still uses same Cudy OTA endpoint family.
- CSP 2.5 changes beta normalization from literal `Beta` to lowercase `b` removal.
- R100 has real CSP 2.5 features such as Packet Capture and DoH stack.
- R25 2.4.16 already contains SLM770A support.

UNPROVEN:

- an LT500D 3.0 CSP 2.5 beta currently exists on the TEST server.
- the user’s V2 device is excluded by a server-side cohort.
- a specific 2.5.0b version string format for LT500D.
- a private LT500D 3.0 beta URL.
- V2 can safely flash an eventual V3-specific 2.5 build.

---

## 23. CURRENT BEST EXPLANATIONS FOR MISSING LT500D 3.0 2.5

Most plausible possibilities:

1. R25 CSP 2.5 is still under model-specific development/validation and has not been published to public or generic TEST eligibility.
2. A support-only/private beta exists but is not indexed and may require a specific cohort.
3. TEST backend has device-provisioning/allow-list logic not exposed as a request field.
4. The eventual release may introduce additional board/SKU constraints even if it remains R25.

Avoid claiming one is true without new evidence.

---

# PART V — SUCCESSOR PRIORITIES

## 24. FIRST PRIORITY: LOWERCASE-b CSP 2.5 BETA LINEAGE

The next successor should NOT begin with random version strings.

Start from the SOURCE_VERIFIED difference:

R25 2.4.16: remove `Beta`
R100 2.5.12: remove lowercase `b`

Research exact Cudy CSP 2.5 beta naming from official/support/community evidence first.

If a concrete format such as `2.5.0b...` or `2.5.12b...` is evidence-backed, perform a temporary R25 split test where:

- authentic device remains unchanged
- `devtype` remains R25
- raw HTTP `vr` can contain the beta marker
- JSON `firmwarevr` is intentionally controlled/normalized
- real `/etc/rom_version` and bdinfo remain untouched
- metadata only first; do not auto-download/flash until URL/board is inspected

The objective is to test whether a CSP 2.5 beta lineage can select a different R25 catalog entry.

## 25. SECOND PRIORITY: FIND EXACT LT500/LT500D 3.0 ROM_VERSION

Search for exact strings in:

- Cudy support comments
- screenshots
- diagnostic dumps
- forum posts
- firmware filenames
- update metadata captures
- CDN references

An exact `rom_version` is far more valuable than synthetic guessing.

## 26. THIRD PRIORITY: CSP 2.5 DONOR MINING FOR OPENCUDY

Use the extracted R100 rootfs as a donor for architecture/behavior, not as a blind binary transplant.

High-value donor areas:

- Packet Capture
- DoH/https-dns-proxy
- AdShield
- cloud management UI
- autoupgrade improvements
- fwtool/meshupgrade behavior
- newer Meig/5G cellular handling
- newer LuCI registry/menu patterns

Respect R25 hardware differences.

## 27. TARGET SSH POLICY

Do not make the user run commands for tasks that can be done statically in the supplied firmware/rootfs.

Ask for physical SSH only when the remaining question specifically requires:

- live UBUS/runtime state
- server response tied to authentic physical identity
- socket/process behavior
- lifecycle behavior
- hardware state

When asking:

- give one concise runnable block
- heading `SSH terminálba:`
- preserve 4G/SIM
- clean `/tmp` after large downloads
- never write bdinfo
- no reboot unless necessary

---

# PART VI — INCLUDED ARTIFACTS / RECOVERY

## 28. ESSENTIAL INCLUDED ARTIFACTS

The master handoff ZIP includes:

- this complete collector
- a standalone successor prompt
- hot-state summary
- CSP 2.5 R100 firmware full RE ZIP
- R25 stock firmware BIN
- R25 stock extracted rootfs ZIP
- current C27 cumulative installable package
- Developer V4 CLEAN-06 package
- IPTV Hybrid-58 package
- Candidate 47 sysupgrade binary + validation docs
- OTA evidence reports 59-62
- factory/debug lifecycle reports
- IPTV reports
- current beta-hunt checkpoints
- historical project chat/source dumps
- `OPEN CUDY.zip` historical bundle
- SHA256 manifest for the master package contents

The successor should use these files before requesting re-uploads.

---

## 29. USER WORKING STYLE

- Respond in Hungarian unless asked otherwise.
- User prefers progress over lengthy preambles.
- User often says “hajrá”, “mehet”, “folytasd”; continue immediately.
- Do not make the user repeat already-proven tests.
- Produce downloadable checkpoints periodically because long sessions can expire.
- Be precise about verification status.
- When finished with a coherent milestone, package it rather than leaving only chat text.

---

## 30. ONE-SENTENCE CURRENT STATE

We have a physically verified R25 OTA model, a complete extracted CSP 2.5.12 donor proving Cudy still runs LEDE 17.01.5/Linux 4.4.140, and a new source-backed beta clue (`Beta` normalization changed to lowercase `b`) that should drive the next LT500D 3.0 CSP 2.5 beta hunt.

END COLLECTOR
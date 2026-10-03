# RE SUCCESSOR CHAT PROMPT — Cudy LT500D V2 / R25 OpenCudy Engineering Continuation

You are the successor chat continuing an already advanced Cudy LT500D V2 / R25 OpenCudy engineering project. **Do not restart from zero. Do not redo reverse engineering that is already captured in the supplied artifacts.** Your first duty is to preserve the verified baselines, inspect the attached current artifact, and continue from the exact current state.

## 0. LANGUAGE, WORK STYLE, AND NON-NEGOTIABLE RULES

- Answer the user in **Hungarian** unless they explicitly ask otherwise.
- The user expects **actual execution and artifacts**, not generic planning or simulated progress.
- Never claim something is done unless you actually inspected/modified/tested the files and the output physically exists.
- Every newly created project artifact filename **must begin with `RE-`**.
- Never create empty/framework ZIPs. A ZIP/TAR must contain useful, verified content.
- Prefer evidence in this order: exact source/artifact -> static validation -> target/runtime validation -> lifecycle validation.
- Use explicit status language:
  - `SOURCE_VERIFIED`
  - `STATIC_VERIFIED`
  - `TARGET_VERIFIED`
  - `LIFECYCLE_VERIFIED`
  - `UNVERIFIED`
  - `SOURCE_GAP`
  - `TARGET_REQUIRED`
  - `UNKNOWN`
- Core engineering discipline: **evidence -> exact conclusion -> risk -> only then modification**.
- Never infer target behavior only from screenshots or source presence.
- Never silently convert a route/source residue into a claimed functional feature.
- Do not repeatedly ask the user to probe the router for facts that can be established statically from the supplied firmware/source/artifacts.
- If a physical-router check is truly required, batch it into **one comprehensive prompt/script whenever possible**. The user explicitly prefers max ~1 target prompt rather than many small manual probes.
- Router commands must be introduced exactly with the label: **`SSH terminálba:`**
- Target shell is BusyBox/ash. Keep commands BusyBox-compatible.
- The router **does not have the `install` utility**. Use `mkdir`, `cp`, `chmod`, `rm`.
- WinSCP proven transport is **SCP**, not SFTP.
- Do not use ChatGPT Work/Workspace handoff. Continue in this project/chat context.
- Do not modify unrelated working subsystems while working on Developer/hidden features.

## 1. CURRENT PRIMARY ARTIFACT — START HERE

The user attached the current latest Developer artifact:

`RE-LT500V2-R25-ENG08-DEVELOPER-V3-ENGINEERING-FULL-01(1).zip`

The uploaded ZIP has been integrity-checked in the previous chat:

`SHA-256 = cb47bc80aac3a2b4420722de064187b572b17776773788f412cbe4feef5468fd`

ZIP integrity test: **PASS, no compressed-data errors**.

Inside it, the root directory is:

`RE-LT500V2-R25-ENG08-DEVELOPER-V3-ENGINEERING-FULL-01/`

Before changing anything, inspect these files in this order:

1. `RE-README.md`
2. `RE-STATUS.md`
3. `RE-SUCCESSOR-CHAT-PROMPT.md`
4. `RE-DEVELOPER-V3-FEATURE-MATRIX.md`
5. `RE-DONOR-FEATURE-DISCOVERY.md`
6. `RE-DONOR-HIDDEN-FEATURES-RE.csv`
7. `RE-NATIVE-FEATURE-CATALOG.json`
8. `RE-ARCHITECTURE.md`
9. `RE-SECURITY-BOUNDARY.md`
10. `RE-UNRESOLVED.md`
11. `RE-FINAL-HOST-AUDIT.txt`
12. `RE-MANIFEST.csv`
13. `RE-SHA256SUMS.txt`
14. `RE-INSTALL-DEVELOPER-V3-FULL-01.sh`
15. `RE-VERIFY-DEVELOPER-V3-FULL-01.sh`
16. `RE-RUN-DEVELOPER-V3-SELFTEST-01.sh`
17. `RE-ONE-SHOT-TARGET-V3.sh`
18. production payload:
    - `RE-rootfs/usr/lib/lua/luci/controller/RE-re_developer.lua`
    - `RE-rootfs/usr/lib/lua/luci/view/system/RE-developer.htm`

Do not reconstruct these from memory; use the attached ZIP as the current source of truth.

## 2. VERIFIED HARDWARE / FIRMWARE BASELINE

Device:

- Cudy LT500D V2 / R25
- SoC: MediaTek MT7628AN
- CPU: MIPS 24KEc, ~580 MHz stock donor evidence
- RAM: 128 MiB DDR2
- SPI NOR: 16 MiB
- 2.4 GHz: MT7628 integrated radio
- 5 GHz: MT7663/MT7613-family PCIe radio
- modem on physical target: Quectel EC200A-family
- stock board identity: R25
- stock LEDE generation: LEDE 17.01.5 / Cudy firmware family

Current stock ROM identity used by the engineering line:

`2.4.16-20250804-150319`

Current physical target probe previously confirmed:

- model: `LT500D V2.0`
- board: `R25`
- `/overlay` on `/dev/mtdblock9`, JFFS2, persistent
- `ubus`, `ip`, `ifconfig`, `route`, `logread`, `dmesg`, `ps`, `sha256sum`, `opkg`, `quectel-cm` present

MTD truth from the engineering target:

- mtd0 `u-boot`
- mtd1 `u-boot-env`
- mtd2 `factory`
- mtd3 `debug`
- mtd4 `backup`
- mtd5 `bdinfo`
- mtd6 `firmware`
- mtd7 `kernel`
- mtd8 `rootfs`
- mtd9 `rootfs_data`

Never hardcode `rootfs_data` size/geography across firmware versions. Runtime `/proc/mtd`, mounts and `df` are authoritative.

## 3. FROZEN REGRESSION BASELINES — DO NOT DISTURB

### ENG08 4G baseline

The working 4G regression baseline is:

`RE-LT500V2-R25-ENG08-4G-R25-FIX-02-sysupgrade.bin`

SHA-256:

`d03b44931a73f020dfb42e3a43c8fd80b4d5f2d28d5c474caa16fa32000c91ad`

This build is physically installed/validated as the working 4G baseline. Do not alter the 4G stack casually.

Important 4G pieces include:

- `gcom`
- `mcore`
- `cmagent`
- `pingcheck`
- `/usr/lib/4g/*`
- `quectel-cm`
- USB/netifd interface handling

Do **not** blindly remove `cmagent`, `cmsd` or Mosquitto; previous donor analysis found real dependencies.

### H09 OPKG backend

H09 is the frozen, target/lifecycle-verified OPKG backend baseline.

Status:

- `SOURCE_VERIFIED`
- `STATIC_VERIFIED`
- `TARGET_VERIFIED`
- `LIFECYCLE_VERIFIED`

The full isolated package lifecycle selftest passed: install -> list-upgradable -> HOLD -> release HOLD -> named upgrade -> remove -> cleanup/restoration.

Six core upgrades remain intentionally locked and must never be globally upgraded blindly:

- rpcd
- uclient-fetch
- libuclient
- libubox
- luci-base
- libblobmsg-json

Do not rewrite the H09 backend unless there is concrete regression evidence.

### H11 branding/theme base

H11-02 installed successfully and runtime verifier passed. It established branding/theme/developer ownership, but **visual branding consistency still has known misses**:

- Dashboard System card can show `2.4.16 DE`
- System Status firmware row can still show raw `2.4.16-20250804-150319`
- General -> Firmware / Online Update can still show raw ROM identity
- footer already shows `2.4.16 - OpenCudy`

These are separate branding issues, not reasons to rewrite Developer V3.

### Developer V2 READONLY-02

This is the frozen verified read-only Developer baseline beneath V3.

Previous target results:

- target probe: PASS
- install/verifier: PASS
- non-mutating command selftest: PASS

The selftest explicitly proved:

- all fixed read-only command families executed
- network/wireless/firewall/ROM/OPKG state hashes unchanged
- watched service/process state unchanged

Therefore V2-02 is a `TARGET_VERIFIED` baseline.

## 4. CURRENT DEVELOPER V3 ARCHITECTURE

Current artifact name:

`RE-LT500V2-R25-ENG08-DEVELOPER-V3-ENGINEERING-FULL-01`

V3 is intentionally a small ownership delta. Production ownership remains exactly two LuCI files:

- `/usr/lib/lua/luci/controller/re_developer.lua`
- `/usr/lib/lua/luci/view/system/developer.htm`

The package payload files are stored under `RE-rootfs/...` with `RE-` prefixed artifact names, but install scripts place them into the real runtime names/paths.

V3 does NOT own or replace:

- H09 OPKG backend
- H11 theme owner
- H11 branding owner
- network config owner
- wireless config owner
- firewall owner
- cellular/4G owner
- kernel
- DTB
- bootloader
- firmware image

Native hidden/conditional features are launched through the **original Cudy route/controller/CBI backend**, not cloned or reimplemented.

Server-side request model:

- fixed Developer toggle
- allowlisted SSH actions
- allowlisted Telnet lifecycle actions
- existing engineering terminal action
- fixed-key read-only `report` endpoint
- fixed system/kernel log source endpoint
- fixed catalog endpoint
- fixed support-safe snapshot endpoint

The browser/native launcher may open only entries compiled into the fixed catalog and must reject blocked/source-absent entries.

No arbitrary privileged server endpoint may accept:

- arbitrary shell
- arbitrary path
- arbitrary service name
- arbitrary ubus object
- arbitrary native route
- arbitrary AT command
- arbitrary GPIO
- arbitrary MTD operation

## 5. DEVELOPER V3 CORE FEATURE SET

V3 currently defines **24 core engineering features**:

1. Terminal — CONTROLLED WRITE
2. Sandbox / Telnet — CONTROLLED WRITE
3. SSH Access — CONTROLLED WRITE
4. Board & Firmware Identity — READ ONLY
5. Kernel & Uptime — READ ONLY
6. Memory & Load — READ ONLY
7. Overlay & Filesystems — READ ONLY
8. MTD Inventory — READ ONLY
9. Interfaces — READ ONLY
10. Routes — READ ONLY
11. Cellular — READ ONLY
12. USB / Modem — READ ONLY
13. Service Matrix — READ ONLY
14. OPKG State — READ ONLY
15. Cudy Framework — READ ONLY
16. Wireless Runtime — READ ONLY
17. Kernel Modules — READ ONLY
18. Listeners — READ ONLY
19. Boot / Cron — READ ONLY
20. Overlay Changes — READ ONLY
21. VPN Runtime — READ ONLY
22. Hidden Feature Lab — NATIVE ROUTE GATE
23. System Log + Kernel Log — READ ONLY
24. Engineering Snapshot — READ ONLY EXPORT

Important user decision:

- **System Log MUST remain a Developer tile.**
- **Kernel Log MUST remain a Developer tile.**

Do not remove them merely because Cudy also exposes a normal log route elsewhere.

## 6. NATIVE HIDDEN / CONDITIONAL FEATURE CATALOG

The attached V3 catalog contains **54 entries** derived from exact stock R25 `2.4.16-20250804-150319` source/rootfs.

Current source-presence summary:

- 54 catalog entries total
- 53 referenced source paths present
- 1 source path absent: SNMP exact CBI model

Do not equate `source present` with `target functional`.

Major catalog groups/candidates already discovered include:

### Diagnostics

- Native Diagnosis
- Diagnosis: Cellular
- Diagnosis: WAN
- Diagnosis: Wireless
- Diagnosis: Devices
- Diagnosis: Services
- Diagnosis: System

### Wireless hidden/conditional

- Wireless Chart
- Wireless Probe List
- Wireless Log
- MLO Config
- MAC Repeater
- WPS

Historical correction: Wireless Chart / Probe List / Wireless Log are genuine Cudy hidden/detail routes. They can be exposed through the engineering/native lab, but do not relabel them as invented OpenCudy backend features.

MLO source exists, but LT500 hardware is not Wi-Fi 7. Treat as likely framework residue/unsupported until target evidence proves otherwise.

### Network hidden/conditional

- Port Mirroring
- Legacy QoS
- HNAT/QoS
- MQoS
- Port Config
- Remote Web
- SNMP descriptor residue
- DTU
- Hostname
- Custom DNS
- TTL
- DMZ
- ALG
- Speed Test
- PoE Passthrough

Hardware/package-specific entries must stay capability-gated.

### Services

- USB Sharing / Samba
- Printing Server / p910nd
- Watchcat

### System / hidden maintenance

- LED Control
- Button Control
- LED & Button
- Toggle Button
- Cudy Sandbox / Telnet
- Cudy Native Terminal
- Cudy Kernel Log Page

Stock firmware also contains an internal `hcshd`; classify it **INTERNAL**, not a generic Developer API. Do not expose a raw hcshd command runner.

### VPN source-present protocol pages

- PPTP Client
- PPTP Server
- L2TP Client
- L2TP Server
- OpenVPN Client
- OpenVPN Server
- WireGuard Client
- WireGuard Server
- ZeroTier Slave
- ZeroTier Master
- IPSec Client
- IPSec Server
- IPSec Site-to-Site

The source pages may exist while modules/runtime capability differ. Target-test exact behavior before declaring functional.

### Cellular/security-sensitive catalog entries

These are cataloged for provenance but intentionally **blocked**:

- AT Command
- Modem Reset

Do not activate them automatically.

### Permanently excluded

- TR-069 / CWMP

It may stay cataloged as provenance only, but must remain blocked and absent from normal functionality.

## 7. NORMAL FEATURES THAT MUST NOT BE RECLASSIFIED

### IPTV/VLAN

The user explicitly reminded us that IPTV/VLAN already exists in this firmware line and the emulator also confirms it as a normal LT500 Advanced feature.

Keep it:

`Advanced -> IPTV/VLAN`

Do not duplicate it as Developer functionality.

### OPKG

Keep it:

`Advanced -> System -> Package Manager`

Do not move it into Developer.

### VPN

VPN remains a normal General/Advanced functional domain where exposed. Developer may provide diagnostics/native launchers but should not steal ownership from normal VPN pages.

## 8. STOCK DONOR / EMULATOR EVIDENCE ALREADY DISCOVERED

An LT500 emulator log was inspected. Important caveat: it represented an older LT500/R25 firmware (`2.1.1-20240419-090237`), so use it as version-specific/cross-version corroboration, not automatically as exact 2.4.16 target truth.

It nevertheless confirmed major platform facts:

- Linux 4.4.140 generation
- MT7628AN
- R25 machine
- 128 MiB RAM
- 16 MiB SPI NOR
- MT7663-family 5 GHz PCIe
- 2.4 GHz MT7628 radio
- JFFS2 overlay architecture
- Quectel EC200A-family modem behavior
- ttyUSB interfaces
- `gcom`/`4gup` orchestration
- VPN kernel/userspace stacks
- wireless hidden/relay interfaces
- normal Cudy Diagnostic Tools structure

Use exact stock 2.4.16 rootfs/source in the attached project artifacts as the stronger evidence when available.

## 9. STOCK CUDY FEATURE REGISTRY DISCOVERY

V3 documented the Cudy registry architecture:

- `/usr/lib/lua/luci/description.lua` = broad descriptor pool
- `luci/gui.lua` = selects normal GUI set and contains explicit hidden child routes
- descriptor/source presence != visible normal GUI feature

Known exact hashes from the inspected stock 2.4.16 rootfs:

- `description.lua`: `db0727db89e7fa0c6f9a4bd286a7f48bbe0dadf1add13e59b9f81397f946ad3f`
- `gui.lua`: `113ddbaa2b6c7edb4ae2b540f0bbbf268a79bfd9799078ebbbe6078969e1ef2b`
- `forbidden.lua`: `36e2e82f86fdae5cc06b4eb0fb34d201438617f5de53df973cff699b2b9afcbe`

Explicit hidden child routes found in `gui.lua`:

- `admin/network/wireless/chart`
- `admin/network/wireless/probelist`
- `admin/network/wireless/logread`
- `admin/system/status/dmesg`
- `admin/system/terminal`

`forbidden.lua` also names `admin/system/terminal`, corroborating that it is a real hidden/special Cudy route.

Factory/developer markers:

- `/etc/rom_develop`
- `bdinfo factory`
- `/etc/rom_dbg` references in stock libraries
- stock `testonly.js` adds a Test Only watermark; it does not by itself unlock routes

Stock Dropbear/Telnet/password scripts had `bdinfo dbg` gating. ENG08 already altered the engineering-access behavior; do not patch those files again as part of ordinary Developer V3 work.

## 10. CURRENT V3 HOST-VALIDATED STATUS

From the attached `RE-FINAL-HOST-AUDIT.txt`:

- exact stock R25 Cudy 2.4.16 source/rootfs evidence used
- 54 source-derived catalog entries
- 53/54 source paths present
- System Log and Kernel Log retained
- IPTV/VLAN remains Advanced
- TR-069/CWMP blocked
- raw AT blocked
- modem reset blocked
- production payload delta exactly controller + Developer view
- H09/H11 ownership gates retained

Host tests previously passed:

- Python static gates: PASS
- Lua controller syntax: PASS
- browser JavaScript syntax: PASS
- shell syntax: PASS
- fixed report allowlist: PASS
- invalid-scope fail-closed: PASS
- source-presence classification: PASS
- security static gates: PASS

Important: according to the artifact itself, **V3 physical-router runtime is still UNVERIFIED until the one-shot target gate is run and returns PASS**. Do not silently upgrade this status unless the user provides target output proving it.

## 11. CURRENT V3 FILE HASHES — USE FOR REGRESSION

Important production payload hashes in the attached artifact:

- V3 controller artifact:
  `b25c4b0925750792425c555f81725d897ac080bfe37dd878eba0e0cd32fb515a`
- V3 Developer view artifact:
  `b5581ca7b42330b684e6fa5d8e53017010c7149a879e058edf432da65d5d8a3e`

One-shot script hash:

`6247ac7e7b9f01276e57b035ed4d63c17adcd4e1e54a5295eddaf0a9ca8d6006`

Installer hash:

`29c400f688f2c609f77f62b388d0103d35e1af0485023547604a4c5287af5095`

Verifier hash:

`6069b4ee8c912732253f41e783d3d3f5ec2ae1b2e3d8a54e9652bf9c105c5eba`

Selftest hash:

`4be6893682b49bcfe80ae85ad9a26215b493273f4534c7130dac43cb72670cdc`

Use the full `RE-SHA256SUMS.txt` in the archive for complete integrity verification.

## 12. IMMEDIATE NEXT ACTION — DO THIS, DO NOT PLAN AROUND IT

The user’s active goal is:

**find additional Developer / hidden / non-activated features, implement everything reasonably possible, make the current build genuinely functional, test it yourself as far as possible, and minimize physical-router interaction to at most one consolidated prompt where target evidence is required.**

Start with these steps:

### STEP A — Inspect the attached V3 artifact deeply

Do not assume the existing V3 implementation is flawless. Audit the actual Lua controller, Developer template, installer, verifier, selftest, catalog and documentation.

Check:

- Lua semantics under old LEDE/LuCI module environment
- use of uncaptured globals after `module(...)`
- BusyBox compatibility
- all native routes against stock controllers/models
- CSRF/POST protection for write actions
- output size caps
- HTML escaping
- JS route allowlist behavior
- modal/open-native behavior
- error handling when CBI route returns 403/404/500/nil Lua exception
- source-present but hardware-absent behavior
- unknown/missing command behavior
- memory/CPU cost on MT7628
- duplicate request handlers/events
- long-output rendering and scrolling
- Dark/Light theme compatibility
- exact ownership regression against H09/H11/4G

### STEP B — Expand hidden/non-activated feature discovery from exact 2.4.16 stock source

Search beyond the existing 54 entries through:

- `description.lua`
- `gui.lua`
- all LuCI controllers
- all `model/cbi` files
- helpers/modules
- init scripts
- `/usr/sbin`, `/usr/bin`, `/bin`, `/sbin`
- strings in relevant proprietary binaries
- UCI defaults/config files
- service scripts
- hidden routes referenced by JS/templates
- `bdinfo`/factory/debug conditions
- `rom_develop`/`rom_dbg`
- feature resolver conditions (`mode`, `uci`, `oruci`, `oruci2`, `iface`)

For every newly discovered candidate, record:

- stable ID
- title
- group
- route
- source path
- backend/controller/model
- classification
- risk
- required capability
- runtime dependency
- normal vs Advanced vs Developer vs Internal vs blocked placement
- source verification status
- target verification status
- whether it can safely be opened in native Cudy modal

Do not duplicate a normal feature into Developer unless there is an explicit engineering reason.

### STEP C — Implement safe candidates

Prefer reusing the original Cudy route/backend if source exists.

For source-present candidates:

- read-only native pages -> can generally be exposed through the native lab after safety review
- configuration pages -> can be exposed if they already have native validation/Apply semantics and do not violate project ownership; clearly label them as native configuration pages
- hardware-specific pages -> capability-gate or show Unsupported/Unavailable
- missing backend/package -> do not fake it; show Source present / Runtime unavailable
- destructive/internal pages -> keep blocked unless explicitly approved

Do not build fake backends or fake data just to make a tile green.

### STEP D — Self-test as much as possible without router

Run host/static tests on every modification:

- shell `sh -n`
- Lua syntax parser/compiler available in environment
- JS syntax extraction + `node --check`
- ZIP/TAR integrity
- SHA-256 manifest verification
- route/source-path cross-reference
- policy-blocked route regression
- H09/H11 ownership regression
- only expected production files changed
- no forbidden commands or broad UCI dump introduced

Where feasible, create mock/stub tests for:

- report scopes
- invalid scope
- catalog JSON
- route allowlist
- blocked route behavior
- source-present/source-absent capability state
- output truncation
- HTML escaping
- snapshot redaction
- service/process parsing

### STEP E — At most one physical-router prompt

If target evidence is required, create one comprehensive one-shot target script that:

1. performs read-only preflight
2. verifies LT500D/R25 identity
3. verifies expected V2/V3 baseline hashes
4. creates rollback backup
5. installs guarded delta
6. clears only necessary LuCI caches
7. runs Lua syntax/runtime loading checks
8. verifies exact installed hashes
9. exercises every new fixed read-only report scope
10. performs non-mutating before/after hash checks of:
   - network
   - wireless
   - firewall
   - ROM metadata
   - OPKG database/state
11. checks 4G/service process state before/after
12. probes native route resolution safely where possible without saving/applying
13. reports each route as one of:
   - TARGET_OK
   - SOURCE_PRESENT_ROUTE_MISSING
   - CAPABILITY_ABSENT
   - BACKEND_ERROR
   - POLICY_BLOCKED
   - UNKNOWN
14. never reboots/sysupgrades unless user explicitly requests it
15. ends with one unambiguous PASS/FAIL line

The user wants as little manual target work as possible. Do not split this into 20 commands unless absolutely necessary.

## 13. FEATURES THAT MUST REMAIN BLOCKED / EXCLUDED

Unless the user explicitly changes policy:

- TR-069 / CWMP: permanently excluded
- raw arbitrary AT console: blocked
- destructive modem reset launcher: blocked
- raw MTD write/erase: blocked
- arbitrary GPIO write: blocked
- arbitrary UCI write API: blocked
- arbitrary service-name action API: blocked
- arbitrary ubus object API: blocked
- raw hcshd command channel: blocked
- firmware write/sysupgrade from Developer lab: blocked

Existing controlled Terminal/SSH/Telnet are already deliberate engineering features. Do not broaden them into a generic unaudited privileged execution API.

## 14. ENGINEERING SNAPSHOT PRIVACY / REDACTION

The support-safe Engineering Snapshot must not simply dump all of `uci show` or raw secrets.

Continue to protect/redact where possible:

- Wi-Fi passwords
- credentials
- tokens
- private keys
- IMEI/IMSI/ICCID when exported for support
- device/client MACs as appropriate for support-safe export
- public/private IPs where necessary

Raw System Log and Kernel Log may remain separate Developer diagnostic views by project decision, but the support-safe snapshot should be more conservative.

## 15. UI / FIDELITY REQUIREMENTS

Developer UI should remain Cudy-native, not a nested complete LuCI shell embedded awkwardly in another page.

Keep:

- Cudy modal semantics where available
- clear category structure
- source/risk/status badges
- readable Dark and Light theme
- long text in scrollable monospace containers
- Loading / Unavailable / Unsupported / Error states
- no fake success state
- no fake demo data

When a native Cudy route fails, show exact classification and error context rather than pretending the feature works.

System Log and Kernel Log must stay accessible as Developer tiles.

## 16. KNOWN OPEN ISSUES SEPARATE FROM DEVELOPER V3

Do not lose these, but do not let them derail the hidden-feature branch unless the user asks:

- H11 branding consistency:
  - Dashboard System card
  - System Status firmware row
  - General/Firmware Online Update identity
- H10 package UI visual branch exists separately
- future package compatibility policy still distinguishes SAFE / REVIEW REQUIRED / BLOCKED
- kernel/core/kmod package upgrades remain high-risk

## 17. BUILD / CHECKPOINT POLICY

The user previously suffered workspace/session resets. Therefore:

- after each significant feature block, create a real downloadable checkpoint
- before risky refactors, create a checkpoint
- include SHA-256 and changelog
- verify final ZIP/TAR by extracting again
- include a manifest and status file
- do not leave many hours of work only in scratch state

All new artifact names must start with `RE-`.

Suggested next version naming if V3 needs modifications:

- `RE-LT500V2-R25-ENG08-DEVELOPER-V3-ENGINEERING-FULL-02`

Do not call it `TARGET_VERIFIED` until physical target evidence exists.

## 18. REQUIRED FINAL DOCUMENTATION FOR THE SUCCESSOR'S NEXT MAJOR CHECKPOINT

When the next major Developer/hidden-feature build is complete, include at minimum:

- `RE-README.md`
- `RE-STATUS.md`
- `RE-CHANGELOG.md`
- `RE-ARCHITECTURE.md`
- `RE-SECURITY-BOUNDARY.md`
- `RE-DEVELOPER-FEATURE-MATRIX.md`
- `RE-DONOR-FEATURE-DISCOVERY.md`
- `RE-DONOR-HIDDEN-FEATURES-RE.csv`
- `RE-NATIVE-FEATURE-CATALOG.json`
- `RE-UNRESOLVED.md`
- `RE-TARGET-CHECKLIST.md`
- `RE-FINAL-HOST-AUDIT.txt`
- `RE-MANIFEST.csv`
- `RE-SHA256SUMS.txt`
- installer
- verifier
- selftest
- rollback
- one-shot target script
- **updated successor-chat prompt** for the next chat

Documentation must clearly separate:

- donor/source fact
- implementation fact
- target fact
- assumption
- unresolved item

## 19. SUCCESS CONDITION

The Developer/hidden-feature branch is not “done” merely because many tiles exist.

A candidate is complete only when its state is correctly classified and handled:

- native normal feature -> remains normal
- native Advanced feature -> remains Advanced
- safe hidden Developer feature -> exposed with correct route/backend
- hardware conditional -> capability-gated
- source residue -> documented, not faked
- internal-only -> documented, not automatically exposed
- blocked/destructive -> remains blocked

A V3/V4-style build is complete only when:

- source audit is complete for that checkpoint
- static tests pass
- package integrity passes
- ownership regressions pass
- one-shot target test is available
- if target output exists, every failed native route is classified from exact evidence
- no 4G/H09/H11 regression is introduced
- documentation and successor prompt are included

## 20. WHAT TO SAY TO THE USER FIRST

Do not greet them with a long recap. Start with a concise confirmation such as:

> Megvan az előd teljes állapota és a csatolt `RE-LT500V2-R25-ENG08-DEVELOPER-V3-ENGINEERING-FULL-01` build. Nem kezdem újra nulláról. Először a ZIP tényleges tartalmát és a V3 production controller/view-t auditálom, utána innen folytatom a további hidden/nem aktivált funkciók feltárását és csak konkrét evidence alapján készítek V3-02 deltát. A H09 OPKG-hoz, ENG08 4G-hez és működő H11/V2 részekhez nem nyúlok.

Then actually perform that audit. Do not stop at planning.
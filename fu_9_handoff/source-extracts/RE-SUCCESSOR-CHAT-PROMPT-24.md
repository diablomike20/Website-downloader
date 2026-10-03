# RE-SUCCESSOR-CHAT-PROMPT-24

You are the next engineering session for **Cudy LT500D V2 / R25 — OpenCudy**.

Continue from this checkpoint. **Do not restart reverse engineering from zero.**

## User style / working protocol
- Answer in Hungarian.
- Prefer concrete engineering work over explanation.
- “mehet / hajrá / csináld / folytasd” means proceed.
- All generated project artifacts must start with `RE-`.
- Router command heading must be exactly `SSH terminálba:`.
- Target shell is BusyBox/ash; use mkdir/cp/chmod/rm rather than assuming GNU `install`.
- WinSCP SCP works.
- Never claim target verification without physical-router evidence.
- Status words: SOURCE_VERIFIED, STATIC_VERIFIED, TARGET_VERIFIED, LIFECYCLE_VERIFIED, WEB_VERIFIED, UNVERIFIED, TARGET_REQUIRED, TARGET_OBSERVED.

## Absolute engineering rule
> A stock Cudy ezt hogyan csinálja, és tényleg muszáj-e eltérni tőle?

> Minden normál hardver- és szolgáltatásfunkció stock Cudy truthból indul.

> Eltérés csak akkor marad, ha az unlockhoz bizonyíthatóan kell.

Stock truth for R25 is factory SquashFS + stock firstboot/uci-defaults materialization + normal runtime semantics. Do not blindly overwrite runtime `/etc/config/*`.

## Tamper vs retry
Keep separate:
- tamper/integrity investigation
- broken-service retry/restart investigation
Never recreate the earlier invented “tamper retry loop” framing.

## Current physical target — known good baseline
Model: LT500D V2.0
ROM: R25
LEDE: 17.01.5 / Cudy 2.4.16
Kernel: 4.4.140

bdinfo:
- md5 OK
- check OK
- checkuuid OK
- dbg FAIL in normal OpenCudy mode

Cumulative-17 physical verification:
- cellular exact stock/live-stock hashes PASS
- Dropbear running
- Telnet running/listening TCP 23
- hcshd running/listening UDP 56791
- watchdog procd owned, timeout 30s, feed 5s
- 4G up on usb0, lease/default route/DNS, modem lifecycle online
- FILE_PARITY=PASS

Performance:
- user reports it is now better
- ~4-hour target capture showed no persistent gcom/4G/watchdog/network restart loop
- performance work is now acceptance/regression monitoring, not primary RE.

## Minimal deltas
KEEP:
- Dropbear startup debug-gate bypass — UNLOCK_REQUIRED
- Telnet startup debug-gate bypass — UNLOCK_REQUIRED
- stable engineering root access — UNLOCK_REQUIRED
- installed sysupgrade unlock — UNLOCK_REQUIRED
- scheduled vendor OTA suppression — UNLOCK_PERSISTENCE
- CWMP/TR-069 disabled — explicit project exception

RESTORE/PRESERVE STOCK:
- hcshd startup
- cellular/antenna stack
- normal hardware/services unless proven otherwise

Do not globally set `bdinfo dbg=OK`.

## Core hashes
dropbear unlocked:
75a2dc540978e2712d32bd4e1d354e67cb5cf401d12981591915a1832871f2f8

telnet unlocked:
215dfc5b3fc694262dacd44610c61fc52df5217b6e062e7d59e2aa803c655622

cron OTA policy:
9ee0c111e3a4ec84283422adf196322ff486a830d3e55522df75d5905fbeaaaa

cwmp policy:
18b39a7c5308dd54d4ab27548c27fdf8040f6d6426ba8a72a1b1ac393c9e21dd

stock hcsh:
a0ddeb83b539607bef93f34d41dfa6fcc7731c68334f018a3ead43aac0e20288

4gup stock-live:
f13536e75e2fbdb24d87c34bddb579fec538bf651238e7bc60ce15fce2194c32

platform.sh baked unlock:
1de73bc54df6117c0f24d5160a65086d50f37cc0cb9179f033ae83b928421369

11_fix_passwd baked unlock foundation:
1919f23eca40d763b4669def734158b077d5a2426b9d0ce0379d48dd6694cc75

99_00_console baked unlock foundation:
1cafdb6d084f2e62c89814adbf325665151c05553e7297c4eb54512e1d5fb757

## OPKG
Exact `/bin/opkg` SHA:
48332ad1dcbeb3bcdc3ceac968b85eef57cab0476bb77f21cb48b8d8d0c93cdf

Version:
9f61f7acf3845d2e09675b49fec5d783d57eb780 (2017-12-08)

Current package inventory: 127 records, including 86 reconstructed stock-ROM kmods.

## Developer UI direction
V3 duplicated normal UI too much.
Developer V4 CLEAN:
- ordinary Network/Wireless/VPN/etc. not duplicated
- Source/RE Catalog collapsed/evidence-only
- genuine Developer content only
- System Log + Kernel Log remain
- Cudy Factory Debug is a distinct high-risk maintenance feature
- OpenCudy SSH/Telnet unlock remains separate.

## Cudy Factory Debug RE — important
Exact physical-target `/usr/lib/libbdinfo.so` SHA:
dc2ac9f10739eb1f690acf3fbd9e17d8f824673f7faa7173db3894faa4cfc15b

SOURCE_VERIFIED `bdinfo_check_dbg()`:
- fread raw `/proc/sys/dev/flash_uuid` (newline retained)
- hmac
- `%s%s@2025`
- SHA256
- lowercase `%02x`
- exactly 64-byte `/etc/rom_dbg`
- strcmp validation

Decision gate:
- current `/etc/rom_release` present causes retail failure before token acceptance
- maintenance path requires `/etc/rom_release` absent
- public Cudy runtime evidence independently showed hcshd removing `/etc/rom_release`.

Developer V4 CLEAN-03 implements:
- backup marker state
- remove release marker
- generate exact token
- write 64 bytes, no newline
- verify `bdinfo dbg=OK`
- rollback on failure
- Disable restores prior state.

**This enable/disable action is STATIC_VERIFIED / TARGET_REQUIRED.**
Installation does NOT toggle it.

## Main build artifact
`RE-LT500V2-R25-OPENCUDY-CUMULATIVE-24-TARGET-INSTALLABLE.tar.gz`

This is the current installable cumulative target build. It is deliberately not a new flash `.bin`.

It contains:
- current minimal unlock/persistence service files
- stock/live-stock cellular and hcsh
- exact historical OPKG + FINAL-11 UI/backend + 127-record fallback DB
- stock Cudy app bind path
- Developer V4 CLEAN-03
- full docs
- verifier + rollback
- no-reboot installer

The preflight requires the known ENG07 foundation in `/rom`; it does not invent/rewrite password/console/sysupgrade foundation files.

## Immediate next steps
1. Have the user run Cumulative-24 preflight/install/verify. **No reboot.**
2. Review verifier output carefully before changing anything.
3. Then target-test Developer V4 Cudy Factory Debug:
   - enable once
   - verify `bdinfo dbg=OK`, release absent, rom_dbg present
   - do not reboot
   - disable
   - verify `bdinfo dbg=FAIL`, retail release marker restored, rom_dbg removed/restored as appropriate
   - confirm SSH/Telnet still work
4. Only after that mark the feature TARGET_VERIFIED.
5. Do not chase `bdinfo_check_uuid()` further unless it blocks a real goal.
6. The next reboot should be reserved for a meaningful image-level milestone.

## Future full flash `.bin`
Do NOT in-place patch compressed SquashFS.
The previous ENG06 attempt boot-failed.

When making a real full flash build:
- reproduce SquashFS v4
- XZ
- 512 KiB block size
- bake the physically proven live-good files, not stale engineering `/rom`
- preserve kernel prefix and rootfs_data/JFFS2 geometry
- validate all offsets/sizes/hashes offline
- preserve U-Boot recovery RSA
- flash only after explicit physical-test gate.

Read first:
- `RE-OPENCUDY-LT500D-R25-FULL-DOCUMENTATION-24.md`
- `RE-LT500V2-R25-TARGET-DELTA-AUDIT-20.md`
- `RE-LT500V2-R25-BDINFO-CHECKDBG-STATIC-RE-22.md`
- `RE-LT500V2-R25-BDINFO-DBG-DECISION-TREE-RE-23.md`
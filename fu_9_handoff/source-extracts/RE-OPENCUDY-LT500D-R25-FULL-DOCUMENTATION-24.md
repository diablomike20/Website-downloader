# OpenCudy — Cudy LT500D V2 / R25 — Full Engineering Documentation 24
# Teljes mérnöki dokumentáció / Full engineering documentation

**Build:** `RE-LT500V2-R25-OPENCUDY-CUMULATIVE-24-TARGET-INSTALLABLE`  
**Date:** 2026-09-25  
**Target:** Cudy LT500D V2.0 / R25  
**Base:** Cudy LEDE 17.01.5 / 2.4.16, kernel 4.4.140

---

## 1. Vezetői állapot / Executive state

A projekt jelenlegi fizikailag igazolt állapota stabilabb, mint a korábbi engineering állapot. A router teljesítménye a felhasználó megfigyelése szerint javult, és a többórás target capture nem mutat tartós `gcom`, 4G, watchdog vagy network restart loopot.

A mostani 24-es kiadás **telepíthető kumulatív target build**, nem új flash `.bin`. Szándékosan az aktív JFFS2 overlayre telepít, mert:
- a jelenlegi jó állapot fizikailag igazolt;
- az aktuális `/rom` még korábbi engineering eltéréseket tartalmaz;
- az ENG06 in-place SquashFS módosítás korábban boot failure-t okozott;
- új flash image csak reprodukálható XZ SquashFS rebuild + teljes offline validáció után készülhet.

**Cumulative-24 telepítéséhez nem kell reboot.**

---

## 2. Kötelező első elv / Mandatory first principle

> **A stock Cudy ezt hogyan csinálja, és tényleg muszáj-e eltérni tőle?**

> **Minden normál hardver- és szolgáltatásfunkció stock Cudy truthból indul.**

> **Eltérés csak akkor marad, ha az unlockhoz bizonyíthatóan kell.**

A stock truth R25-nél nem mindig a nyers SquashFS byte-állapot. Az `/etc/uci-defaults/*`, különösen `99_oem`, több fájlt szándékosan materializál első bootkor. Ezért az autoritatív baseline:

`factory SquashFS + stock uci-defaults materialization + normal runtime configuration`.

---

## 3. Firmware provenance

### Stock Cudy full image
- file: `LT500V2-R25-2.4.16-20250804-150319-flash.bin`
- size: 12,124,315 bytes
- SHA-256: `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

### Cudy-issued OpenWrt
- file: `openwrt-ramips-mt76x8-cudy_lt500-v2-squashfs-flash.bin`
- size: 9,306,901 bytes
- SHA-256: `3d8bb8eac7396f8263e90ecf14eca0f324ea6dbb295106e72b0a96753f31255b`

### ENG07 physical candidate
- file: `RE-LT500V2-R25-ENG07-PHYSICAL-CANDIDATE-01.bin`
- size: 11,796,635 bytes
- SHA-256: `67b7a5ef5ea3d0bebb5959d3ae7056d239323dd7fbfb7b939c60a6e5c16b1b52`

Historical successful provisioning chain:

`stock Cudy -> Cudy-issued OpenWrt -> unlocked original Cudy`.

---

## 4. Flash layout / boot safety

Full stock image:
- U-Boot: `0x00000-0x2ffff`
- RSA signature: `0x30000-0x300ff`
- padding: `0x30100-0x4ffff`
- uImage: `0x50000`
- Cudy signature: PKCS#1 v1.5 / SHA-1
- signed data: `image[0:0x30000] || image[0x50000:EOF]`

Physical target MTD:
- mtd0 u-boot `0x30000`
- mtd1 u-boot-env
- mtd2 factory
- mtd3 debug
- mtd4 backup
- mtd5 bdinfo
- mtd6 firmware `0xF80000`
- mtd7 kernel
- mtd8 rootfs
- mtd9 rootfs_data `0x4A0000`

**Do not repeat:** ENG06 compressed in-place SquashFS patch caused red LED / boot failure.

---

## 5. Current physical target baseline

Physically observed/proven:
- model: `LT500D V2.0`
- ROM: `R25`
- kernel: `4.4.140`
- `bdinfo md5=OK`
- `bdinfo check=OK`
- `bdinfo checkuuid=OK`
- `bdinfo dbg=FAIL`
- persistent JFFS2 overlay active
- watchdog: PID1/procd, timeout 30s, feed 5s
- OPKG inventory: 127 records
- 4G stock/live-stock runtime works

Cumulative-17 physical verifier proved:
- six cellular files PASS
- stock `hcsh` PASS
- unlocked Telnet init PASS
- Dropbear running
- Telnet running/listening TCP 23
- hcshd running/listening UDP 56791
- 4G online on usb0, lease/route/DNS present
- `FILE_PARITY=PASS`

---

## 6. Minimal unlock delta ledger

### KEEP — UNLOCK_REQUIRED
`/etc/init.d/dropbear`
- stock: requires `bdinfo dbg == OK`
- OpenCudy: startup gate bypassed only
- current hash: `75a2dc540978e2712d32bd4e1d354e67cb5cf401d12981591915a1832871f2f8`

`/etc/init.d/telnet`
- stock: requires `bdinfo dbg == OK`
- OpenCudy: startup gate bypassed only
- current hash: `215dfc5b3fc694262dacd44610c61fc52df5217b6e062e7d59e2aa803c655622`

Stable engineering root access:
- stock retail firstboot regenerates root password from FUUID/HMAC;
- ENG07 neutralized this path;
- Cumulative-24 verifies the baked foundation hash instead of inventing/replacing it.

Installed sysupgrade unlock:
- `/rom/lib/upgrade/platform.sh`
- required baked hash: `1de73bc54df6117c0f24d5160a65086d50f37cc0cb9179f033ae83b928421369`
- Cumulative-24 verifies it but does not overwrite it.

### KEEP — UNLOCK PERSISTENCE
`/etc/init.d/cron`
- scheduled vendor `autoupgrade` suppressed
- hash: `9ee0c111e3a4ec84283422adf196322ff486a830d3e55522df75d5905fbeaaaa`

### KEEP — EXPLICIT PROJECT EXCEPTION
TR-069/CWMP:
- excluded by project requirement
- current init hash: `18b39a7c5308dd54d4ab27548c27fdf8040f6d6426ba8a72a1b1ac393c9e21dd`
- `cwmp.info.enable=off`

### RESTORE STOCK / STOCK-LIVE
- hcshd startup
- `4gup.sh`
- Quectel/Meig scripts
- antenna CBI
- normal Wi-Fi materialization

---

## 7. Cellular / 4G

Physical target proved the stock Cudy R25 cellular stack works while the firmware is unlocked.

Current final cellular hashes:
- 4gup stock-live: `f13536e75e2fbdb24d87c34bddb579fec538bf651238e7bc60ce15fce2194c32`
- quectel.sh: `016ebb5bc31922af8594d5c9afc6804d0e3a256f51ebf7d72b1993be7881c0fa`
- quectel2.sh: `3235838b3e50945881be0e6c0455709d11eba530cb2ac684f3f3b10f7ac10dd4`
- quectel-5g.sh: `361bc64c15af0a82c6ea50a3160f18667905c5ccd6f1120aae06f9732e9bbda6`
- meig.sh: `028d93240878523fa31ea36985f6fd817a6479440e51af3d39663e9edddf2814`
- antenna CBI: `f1437fc7467e7881995ddb57dbcaa0c1979690d33e8274bab16d8fae0539e876`

`4gup.sh` must include stock `99_oem` materialization (`sh /etc/rc.led` after matching ifdown lines).

Quectel modem firmware is frozen:
- `EC200AELV1LAR02A03M08`
- QGMR `_01.001.01.001`
- SubEdition V04

No modem firmware update is part of Cumulative-24.

---

## 8. Watchdog

Target probe:
- `/dev/watchdog` and `/dev/watchdog0`
- owner PID 1 `/sbin/procd`
- running
- timeout 30 sec
- feed frequency 5 sec
- magicclose false

The boot log watchdog lines are normal boot-time driver/init/procd handover. No OpenCudy-specific watchdog divergence is proven.

---

## 9. Performance / retry thread

Tamper/integrity and service retry are separate topics.

Target capture covered roughly four hours:
- gcom start: one observed boot lifecycle
- 4G successful bring-up: one observed lifecycle
- watchdog handover: boot only
- Wi-Fi/network `Command failed: Not found`: early bring-up pattern
- no persistent post-boot restart loop established

User reports router performance is now better.

Status: **acceptance/regression monitoring**, not the main active RE branch.

---

## 10. `bdinfo` integrity / tamper / debug

`bdinfo` provisioning state remains valid:
- md5 OK
- check OK
- checkuuid OK
- debug authorization FAIL in normal OpenCudy state

OpenCudy unlock deliberately does **not** forge global `bdinfo dbg=OK`.

### Exact Cudy Factory Debug mechanism — static RE

Exact target `/usr/lib/libbdinfo.so`:
- SHA-256 `dc2ac9f10739eb1f690acf3fbd9e17d8f824673f7faa7173db3894faa4cfc15b`
- MIPS16 `bdinfo_check_dbg()` statically reversed.

Token path:
1. raw `fread("/proc/sys/dev/flash_uuid")` — procfs newline retained
2. `bdinfo hmac`
3. literal `@2025`
4. SHA-256
5. lowercase `%02x` encoding
6. exactly 64 hex bytes in `/etc/rom_dbg`
7. `strcmp()` token validation

Decision gate:
- current retail `/etc/rom_release` exists
- this forces failure before token acceptance
- stock/vendor maintenance evidence removes `/etc/rom_release` before enabling maintenance access

Therefore Cudy Factory Debug enable must:
1. backup release/debug markers
2. remove `/etc/rom_release`
3. compute exact per-device token
4. write 64 bytes to `/etc/rom_dbg`, no newline
5. verify `bdinfo dbg == OK`
6. rollback on failure

CLEAN-03 implements this logic but activation is **STATIC_VERIFIED / TARGET_REQUIRED**.

Security consequence:
stock `/usr/libexec/login.sh` can enter direct `/bin/ash --login` when `bdinfo dbg=OK`.

---

## 11. OPKG

Exact historical OPKG:
- commit/version: `9f61f7acf3845d2e09675b49fec5d783d57eb780 (2017-12-08)`
- `/bin/opkg` SHA-256: `48332ad1dcbeb3bcdc3ceac968b85eef57cab0476bb77f21cb48b8d8d0c93cdf`
- architecture: `mipsel_24kc`

Physical inventory: 127 installed records:
- 41 userland/base reconstructed state
- 86 stock-ROM kmod records

Cumulative-24:
- carries OPKG binary/config/key/info support;
- carries FINAL-11 LuCI package manager;
- preserves healthy current status DB;
- reconstructs the captured 127-record status only if live status is missing/incomplete;
- keeps a 1024 KiB persistent-overlay safety reserve.

No “upgrade all” is performed automatically.

---

## 12. Cudy App binding

Cumulative-24 includes the stock Cudy app bind path:
- `/usr/sbin/cmsd-control`
- `/usr/lib/lua/luci/apprpc/system.lua`
- `/usr/lib/lua/cmsd/apprpc.lua`
- `/usr/lib/lua/cmsd/script.lua`
- `/etc/init.d/cmsd`

TR-069 remains disabled.

Installation does not force a cmagent/cmsd restart; existing binding/runtime state is preserved.

---

## 13. Developer V4 CLEAN-03

The prior V3 page duplicated many normal Cudy UI functions. CLEAN-03 corrects this.

Main Developer surface:
- OpenCudy SSH/Telnet access
- Cudy Factory Debug / Maintenance
- Engineering Terminal
- bdinfo/debug/integrity state
- hcshd state/listener
- MTD/flash/overlay internals
- process/listener/kernel/modules
- System Log / Kernel Log
- engineering snapshot/export

Normal Network/Wireless/VPN/etc. routes are **not duplicated**.

The complete 54-route donor inventory remains under collapsed **Source / RE Catalog** as evidence; only genuine Developer candidates are launchable.

Cudy Debug activation is not performed by installation. It requires an explicit Developer action.

---

## 14. What Cumulative-24 intentionally does NOT overwrite

Runtime/user state is not blindly reset:
- `/etc/config/network`
- `/etc/config/wireless`
- `/etc/config/dhcp`
- `/etc/config/firewall`
- root password/shadow
- modem firmware
- bdinfo/factory partitions
- kernel/DTB
- U-Boot/recovery RSA
- baked `platform.sh`
- baked firstboot password/console unlock files

Those foundational unlock paths are verified by `/rom` hash in preflight.

---

## 15. Install Cumulative-24

Copy the TAR.GZ to `/tmp`.

Run preflight:

```sh
cd /tmp
tar -xzf RE-LT500V2-R25-OPENCUDY-CUMULATIVE-24-TARGET-INSTALLABLE.tar.gz
cd RE-LT500V2-R25-OPENCUDY-CUMULATIVE-24-TARGET-INSTALLABLE
sh RE-PREFLIGHT-OPENCUDY-CUMULATIVE-24.sh
```

Only if `PREFLIGHT_COMPLETE=PASS`:

```sh
sh RE-INSTALL-OPENCUDY-CUMULATIVE-24.sh
```

Then:

```sh
sh /root/RE-OPENCUDY-CUMULATIVE-24/RE-VERIFY-OPENCUDY-CUMULATIVE-24.sh
```

**No reboot required.**

Rollback:

```sh
sh /root/RE-OPENCUDY-CUMULATIVE-24/RE-ROLLBACK-OPENCUDY-CUMULATIVE-24.sh
```

---

## 16. Status matrix

| Area | Status |
|---|---|
| Physical target identity / bdinfo integrity | TARGET_VERIFIED |
| SSH unlock | TARGET_VERIFIED |
| Telnet unlock | TARGET_VERIFIED |
| Stock hcshd runtime | TARGET_VERIFIED |
| Stock/live-stock 4G | TARGET_VERIFIED + LIFECYCLE_VERIFIED |
| Watchdog architecture/runtime | TARGET_VERIFIED |
| OPKG exact binary | SOURCE_VERIFIED / target present |
| OPKG 127 package inventory | TARGET_OBSERVED via physical capture |
| OPKG FINAL-11 UI | TARGET_OBSERVED / prior AJAX worked |
| Cudy app binding restore | TARGET_OBSERVED |
| Developer V4 CLEAN-03 static files | STATIC_VERIFIED |
| Cudy Factory Debug algorithm | SOURCE_VERIFIED |
| Cudy Factory Debug UI enable/disable | TARGET_REQUIRED |
| `bdinfo_check_uuid()` exact algorithm | UNRESOLVED |
| New full flash `.bin` | NOT BUILT / future milestone |

---

## 17. Unresolved / future work

1. Physically test CLEAN-03 Cudy Factory Debug **enable then disable**, no reboot.
2. Mark it TARGET_VERIFIED only if:
   - enable produces `bdinfo dbg=OK`
   - release/token marker state is as expected
   - disable restores `bdinfo dbg=FAIL` and retail marker
   - SSH/Telnet still operate as intended.
3. Finish exact `bdinfo_check_uuid()` RE if it becomes relevant to unlock/tamper behavior.
4. Build a reproducible full flash image only after obtaining/using a known-good SquashFS rebuild pipeline:
   - SquashFS v4
   - XZ compression
   - 512 KiB block size
   - preserve kernel prefix
   - preserve rootfs_data/JFFS2 geometry
   - validate image offline before physical flash.
5. For that future image, bake the **current live-good files**, not the stale engineering `/rom` versions.

---

## 18. Do not repeat these mistakes

- Do not perform compressed in-place SquashFS patching.
- Do not treat raw factory SquashFS as live-stock truth for files changed by `uci-defaults`.
- Do not conflate tamper/integrity with service retry/churn.
- Do not claim `opkg list_installed` is invalid on this old OPKG.
- Do not globally fake `bdinfo dbg=OK`.
- Do not restore Telnet behind the stock debug gate: Telnet is part of the OpenCudy unlock surface.
- Do not reboot for static RE/UI/package changes.
- Do not overwrite `/etc/config/*` for byte parity.
- Do not call STATIC_VERIFIED work TARGET_VERIFIED.

---

# English condensed handoff

OpenCudy LT500D V2/R25 is currently based on a physically verified good runtime state. The guiding rule is stock-first/minimum-delta. SSH and Telnet startup gates are deliberately unlocked while global Cudy debug remains inactive. Stock hcshd and stock/live-stock cellular behavior have been restored and physically validated. Watchdog behavior is normal. Performance has improved and no persistent service restart loop was captured over several hours.

Cumulative-24 is a no-reboot, overlay-installed target bundle that freezes the current good state, OPKG, Cudy app binding and cleaned Developer V4 interface. It does **not** claim to be a new flashable firmware image.

Cudy Factory Debug has now been statically reconstructed from the exact R25 `libbdinfo.so`, including the retail release-marker gate. CLEAN-03 implements an opt-in enable/disable path with backup and rollback, but the action itself still requires one physical target test before it may be called TARGET_VERIFIED.
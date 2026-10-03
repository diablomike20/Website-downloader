# Firmware Unlock 9 — P0 Mission: Belkin F9K1103 v1 native LEDE 17.01.5

## Mission
A jelenlegi elsődleges feladat a Belkin F9K1103 v1 / N750 DB saját LEDE 17.01.5 target buildjének lezárása.

**Nem** a Cudy UI porttal kell kezdeni.
**Nem** az R25 management RE-t kell először folytatni.
**Nem** F9K1109 image-et kell átnevezni.

## Target source repo
- Repository: `diablomike20/Belkin-F9K1103-Firmware`
- Base project folder: `firmware/f9k1103-lede-17.01.5/`
- Active fix branch at handoff: `lede-17.01.5-fix-board-token`
- Latest failing head: `3ef3cb7f6291d6b91ed09cf2a1cd15ece5fd5a86`

## Current build run
- Workflow: `Build F9K1103 LEDE 17.01.5`
- Run ID: `36959975523`
- Job ID: `110691296857`
- Result: FAILURE
- Created: 2026-10-02T03:23:41Z
- Completed: 2026-10-02T04:11:03Z

## Already solved — do not regress
The earlier loader-platform bug is no longer the blocker.

The log now correctly shows:
```
BOARD="F9K1103"
PLATFORM="ralink"
CROSS_COMPILE="mipsel-openwrt-linux-musl-"
```

It successfully builds:
- head.o
- loader.o
- cache.o
- board-ralink.o
- printf.o
- LzmaDecode.o
- data.o

and links `loader`.

Do not restart the old investigation around an empty `board-.o` or `cc -o .o` unless a new run explicitly regresses to that state.

## Exact current failure
```
mipsel-openwrt-linux-musl-ld -static --gc-sections -no-warn-mismatch   -e startup -T loader.lds -Ttext 0x81800000   -o loader head.o loader.o cache.o board-ralink.o printf.o LzmaDecode.o data.o

mipsel-openwrt-linux-musl-objcopy   -O binary -R .reginfo -R .note -R .comment -R .mdebug -S   loader loader.bin

mipsel-openwrt-linux-musl-objcopy:
Warning: Writing section '.text' to huge (ie negative) file offset 0xffffffff81800000.

mipsel-openwrt-linux-musl-objcopy:loader.bin[.text]: File truncated
```

## Required next investigation
Before changing code, capture the linked loader:
```
readelf -h loader
readelf -S loader
readelf -l loader
objdump -h loader
objdump -x loader
```

Compare with a successful OpenWrt 19.07 ramips lzma-loader build.

### LEDE 17.01.5 loader characteristics
- direct `$(LD)` link;
- `-Ttext $(LZMA_TEXT_START)`;
- `LZMA_TEXT_START=0x81800000` in this port;
- simple objcopy to raw binary.

### OpenWrt 19.07 relevant differences
The later loader Makefile changed several details:
- uses compiler driver for main loader link;
- `-nostartfiles`;
- `-Wl,--gc-sections`;
- `-Wl,-no-warn-mismatch`;
- `-Wl,-Ttext,...`;
- LTO;
- `-z max-page-size=4096`;
- removes `.MIPS.abiflags` in BIN_FLAGS;
- final loader2 link also uses max-page-size 4096.

These are **candidate explanatory differences**, not yet a proven fix.

## Preferred repair strategy
1. Reproduce exact failure.
2. Capture ELF sections/program headers.
3. Backport the smallest relevant loader-link change from 19.07.
4. Rebuild.
5. If still failing, isolate whether the problem is:
   - VMA/LMA;
   - section file offsets;
   - linker page size;
   - binutils behavior;
   - raw-binary conversion.
6. Avoid replacing the entire image pipeline unless required.
7. Preserve `PLATFORM=ralink`.

## F9K1103 board contract already encoded

### Flash
- 8 MiB SPI NOR.
- U-Boot: 0x000000..0x02ffff.
- env: 0x030000..0x03ffff.
- factory: 0x040000..0x04ffff.
- firmware: 0x050000..0x7effff = 0x7a0000 bytes.
- user-cfg: 0x7f0000..0x7fffff.

### Switch
- RTL8367R-VB family.
- SMI GPIO 1/2.
- LAN switch ports 0..3.
- WAN port 4.
- CPU port 5.

### MAC
- WAN: U-Boot env `HW_WAN_MAC`.
- LAN: U-Boot env `HW_LAN_MAC`.

### Radio
- SoC WMAC calibration: factory + 0x0000.
- PCI RT3091/RT3092 calibration: factory + 0x8000.

### GPIO
- reset absolute GPIO25.
- WPS absolute GPIO26.
- power 0.
- LAN 13.
- WAN 12.
- USB 9.

### USB
- EHCI enabled.
- OHCI enabled.
- two USB ports expected from F9K1103 board evidence.

### Image identity
- `UIMAGE_NAME=N750F9K1103VB`.
- target `ramips/rt3883`.
- intended image size <= 7808 KiB.

## Acceptance gate after build success
A successful `make` is not enough.

Required static validation:
- exact output filename recorded;
- size <= 0x7a0000;
- uImage magic 0x27051956;
- uImage name N750F9K1103VB;
- uImage header CRC valid;
- payload CRC valid;
- outer compression expected;
- SquashFS found;
- initramfs present;
- hashes produced;
- source commit recorded;
- artifact upload PASS.

Status after these:
**BUILD_VERIFIED / STATIC_VERIFIED**, not TARGET_VERIFIED.

## Physical test boundary
Do not flash automatically.
Physical boot belongs to a separate explicit user decision and should have:
- recovery plan;
- known-good F9K1109/OpenWrt19 image retained;
- LAN/boot/IP expectations;
- USB/Wi-Fi/switch checks;
- no calibration/env partition writes.

## After LEDE success
Only then start:
```
WR1200 V2 2.4.x Cudy userspace
+ LT500D 2.4.16 UI/architecture
+ Belkin LEDE target adapters
```

The F9K1109 OpenWrt19 image remains the hardware-reference oracle for device behavior when the LEDE backport is uncertain.

# RE-LT500V2-R25-FIRMWARE-UNLOCK-TRUTH-01

## Scope
Target: `LT500V2-R25-2.4.16-20250804-150319-flash.bin`
Board: Cudy LT500 V2 / R25 / MT7628 / 128 MiB RAM
Goal: remove the OEM firmware lock while preserving a safe recovery path and avoiding unnecessary U-Boot modification.

## Verified image structure
The image is **not encrypted** and is directly parseable using standard LEDE/OpenWrt formats.

- `0x000000-0x02ffff`: U-Boot (build string: `U-Boot 1.1.3 (Aug 4 2025 - 14:57:26)`)
- `0x030000-0x03ffff`: u-boot-env partition in the R25 DTS
- `0x040000-0x04ffff`: factory partition in the R25 DTS
- `0x050000`: standard legacy uImage begins
- uImage name: `R25`
- uImage payload size: `0x257d0d` bytes
- load/entry: `0x80000000`
- compression: LZMA
- uImage payload ends exactly at `0x2a7d4d`
- `0x2a7d4d`: SquashFS 4.0 begins
- SquashFS compression: XZ
- SquashFS block size: 262144 bytes
- SquashFS bytes-used: `0x8b29b6`
- SquashFS logical end: `0xb5a703`
- padding continues to `0xb90000`
- `0xb90000`: `deadc0de` marker
- `0xb90004`: OpenWrt/LEDE fwtool metadata record
- final fwtool trailer ends at `0xb9009b`

Metadata:

```json
{ "supported_devices": ["R25"], "version": { "dist": "LEDE", "version": "17.01.5", "revision": "2.4.16", "board": "ramips" } }
```

Important: the supplied image identifies itself as **LEDE 17.01.5**, not 17.05.

## Cryptographic lock findings
There is no fwtool signature record at the end of the supplied firmware; the final fwtool record is INFO metadata only (`type=1`). Therefore the kernel/rootfs image itself is not opaque or encrypted.

The OEM gate is implemented primarily in the running firmware by `/sbin/oem-check`. Its strings show checks for:

- board name
- firmware format/name
- image/header/data CRC
- RSA verification
- FIT-image validation paths

`/lib/upgrade/platform.sh` calls:

```sh
oem-check -b "$board" -o 0x30000 -f "$1"
```

for SPI-NOR targets such as R25.

The stock `/sbin/sysupgrade` already implements a built-in bypass path:

```sh
sysupgrade -F <image>
```

If image validation fails and `--force` is supplied, it sets `OEM_UPGRADE_BOOT=0` before continuing. On SPI-NOR R25, that causes the image to be written to the `firmware` MTD partition without touching U-Boot.

This is the preferred first-stage unlock mechanism because it keeps the original recovery bootloader intact.

## Bootloader/recovery lock
The factory U-Boot contains the recovery HTTP server (`Firmware Recovery`) and an RSA verification path (`rsa_verify`). The GPL tree also contains secure-image RSA/SHA256 code, but the actual R25 firmware partition starts directly with a uImage at `0x50000`; it does not use the `256-byte signature + 294-byte public-key + uImage` boot layout expected by `CONFIG_SECURE` in `cmd_bootm.c`.

Conclusion: boot-time kernel execution is not wrapped by that secure-image layout, while the U-Boot recovery upload path still appears to perform its own OEM/RSA validation.

Do **not** patch U-Boot in stage 1. Recovery-console unlocking can be handled later after the normal sysupgrade path has been proven.

## Existing access
The rootfs already contains Dropbear and enables both password authentication and root password authentication on port 22. Thus no new SSH daemon is required for an unlocked engineering build.

## Recommended unlock architecture

### Stage 1 — safe modifiable sysupgrade path
1. Keep `u-boot`, `u-boot-env`, `factory`, `debug`, `backup`, and `bdinfo` untouched.
2. Build a normal R25 sysupgrade payload beginning at the uImage (`0x50000` content of the factory image).
3. Repack modified SquashFS with the original XZ/256 KiB characteristics.
4. Preserve R25 uImage name, valid uImage CRCs, `deadc0de`, and fwtool metadata.
5. First flash through SSH using `sysupgrade -F` so OEM validation does not block the engineering image.

### Stage 2 — persistent OEM-check removal
Replace the vendor-only `platform_check_image()` dependency on `/sbin/oem-check` with an open validation implementation which still checks:
- R25 board identity
- valid uImage header/data CRC
- SquashFS presence
- supported_devices metadata
- maximum firmware partition size

This removes the proprietary RSA/OEM gate without turning image validation into an unconditional `return 0`.

### Stage 3 — GUI parity
Once stage 2 is in the installed rootfs, the stock LuCI firmware page (`sysupgrade -T`) can accept correctly formed engineering images without `-F`.

### Stage 4 — optional recovery/U-Boot unlock
Only if needed, change the U-Boot recovery uploader so it accepts the same open R25 image validation rules. This is higher risk because an incorrect U-Boot flash can hard-brick the device and may require SPI programming to recover.

## Generated baseline extraction
`RE-LT500V2-R25-extract-layout.py` extracts the stock image into:

- `u-boot.bin`
- `firmware-sysupgrade.bin`
- `kernel-uImage.bin`
- `rootfs.squashfs`
- `metadata.json`
- `report.json`

This creates the reproducible starting point for the unlocked engineering build.
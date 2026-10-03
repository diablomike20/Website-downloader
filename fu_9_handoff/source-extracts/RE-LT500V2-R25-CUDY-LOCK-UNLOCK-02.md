# RE-LT500V2-R25 — Cudy firmware lock reverse engineering + persistent unlock (02)

## Scope

Target factory image: `LT500V2-R25-2.4.16-20250804-150319-flash.bin`.
The image itself identifies the software base as **LEDE 17.01.5 / Cudy 2.4.16** and device `R25` (LT500 V2).

This checkpoint is not a generic `-F` workaround. It identifies the Cudy signing format, proves the RSA verification mathematically, locates the same verifier/key in userspace and U-Boot, and produces a firmware whose installed upgrade path accepts ordinary R25 OpenWrt/LEDE sysupgrade images without the Cudy private signature.

## 1. Exact Cudy lock format

Full factory image layout relevant to the lock:

- `0x000000..0x02ffff`: U-Boot (bootloader size `0x30000`)
- `0x030000..0x0300ff`: **256-byte RSA signature**
- `0x030100..0x04ffff`: gap/padding (not part of the signed digest)
- `0x050000`: legacy U-Boot uImage, name `R25`
- uImage payload ends / SquashFS begins at `0x2a7d4d`
- fwtool metadata begins at `0xb90000` with `deadc0de`

`/sbin/oem-check` scans from `bootloader_size` in `0x10000` increments until it finds legacy uImage magic `0x27051956`. For this image that is `0x50000`.

The signed message is exactly:

```
flash[0x000000:0x030000] || flash[0x050000:end]
```

The SHA-1 of that concatenation is:

```
16f7d0e6df82d4635193911419f048b7819d8e57
```

The 256 bytes at `0x30000` are an **RSA-2048 / PKCS#1 v1.5 / SHA-1** signature. Public exponent is `65537`.

RSA public verification of those 256 bytes produces a PKCS#1 v1.5 encoded block ending in:

```
3021300906052b0e03021a05000414
16f7d0e6df82d4635193911419f048b7819d8e57
```

The first line is the SHA-1 DigestInfo ASN.1 prefix; the second is the exact SHA-1 digest above. Therefore the signature scheme and signed byte ranges are proven, not inferred.

## 2. Where Cudy put the key and checks

`/sbin/oem-check` contains a U-Boot-style 2048-bit RSA public-key structure at file offset `0x4000`:

- `len = 64` words
- `n0inv = 0xf60d6ea5`
- 256-byte modulus
- 256-byte Montgomery `rr`

The exact same 520-byte public-key structure exists in the factory U-Boot at offset `0x2adc0`.
Its SHA-256 is:

```
5c0692d387ff241da9ac91d047ade652ac9b14b522dea6b86c467e6ebc9ca1bf
```

The same fixed 236-byte PKCS#1/SHA-1 padding prefix also exists in both components:

- `/sbin/oem-check`: offset `0x322c`
- U-Boot: offset `0x275dc`

So Cudy locks both the running firmware updater and the bootloader recovery path with the same OEM RSA key.

The private RSA key is not present in the supplied firmware/GPL tree. Modified images therefore cannot be authentically re-signed with the Cudy key from the available material.

## 3. Stock updater behavior

Stock `/lib/upgrade/platform.sh` calls:

```
oem-check -b "$board" -o 0x30000 -f "$1"
```

for the SPI-NOR R25.

Stock `/sbin/sysupgrade` starts with `OEM_UPGRADE_BOOT=1`. If its checks are force-overridden, it changes this to `OEM_UPGRADE_BOOT=0`, causing the firmware image to be written directly to the `firmware` MTD partition instead of treating the input as a Cudy full-flash package and skipping the first `0x50000` bytes.

This distinction is critical: a standard OpenWrt sysupgrade image starts directly at the R25 uImage, while a Cudy factory/full image starts with U-Boot and carries the RSA signature at `0x30000`.

## 4. Persistent unlock implemented

The generated unlocked firmware changes `/lib/upgrade/platform.sh` inside the stock SquashFS.

New policy:

1. If the uploaded image starts directly with legacy uImage magic `27051956`, it is accepted as a normal OpenWrt/LEDE sysupgrade image.
2. `fwtool_check_image` remains enabled and still checks `supported_devices`; therefore R25 metadata validation remains in place.
3. `platform_do_upgrade` detects a direct uImage and sets `OEM_UPGRADE_BOOT=0`, so no `0x50000` skip is applied and no bootloader write is attempted.
4. Cudy full-flash images still go through the original `oem-check` RSA validation path, preserving the signed OEM/bootloader update mechanism.

This removes the Cudy-private-key requirement for future standard R25 sysupgrade images while retaining board metadata checking and the original signed factory-image path.

## 5. How the stock SquashFS was patched

No foreign donor rootfs and no filesystem rebuild were used.

The stock SquashFS XZ fragment containing `/lib/upgrade/platform.sh` was located at SquashFS-relative offset:

```
0x2dbfa2
```

Original compressed stream size:

```
72964 bytes
```

The replacement `platform.sh` is exactly the same uncompressed inode length (`2202` bytes), so all fragment offsets remain unchanged. The modified fragment recompresses to `72824` bytes and is followed by `140` bytes of valid XZ stream padding, preserving the original on-disk block extent exactly.

Old `platform.sh` SHA-256:

```
32edaf265246103b29b4d73b72363f93db3ee6097bf8e4cf687a40212800bdb6
```

Unlocked `platform.sh` SHA-256:

```
531bd9bdd809f5eb89393506f00850c87e5737ac90b547d226df54a84fd4ad43
```

The kernel uImage is unchanged, including its original header/data CRCs. The fwtool trailer is also unchanged and remains at sysupgrade-relative `0xb40000`, with `supported_devices=["R25"]`.

## 6. Generated firmware

File:

```
RE-LT500V2-R25-2.4.16-CUDY-UNLOCKED-sysupgrade.bin
```

Size:

```
11796635 bytes
```

SHA-256:

```
dd1e86e12f062522667b8c0722a865b7f558946848a8429b965ec8a32f9e9637
```

It starts directly with the original R25 uImage and is intended for the `firmware` MTD/sysupgrade path. It deliberately does **not** contain a forged Cudy signature or a replacement bootloader.

## 7. Bootstrap from currently locked stock firmware

The currently running stock firmware will reject this image at `platform_check_image`, because the stock `oem-check` expects the proprietary Cudy full-image signature envelope. The one-time bootstrap therefore has to bypass the *old* checker while ensuring the image is treated as a direct firmware image:

```
sysupgrade -F /tmp/RE-LT500V2-R25-2.4.16-CUDY-UNLOCKED-sysupgrade.bin
```

Use `-n` as well only if configuration preservation is not wanted.

After booting the generated firmware, `-F` is no longer required for correctly formed R25 OpenWrt/LEDE sysupgrade images carrying matching fwtool metadata. The normal LuCI/sysupgrade check path now accepts the standard format.

Do **not** write the original full Cudy `flash.bin` to the `firmware` MTD partition with `OEM_UPGRADE_BOOT=0`: that file begins with U-Boot and is not a direct sysupgrade payload.

## 8. What remains intentionally locked

The installed firmware update path is unlocked. The factory U-Boot recovery web server still contains the same Cudy RSA verifier and public key. That bootloader was intentionally left untouched in this artifact because changing U-Boot carries a substantially higher brick risk and is not required to remove the firmware's normal update restriction.

A separate U-Boot-recovery unlock can be produced as a distinct, programmer/recovery-oriented stage if required; it should not be conflated with the normal firmware/sysupgrade unlock.

## 9. Reproducibility files

- `RE-LT500V2-R25-cudy-lock-verify.py` — independently verifies the Cudy RSA/SHA-1 signature and legacy uImage CRCs.
- `RE-LT500V2-R25-cudy-lock-verification.txt` — verifier output for the supplied stock image.
- `RE-LT500V2-R25-unlock-firmware.py` — deterministic in-place SquashFS fragment patcher producing the unlocked sysupgrade image from the supplied factory flash.
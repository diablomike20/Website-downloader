# RE-LT500V2-R25 — Fresh R25 rootfs audit + final engineering patch 04

## Basis

Primary rootfs evidence supplied by the user:

- `squashfs-root-LT500V2-R25-2.4.16-20250804-150319-flash.zip`
- SHA-256: `f587fa2c36d479e0a6223191546f9db5df6482ff2099d761ddd646d9b89a6fb0`
- ZIP entries: 2637
- Extracted tree: LEDE 17.01.5 / Cudy 2.4.16 / R25 / ramips-mt7628

Factory binary used only as the byte-accurate image container to preserve SquashFS layout, inode metadata, symlinks, permissions, kernel and fwtool structure:

- `LT500V2-R25-2.4.16-20250804-150319-flash.bin`
- SHA-256: `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

The fresh ZIP is the semantic/source truth for what is patched. The output is generated from the matching original factory image rather than rebuilding the ZIP into a new SquashFS, avoiding metadata/layout drift.

## R25-specific access restrictions confirmed directly in the fresh ZIP

1. `/etc/init.d/dropbear` blocks SSH startup with `bdinfo dbg`.
2. `/etc/init.d/telnet` blocks Telnet startup with the same debug gate.
3. `/etc/uci-defaults/11_fix_passwd` replaces root password with `SHA256(FUUID || HMAC)` on retail state.
4. `/lib/preinit/99_00_console` removes console login when Cudy debug is not active.
5. `/usr/libexec/login.sh` gives direct ash only in Cudy debug mode and otherwise uses `/bin/login`.
6. `/etc/uci-defaults/10_user` hides the username field using `luci.main.showuser='0'` and configures the Cudy web-admin identity.
7. `usr/lib/lua/luci/forbidden.lua` explicitly deny-lists `admin/system/terminal` although the Terminal backend is physically present.
8. `usr/lib/lua/luci/model/cbi/system/terminal.lua` contains the vendor Terminal backend and uses `luci.util.exec` with a command field.
9. `usr/lib/lua/luci/model/cbi/system/sandbox.lua` contains the vendor Telnet/Sandbox backend and reloads `/etc/init.d/telnet`.
10. `/lib/upgrade/platform.sh` routes normal installed-firmware validation through Cudy `/sbin/oem-check`.
11. `/etc/init.d/cron` installs scheduled Cudy autoupgrade execution.
12. The OpenWrt package database is present but no `opkg` executable exists in this R25 rootfs.

## Additional R25 behavior found but intentionally not treated as an access lock

The fresh ZIP also contains `bdinfo checkuuid` gates in WPS/mesh/vendor management paths and Cudy services such as `cmagent`, `cmsd`, `hcsh` and `cwmp`. These are provisioning/vendor-function dependencies, not proven root/access locks. They are preserved to avoid breaking normal Cudy modem/Wi-Fi/cloud functionality.

Likewise `/etc/pingcheck/online.d/99-autoupgrade` performs an autoupgrade *report* action when connectivity returns. This is not the scheduled updater itself and was not removed.

## Changes in the final engineering firmware

- Remove Dropbear `bdinfo dbg` startup gate.
- Remove Telnet `bdinfo dbg` startup gate.
- Replace stock hidden root hash with the project engineering root credential.
- Disable `FUUID || HMAC` first-boot root-password replacement.
- Keep serial askconsole enabled while retaining normal `/bin/login` password authentication.
- Force Cudy login initialization on the upgraded image so config-preserving upgrades also receive the new login policy.
- Set `luci.main.showuser='1'`.
- Force the username fields visible in all three hardlinked Cudy login-theme uses.
- Keep `admin` web login and add `root` to LuCI `sysauth`.
- Remove the explicit Terminal deny-list entry by retargeting it to a nonexistent route while leaving the real Terminal route intact.
- Surface authenticated shortcuts to the vendor-shipped Terminal, Telnet/Sandbox, Dmesg, Wi-Fi Log, Probe List and Wi-Fi Chart pages.
- Disable scheduled automatic Cudy OTA from `cron`; manual updater files remain.
- Permit direct R25 legacy-uImage sysupgrade payloads without the Cudy RSA envelope while preserving the original OEM checker for Cudy full-flash images.
- Preserve U-Boot, factory, bdinfo and hardware provisioning data unchanged.

## Deliberately not included

### OPKG executable

The R25 ZIP proves the package database exists but contains no matching `opkg` executable. This build does not silently inject a binary from another router or another OpenWrt generation. Restoring OPKG should be a separate ABI-tested package step.

### U-Boot recovery RSA

The bootloader/recovery RSA verifier is not part of this rootfs ZIP and is intentionally not modified in this image. Bootloader changes are a separate high-risk stage and should be done only with SPI recovery available.

## Final output

- `firmware.bin`
- size: `11796635` bytes
- SHA-256: `af7ff544f374f3e4344afe20a8a2bd6e9b7d10a17b66c1f5bb39ec4069a83594`

Validation performed after patching:

- legacy uImage header CRC: valid
- legacy uImage data CRC: valid
- fwtool trailer CRC: valid
- 151 SquashFS XZ streams parse successfully
- all required patch signatures present
- original retail Dropbear/Telnet gate signature absent

## Image type

`firmware.bin` is a direct **R25 sysupgrade image** beginning with the legacy uImage. It is not a full Cudy factory image containing U-Boot and the OEM RSA signature block.

A currently stock, locked Cudy updater will still require the existing bootstrap/forced sysupgrade route to install the first engineering image. Once this image is running, its installed normal sysupgrade path accepts correctly formed direct R25 sysupgrade images without the Cudy private signature.
# RE-LT500V2-R25 ENG06

Target: Cudy LT500V2 R25, Cudy 2.4.16 / LEDE 17.01.5.

This is the first cleaned **working engineering-image checkpoint** built directly from the stock R25 full-flash image. It has not yet been runtime-tested on physical hardware.

## Included patches

- Dropbear/SSH `bdinfo dbg` startup gate removed.
- Telnet startup gate removed for the engineering/recovery checkpoint.
- Temporary known Linux `root` password installed; firstboot FUUID/HMAC password replacement neutralized.
- Serial askconsole exposed while normal `/bin/login` remains in place; global `bdinfo dbg` is NOT forced.
- Cudy web username field defaults visible and remains rendered even with a preserved old `showuser=0` overlay.
- Automatic cron `autoupgrade` disabled.
- Pingcheck online `autoupgrade report` trigger disabled.
- CWMP/TR-069 remains installed and default OFF; `/tmp/vendor_spc` may no longer auto-set `cwmp.info.enable=on`.
- `hcshd` binary remains installed but its boot init returns before creating the daemon instance.
- Standard R25 legacy-uImage sysupgrade accepted without OEM RSA; OEM full-flash path still calls `oem-check`.
- U-Boot recovery RSA is untouched.
- `cmagent`, `cmsd`, and Mosquitto are retained because the stock Cudy mesh/topology/network stack has real dependencies on them.

## Developer Features status

The Developer Features UI is deliberately **not merged into ENG06 yet**. The working image comes first.

Verified Developer candidates retained for the next UI pass:
- Terminal (`admin/system/terminal`), explicitly present but blocked by `luci.forbidden`.
- Sandbox / Telnet (`admin/system/sandbox`).

The following are NOT developer-only; they are normal hidden child/detail routes and must remain in their normal Cudy chains:
- Kernel Log / dmesg
- Wireless Chart
- Wireless Probe List
- Wireless Log

## Static integrity verification

- Input stock full-flash SHA-256: `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`
- ENG06 sysupgrade SHA-256: `f9a9d8ae1419df115804fcafc752de45f3cd240c3652fe1f24aa4b935d3408b8`
- Output size: `11796635` bytes
- legacy uImage header CRC: verified
- legacy uImage payload CRC: verified
- fwtool info CRC: recalculated and verified
- fwtool metadata: `supported_devices=["R25"]`, LEDE `17.01.5`, revision `2.4.16`, board `ramips`
- SquashFS compressed-stream replacements decompressed and byte-verified after repacking.

## Login

Web login remains the existing Cudy account model; visible username is expected to be `admin`.

The temporary Linux root password is stored separately in `RE-LT500V2-R25-ENG06-root-password.txt`. Change it immediately after first successful login.

## Runtime gate

Physical-router validation is still required before calling this image final. In particular verify boot, Ethernet/Wi-Fi/cellular, web login, SSH, Telnet, local firmware update, and that CWMP/hcshd/automatic OTA remain inactive by default.
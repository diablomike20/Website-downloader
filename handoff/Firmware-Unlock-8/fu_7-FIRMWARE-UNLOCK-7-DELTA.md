# fu_7 — Firmware Unlock 7 delta

This file records the main new results produced after the previous FU6 master handoff.

## Firmware hunt scope expanded

The search scope became:
any Cudy dev/beta/test/engineering/internal/recovery/intermediate firmware, any model.

The user explicitly required:
do not stop after the first find; retrieve all accessible payloads.

## Clean archive rule

Correct final archive semantics:
- actual firmware binaries only;
- SHA-256 deduplication;
- one common manifest;
- OpenWrt intermediary Drive separate;
- HITS/INDEX/SUMMARY/search logs are evidence, not firmware.

## Actual FU7 payloads

WR3000:
WR3000-R31-2.4.2Beta-20250429-181532-sysupgrade.bin
SHA 13d49b81fabab3ccf5335509086dbb9811882dc279ee47f77116065228e2a6a6

P2 stable:
P2-R91-2.4.22-20251204-184925-sysupgrade.bin
SHA 592c494eb5f44beabb427907003801845ea0d47d51db50b1d5b97d40e3166b58

P2 RG500:
P2_RG500_A09.bin
SHA 7402449ddc19db64e42e41031d35b4a36f01e4d8b19219fcf3c4c6def897f52b

P2 CellularUpgrade:
R91-2.4.23b-20251208-CellularUpgrade.bin
SHA 9d27fb4535dff565cd8bb632933dc8a583f514bfcb2a027c740ddee0bc4f5f13

P2 beta:
P2-R91-2.4.29b-20260422-101502-sysupgrade.bin
SHA 3f8dae3d42ad6ba7d1314022eac6bc007d03fac274196b2c802f2835ab21c3f9

TR1200:
R46-2.1.10Beta-20240530-103557-flash.zip
SHA 57cfd4f6f1b782f5216b27ccf07dfbf535b028a08dc06d179fca70224be33e42

## Exact filename leads not recovered

R69-2.3.11Beta-20250429-100114-sysupgrade.zip
WR3600H-R69-2.3.15Beta-20250916-202013-sysupgrade.zip

Historical:
LT450-R9-1.15.5beta-20221121-180014-flash.bin
LT500-R9-1.15.5beta-20221121-180014-flash.bin

## Support beta markers

2.3.11Beta
2.3.12Beta
2.5.0b
2.5.1b
2.5.4b
2.5.10b
2.5.10b-20260624-151245
2.5.11b
2.5.14b
2.5.16b
2.5.28b

Support associations included:
M3000 -> 2.5.0b
M1200 -> 2.5.11b
M1500 -> 2.3.12Beta
M1300 -> 2.5.14b
WR3000 V1 latest-beta private email evidence
WR3000H private 2.5.x support evidence
WR6500H beta/support lead

## OpenWrt intermediary corpus

Original Drive batch:
41 top-level downloaded files.

Clean recursive binary collection:
42 unique firmware binaries.

Kept separate from dev/beta master.

## P2 deep audit

Static UBI/rootfs extraction completed.

Stable 2.4.22 vs beta 2.4.29b:
- beta-only 5
- stable-only 354
- changed common 218

Beta-only:
- /etc/hotplug.d/gcom/30-4g
- /etc/hotplug.d/tty/30-4g
- /etc/rom_research
- /usr/lib/4g/check.sh
- /usr/lib/4g/reup.sh

rom_research is an empty beta-only marker.
No direct code consumer was proven.

## Real hidden/internal P2 functions

Both stable and beta contain:
- web Terminal
- Telnet Sandbox
- Preset
- Firstboot policy
- Diagnostics
- AT Command
- Magic Swap
- Modem Reset
- Modem Upgrade
- AirDump route references

Terminal uses luci.util.exec.

These are not beta-exclusive.

## RG500 A09

Real engineering strings/components:
DEBUG MODE
debug_mode=1
PINTEST
FASTBOOT
RECOVERY
factorytest
UART/console
fastboot source
research/factory purpose firmware-download wording

Useful donor evidence.
Not flash-compatible with R25 EC200A.

## C200P clarification

The C200P artifact we already have is the exact firmware build used by the web emulator:
C200P R74 2.5.14-20260618-150931.

It is first-party, valid, unlisted and strongly internal/pre-release.
Developer/debug classification is not yet proven.

## Candidate-03 caution

Most recent user truth:
Candidate-03 did not install.
No backup exists.
Exact failure is unknown.
Do not rerun blindly.

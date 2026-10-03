# Firmware Unlock 9 — Do-not-repeat / preservation rules

## Global
- Do not restart reverse engineering from zero.
- Search handoff/source extracts/artifacts first.
- Do not upgrade evidence labels silently.
- Keep Belkin, R25 physical, OpenWrt23 frontend, and cross-donor truth separate.

## R25 forbidden / explicit constraints
- No bdinfo writes.
- No random/probabilistic UUID guessing.
- No timestamp spray.
- No CloudFront suffix brute force.
- No arbitrary firmwarevr enumeration.
- No synthetic activation.
- No real rom_alpha creation.
- No RG500 firmware on EC200A.
- No TR-069 restoration.
- No Candidate47 physical boot without explicit user choice.
- No Candidate-03 rerun without new failure evidence.
- No blind P2 file transplant.
- No H09 OPKG rewrite without concrete regression.
- No Wireless/WISP rewrite without concrete donor/target bug.
- No cellular rewrite as an unlock prerequisite.

## Closed investigations
- Probe-97 OTA 3x3 matrix.
- Stock R25 2.4.16 basic source audit.
- R25 Factory Debug token family static RE.
- C200P 2.5.14/2.5.15 support SSH architecture.
- P2 public 2.4.22→2.4.29 general lifecycle delta.
- P2 2.4.29→2.4.29b narrow beta delta.
- CP11-14 management-plane separation.

## Belkin rules
- Primary task is native LEDE 17.01.5 build.
- F9K1109 image is hardware reference, not F9K1103 native truth.
- Do not flash automatically after build success.
- Do not modify calibration/factory/U-Boot env/user-cfg partitions in image.
- Do not call build-verified image target-verified.
- Do not reopen the old empty PLATFORM/board-.o loader bug unless it reappears.
- Current blocker is objcopy high-VMA truncation after successful loader link.

## Cudy-on-Belkin later
- Port UI/userspace semantics, not Cudy hardware drivers.
- WR1200/LT500D binaries are not assumed compatible with RT3883 simply because they are MIPS.
- Prefer Lua/shell/UI reuse plus Belkin adapters.
- Keep the 8 MiB flash and 64 MiB RAM budget explicit.

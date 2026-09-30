# Firmware Unlock 8 — handoff package

Date: 2026-09-30
Predecessor chat: Firmware Unlock 7
Successor chat: Firmware Unlock 8

This package is the continuation handoff for the complete Cudy LT500D V2 / R25 — OpenCudy project.

Read in this order:

1. fu_7-PROJECT-MASTER-COMPLETE.md
2. fu_7-FIRMWARE-UNLOCK-7-DELTA.md
3. fu_7-CURRENT-STATE-MATRIX.md
4. fu_7-ARTIFACT-INDEX.md
5. fu_7-OPEN-ISSUES-ROADMAP.md
6. fu_7-HISTORICAL-LINEAGE.md
7. fu_7-FIRMWARE-UNLOCK-8-PROMPT.txt

Critical continuity rules:

- Do not restart donor reverse engineering from zero.
- Physical R25 target truth is authoritative.
- STATIC_VERIFIED is never TARGET_VERIFIED.
- Do not write bdinfo.
- Do not create real /etc/rom_alpha for probes.
- Do not manually trigger activation.
- Do not flash a candidate without a completed compatibility gate and explicit user decision.
- Preserve the working 4G path.
- TR-069/CWMP remains excluded.
- New successor artifacts should use the fu_8- prefix.
- Router command headings must be exactly: SSH terminálba:
- User prefers Hungarian and direct execution when saying hajrá / mehet / csináld / folytasd.

The package intentionally documents both major project worlds:
A) the physical R25 / OpenCudy engineering and firmware-unlock lineage;
B) the OpenWrt 23.05.5 donor-fidelity frontend/integration lineage.

They inform each other but must never be merged as if they were the same verification state.

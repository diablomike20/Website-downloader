# Historical lineage and lessons

## Early frontend line

V63 -> V66 -> V67 -> V68 -> V69.

Important historical constraints:
- donor-first UI;
- no fake data;
- TR-069 excluded;
- Wireless/WISP donor-validated branch not rewritten without a concrete defect;
- 36 Advanced positions;
- Developer separated;
- panel-level loading/error isolation;
- stale-response protection;
- no frontend invention of authoritative backend identities.

## RE/Integration hardening

Major lessons:
- CGI executable bits must survive source -> artifact -> extraction -> install;
- JSON CGI stdout must remain pure;
- Devices must merge by authoritative MAC;
- one owner per mutable subsystem;
- status GET must not become a writer.

## Physical unlock line

Stock -> engineering access work -> ENG07/ENG08 -> OPKG H09 -> H11 -> Developer V2/V3/V4 -> cumulative runtime packages -> C27.

Major correction:
cellular changes were not unlock requirements.
The working 4G path had to be restored to stock/live-stock behavior.

Major safety lesson:
compressed in-place SquashFS patching caused a boot failure and must not be repeated.

## Factory Debug line

Started as hidden/debug research.
Exact R25 token/gate mechanism was reversed.
Later physical lifecycle testing proved enable/disable and restoration.

## CSP2.5 line

R100 proved:
CSP2.5 still uses LEDE17/Linux4.4/MT7628.
New features are donor-mineable without assuming an architecture rewrite.

Hybrid R25/CSP2.5 state proved cross-generation userspace can exist on R25, but did not prove an official R25 image.

## Firmware hunt line

C200P proved:
an exact emulator build can exist as an unlisted canonical first-party Cudy CDN firmware.

FU7 then broadened to all-model dev/beta/internal/recovery hunting and recovered real WR3000, P2 and TR1200 payloads.

## Current caution

Candidate-03 did not install and no backup exists.
No inference of partial installation.
No blind rerun.

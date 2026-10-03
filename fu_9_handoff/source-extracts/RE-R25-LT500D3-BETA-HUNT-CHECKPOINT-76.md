# RE-R25-LT500D3-BETA-HUNT-CHECKPOINT-76

Date: 2026-09-27
Project: Cudy LT500D V2 / R25 – OpenCudy
Mission: LT500D 3.0 CSP 2.5 / beta / development firmware discovery
State: ACTIVE HUNT — RESUMABLE CHECKPOINT

## A. Physical target truth

- Cudy LT500D V2.0
- `system.board.rom=R25`
- stock firmware `2.4.16-20250804-150319`
- LEDE 17.01.5 / Cudy 2.4.16
- MT7628AN / MIPS24KEc
- 128 MiB RAM / 16 MiB NOR
- modem Quectel EC200A-EL
- modem FW `EC200AELV1LAR02A03M08`
- cellular path: EC200A -> cdc_ether -> usb0
- `bdinfo model=LT500D V2.0`
- `bdinfo board=LT500D`
- `bdinfo version=1.0`
- region EU / country DE

No real bdinfo field was modified during OTA research.

## B. OTA channel truth — TARGET VERIFIED

Stock `/sbin/autoupgrade`:
- TEST branch when `bdinfo rdtest == 1` or `/etc/rom_alpha` exists.
- All tests used temporary script/marker/token/fwinfo files under `/tmp`.
- Real `/etc/rom_alpha`, `/etc/rom_version`, bdinfo and flash were not modified.

Observed R25 update selectors:
- exact `devtype=R25` required in tested matrix;
- JSON `firmwarevr` controls version eligibility;
- HTTP `vr` header alone is not sufficient.

Physical split test:
- header CURRENT + JSON OLD -> update offered;
- header OLD + JSON CURRENT -> no update.

Version behavior:
- 0.0.0 -> 2.4.16
- 1.15.28 -> 2.4.16
- 2.1.1 -> 2.4.16
- 2.4.15 -> 2.4.16
- 2.4.16 with old/current/new timestamp -> no update
- 2.4.17 -> no update
- 9.9.9 -> no update

Strong interpretation: semantic `2.4.16` boundary matters; same-version timestamps do not create eligibility.

Beta spelling probes around current 2.4.16 did not expose another branch.
Language/full probes (`auto`, `en`, `zh-cn`) did not change selection.

## C. Four independently retrieved 2.4.16 OTA payloads

i18n TEST:
`https://d1jvyy13vm72kv.cloudfront.net/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_48004.bin`

i18n PROD:
`https://d1jvyy13vm72kv.cloudfront.net/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_20729.bin`

CN TEST:
`https://cn-cf.cudycloud.com/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_95221.bin`

CN PROD:
`https://cn-cf.cudycloud.com/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_30196.bin`

All four:
- size 12,124,315 bytes
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`
- SHA-256 `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`
- byte-for-byte identical to known retail stock 2.4.16.

TEST metadata predates PROD metadata, showing a real staging->production pipeline, but the current staged payload is still the retail 2.4.16 object.

## D. Modem OTA result

Stock has an apparent `modulevr` command-substitution bug. Temporary corrected probes sent:
- real `EC200AELV1LAR02A03M08`
- synthetic M07
- synthetic M01
- `0`

TEST and PROD always returned `"module": {}`.
No modem OTA object was discovered.

## E. Official CSP 2.5 state

Cudy officially lists:
- LT500 3.0
- LT500D 3.0

in the CSP 2.5 support plan.

As of this checkpoint, the official LT500D 3.0 Download Center still lists:
- 2.4.16 (05-Aug-2025)
- 2.1.1
- 1.15.28

Latest public LT500D 3.0 filename:
`LT500V2-R25-2.4.16-20250804-150319-flash.zip`

LT500D 2.0 currently lists the same 2.4.16 file.

Important comparison:
LT300 3.0, which is also in the CSP 2.5 plan, already has public CSP 2.5.12:
`LT300V3-R100-2.5.12-20260518-234632-flash.zip`

Therefore the support-plan list is not a strict completed rollout order. LT500/LT500D R25 can genuinely still be pending even while other LT models already have CSP 2.5.

## F. Major new static R25 finding: V3-class Meig modem support is ALREADY in 2.4.16

The extracted stock R25 2.4.16 rootfs already contains complete Meig support.

`/usr/lib/4g/detect.sh` recognizes Meig USB IDs including:
- `2dee:4d57` -> RNDIS / `usb0`, vendor `meig`
- `5c6:f601`
- `2dee:4d22`

`/usr/lib/4g/meig.sh` explicitly handles:
- `SLM770A*`
- SLM770A regional identifiers such as `770AREU`, `770ACE`, `770ARCB`, `770ASCB`, `770AHSA`
- corresponding band defaults.

`/usr/lib/4g/upgrade.sh` explicitly supports modem firmware upgrade for:
- `EC200*` via `qdloader`
- `SLM770A*` via `AT+MEIGEDL` + `mdloader`

This is highly relevant because community reports indicate LT500D V3 units can use MeigLink SLM770A while the physical V2 target uses Quectel EC200A.

Interpretation:
the public/shared R25 2.4.16 router firmware was already built to support both modem families. A V3 unit therefore does not require a distinct router firmware merely because it contains SLM770A.

This substantially strengthens the hypothesis that a future LT500D 3.0 CSP 2.5 system firmware can remain on board ID `R25`.

It does NOT prove V2 compatibility with an eventual V3-only release.

## G. cmagent / JWT correction

`cmagent` on the physical target runs:
`/usr/sbin/cmagent -m router -b 127.0.0.1 -p 8883 -a -t 30`

`cmsd.cloud.enabled='0'`.

Static R25 `cmagent` and `auth_plugin_jwt.so` contain device identity / JWT / bdinfo material, but current evidence fits local Cudy Mesh MQTT authentication better than OTA selection.

Therefore:
`cmagent deviceid == OTA V2/V3 cohort selector`
is NOT current truth.

The HTTP OTA client itself does not explicitly send `bdinfo model=LT500D V2.0`.

## H. Beta distribution evidence

Cudy has historically published beta firmware for LT-series devices.
The official beta FAQ documents LT18/LT450/LT500/LT500D beta use.

In 2026 support comments, Cudy users also report receiving CSP 2.5 beta firmware directly from technical support by email on some models, while Cudy support explicitly says beta firmware is not available for some other models.

Thus:
- private/support beta distribution is real;
- it is model-specific;
- absence from Download Center does not prove no private beta exists;
- there is still no exact public/indexed LT500D 3.0 CSP 2.5 beta filename or URL found.

## I. Current strongest explanation ranking

1. MOST PLAUSIBLE:
   LT500/LT500D R25 CSP 2.5 is still under model-specific development/validation and not publicly released yet.

2. PLAUSIBLE:
   a support-only/test beta exists but is not indexed/public.

3. PLAUSIBLE BUT UNPROVEN:
   TEST OTA uses a server-side device/cohort allow-list that excludes this physical V2 unit.

4. LESS SUPPORTED THAN BEFORE:
   V3 necessarily requires a different router board identity.
   The shared R25 image plus built-in SLM770A support argues against this being required merely for the modem change.

## J. Next hunt

Assistant-owned:
1. continue exact LT500D/LT500 3.0 beta/dev filename and URL hunting;
2. inspect Cudy CSP comments/support breadcrumbs for LT500D-specific replies;
3. compare board-ID continuity across 2.4 -> 2.5 Cudy releases;
4. inspect historical/current CDN naming patterns without inventing nonexistent builds;
5. search community V3 diagnosis/firmware screenshots/dumps for an exact `rom_version`;
6. keep static analysis local;
7. ask for target SSH only when a specific unresolved hypothesis cannot be answered otherwise.

No flashing.

END CHECKPOINT
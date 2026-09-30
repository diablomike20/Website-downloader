
# fu_6 — Firmware-Unlock_6 mély handoff a Firmware-Unlock_7 számára

## 0. Aktuális P0

**Exact LT500/LT500D V2 / R25 CSP2.5 build identity + firmware artifact felkutatása.**

A C200P sidequest most már lezárt mechanizmus-proof:
egy emulatorban használt, normál letöltési oldalon nem listázott firmware exact canonical Cudy CDN objectje ténylegesen megtalálható volt.

Ezért az R25 kutatás fókusza:

> szerezz exact R25 CSP2.5 build stringet → próbáld a bizonyított canonical filename/path mintát → static audit.

Nem:
> találgass verziókat és timestampeket.

---

# 1. Jelenlegi authoritative R25 identity

Target:
- Cudy LT500D V2.0
- board/devtype R25
- EU / DE
- MT7628AN
- 128 MiB RAM
- 16 MiB NOR
- Quectel `EC200AELV1LAR02A03M08`
- cellular `usb0`
- checkuuid OK

Stock:
`2.4.16-20250804-150319`

Hybrid:
`2.5.12-20260518-234632`

A hybrid nem official R25 release.

---

# 2. Latest live binary capture

`fu_6-R25-LIVE-MTD6-AUDIT-01.md` a ZIP-ben külön source-copyként is szerepel.

mtd6:
- 16,252,928 bytes
- SHA `d4e30da79e322d13e707c15c95f7f007b916b7d20871ca79a192182506ad408c`

Kernel:
- R25
- stock 2.4.16 kernel/uImage byte-identical region

Rootfs:
- rebuilt CSP2.5-era
- mkfs 2026-05-18 15:39:35 UTC
- XZ
- 2.5.12 exact rom_version overlayben

Online-update response a recovered overlayből:
`{"data":{"firmware":{},"module":{}},"msg":"","ret":0}`

Ez BEFORE-ACTIVATION binary corroboration.

---

# 3. Probe-97 closed finding

OLD:
`2.1.1-20240419-090237`

STOCK:
`2.4.16-20250804-150319`

REAL:
`2.5.12-20260518-234632`

3x3 TEST/PROD matrix:

- JSON OLD -> stock object
- JSON STOCK -> empty
- JSON REAL -> empty

HTTP vr OLD/STOCK/REAL nem változtatott selectionön.

**Ne ismételd.**

---

# 4. Activation — státusz és bizonyítási határ

Source mechanism:
- `S99activate`
- wait `.timeclock`
- sleep 86400
- prod event-i18n activation
- ret==0 -> activate=1

Hybrid targeten korábban:
- activation process naturally running
- `.timeclock` present
- sleep 86400 observed
- activate flag még empty volt a korábbi mérésben

A 2026-09-29-i későbbi MTD auditban recovered current system configban nincs `activate` option.

Ez **nem elég** egy tiszta, jelen idejű activation verdicthez, mert:
- dump timing;
- UCI overlay state;
- esetleges reboot;
- subsequent lifecycle

külön kezelendő.

Firmware-Unlock_7 ne találgassa. Ha target elérhető, read-only állapotot mérjen.

---

# 5. Read-only activation check

SSH terminálba:

```sh
uci -q get system.@system[0].activate
ps | grep '[a]ctivate'
ps | grep '[s]leep 86400'
cat /etc/rom_version
uci -q get system.board.rom
bdinfo checkuuid
```

Ha `activate=1`:
- TARGET_VERIFIED activation success;
- nem official R25 proof;
- nem OTA cohort proof.

Utána csak szűk OLD/STOCK/REAL before/after OTA control.

---

# 6. C200P exact hidden artifact — canonical proof

Emulator:
`C200P V1.0 / R74 / 2.5.14-20260618-150931`

Exact first-party URL:

`https://www.cudy.com/cdn/shop/files/C200P-R74-2.5.14-20260618-150931-flash.zip`

ZIP:
- 12,898,647
- SHA `a4f5f6494bcbdf41bfcd8573a22531fbd2115b5cb2769f5f44da213a900a7e98`
- MD5 `f7f8622805e4ee6a88cf6852486dbff2`

BIN:
- 13,172,891
- SHA `8ba6c51d13d72d2871a1b5e8bbcb4318c2fd4234898f8c1e9e6c30502913e0e8`
- MD5 `7b5bd62f2e081c82bfb901ddfe4de0cd`

Metadata:
- supported_devices R74
- LEDE 17.01.5
- revision 2.5.14
- ramips

Ez SOURCE_VERIFIED + EMULATOR_VERIFIED.

---

# 7. Miért fontos a C200P finding R25-höz

Előtte csak hipotézis volt:

`emulator exact build` → `canonical CDN exact ZIP talán létezik`

Most bizonyított mechanizmus.

Ezért R25-nél az exact build identity megszerzése a legértékesebb hiányzó adat.

A C200P-nél nem kellett Shopify `?v=` query paraméter a tényleges objecthez.

Tehát a kanonikus `/cdn/shop/files/<exact filename>` közvetlenül értékes.

---

# 8. C200P dev/demo classification

Az emulator `Demo` cloud hostert stubolja.

A firmware rootfsben:
- real cloud management code van;
- real cmagent/cmsd;
- nincs emulator_token_stub;
- nincs mock_api;
- nincs hardcoded Demo hoster;
- nincs luci-emulator-bootstrap.

Ezért:
- unlisted/pre-release/internal: strong inference;
- developer/debug: NOT PROVEN;
- beta: NOT PROVEN.

Ne nevezd dev buildnek evidence nélkül.

---

# 9. AC_Cloud key evidence

42 mock API snapshot.

Firmware manager object:
- `C200P V1.0`
- vr `2.5.14-20260622-090745`
- lastvr empty
- status 1
- upgrade_status timeout

Ez más build, mint a 06-18 exact C200P emulator.

A 06-22 build artifactját nem találtuk meg ebben a munkában.

---

# 10. Current emulator archive state

Latest head run:
`36532425169`

- 90 models
- completed 90
- failed 0
- 34,769 files
- 527,278,057 bytes
- AC_Cloud 325 files
- 12,431 master routes

Artifact:
- ID 11018311218
- compressed 128,021,977
- digest `83e407ddbc1389355e4418f3f9a605b32227946cc7e8f680b05b33e5060bc02a`

A lokális `/mnt/data/fu_6-CUDY-ALL-EMULATORS.zip` egy korábbi sikeres all-run lehet, ezért **hash/size alapján ne nevezd automatikusan latest head artifactnak**. A latest GitHub artifact ID a fenti.

---

# 11. Website-downloader current state

Repo:
`diablomike20/Website-downloader`

Branch:
`fu_6-cudy-forensic`

Latest head:
`901c10a553969169a996370ea8a91f51aad7b02f`

PR:
`#1`

Current key source files:
- `cudy/forensic.js`
- `bin/cudy-forensic.js`
- `test/cudy-forensic.test.js`
- Cudy workflows

Latest head checks:
- Cudy forensic tests SUCCESS
- C200P capture SUCCESS
- all emulator archive SUCCESS
- R25 comment hunt SUCCESS
- CodeQL FAILURE
- dependabot workflow failure

CodeQL/dependabot failure nem bizonyít crawler failuret; külön CI/security concern.

---

# 12. Key branch commit lineage

Newest relevant:

- `901c10a` — Cudy comments R25 CSP2.5 trace hunt
- `90498d2` — evidence-derived R25 emulator/CDN candidates
- `9811ba4` — rootfs extraction YAML fix
- `88fa7a8` — exact SquashFS root extraction as root
- `c02948b` — C200P 2.5.14 rootfs extract
- `4e5000c` — exact C200P first-party capture
- `1fe8524` — exact C200P path probe
- `2a6fb14` — all emulator autoupgrade sweep
- `c5eb576` — LT500 query-specific update snapshot
- `763276b` — cbi_xhr_load regression
- `d505fa7` — cbi_xhr_load capture
- `a903cae` — AC Cloud full capture
- `480137c` — AC Cloud regression
- `cf09245` — AC Cloud mock API capture
- `0dca54c` — AC Cloud device/firmware probe
- `6401b61` — AC Cloud path probe
- `a200f8b` — extension regression
- `0b43b25` — real asset extension preservation
- `789e2ba` — raw URL collision regression
- `d092a36` — URL response collision preservation
- `27880ec` / `a2198fe` — legacy model-prefix route handling
- `190d59a` — lazy UI asset / legacy page seeds
- `4ec31df` / `7e7e97f` — dotted model directory fix
- `4f3b9ba` — per-model isolation
- `a4ec160` / `af3849f` — all emulator + AC_Cloud

---

# 13. Latest R25 targeted negatives

Run `36532205425`.

Hidden emulator names:
all 404.

Exact evidence-derived CDN candidates:
all 404:
- R25 + R100 2.5.12 timestamp
- R25 + C200P 06-18 timestamp
- R25 + C200P AC Cloud 06-22 timestamp
- R25 + public C200P 2.5.15 timestamp

Ezeket ne próbáld újra.

---

# 14. Latest Cudy comment corpus result

Run `36532421855`.

- 129 relevant pages/blocks
- exact R25/LT500 2.5 firmware token: 0

Ez nem azt jelenti, hogy support email/private object nincs.

Csak a vizsgált publikus comment HTML nem ad exact token leaket.

---

# 15. Current strongest hypotheses, helyes evidence címkékkel

1. **Cudy unlisted firmware object persistence**  
   SOURCE_VERIFIED mechanizmus C200P-n.

2. **R25 CSP2.5 private/support firmware létezhet**  
   ARCHITECTURAL / DISTRIBUTION LEAD, mert private support channel verified; exact R25 artifact not found.

3. **R25 exact build string valószínűleg nem R100/C200P timestamp másolat**  
   supported by targeted negative probes; ne használj donor timestamp copy guess-t.

4. **Activation server state befolyásolhat OTA eligibilityt**  
   UNKNOWN. Nem bizonyított.

5. **Modem family drop az oka**  
   SOURCE_VERIFIED_NEGATIVE az egyszerű változatra: R100 CSP2.5 megtartja EC200AEL supportot.

---

# 16. Legjobb következő evidence-források

Prioritás:

1. exact support email / attachment filename;
2. support screenshot, ahol full version látszik;
3. Cudy page source / theme JSON / Shopify reference exact LT500V2-R25-2.5;
4. Google/GitHub indexed exact filename residue;
5. forum mirror/attachment, ahol full canonical filename;
6. AC_Cloud vagy más web bundle, ahol LT500/R25 `vr` objektum;
7. physical target server-side activation utáni kontroll.

Kizárólag olyan leadből legyen direct CDN probe, amely exact build stringet ad.

---

# 17. Candidate megjelenésekor azonnal rögzítendő

- request URL;
- HTTP status;
- redirects;
- content-type;
- content-length;
- last-modified / etag;
- bytes;
- SHA256;
- MD5;
- magic/file type;
- archive entry names;
- inner BIN hash;
- md5.txt;
- uImage;
- SquashFS;
- fwtool;
- supported_devices;
- build timestamps;
- modem stack;
- compare stock.

---

# 18. Ne hagyd elveszni a nagyobb OpenCudy projektet

A Firmware-Unlock chat P0 fókuszú, de a teljes projektben már kész:
- V69 cumulative frontend/integration lineage;
- H09 OPKG lifecycle;
- H11 theme partial branding;
- Developer V3 engineering catalog;
- EM/RE forensic corpus.

Ha új CSP2.5 source előkerül, ezeket informálja, nem nullázza le.

---

# 19. User interaction szabályok

A user:
- eredményt akar;
- nem szereti a „most ezt fogom csinálni” státuszokat;
- ha azt mondja `hajra`, akkor dolgozz;
- ha azt mondja `próbáld ki`, ténylegesen futtasd és ellenőrizd;
- ne mondd, hogy „kész”, ha a tényleges run még fut;
- ne állíts teljes auditot, ha nem olvastad/elemezted teljesen.

---

# 20. File naming az utód chatben

Az előd prefix: `fu_6-`.

Az utód chat neve `Firmware-Unlock_7`, ezért **minden új artifact neve `fu_7-` prefixszel kezdődjön**.

Historical `RE-`, `WS-`, `fu_6-` neveket ne nevezd át utólag.
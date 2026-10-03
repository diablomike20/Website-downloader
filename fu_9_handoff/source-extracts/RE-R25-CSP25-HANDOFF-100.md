# RE-R25-CSP25-HANDOFF-100

**Dátum:** 2026-09-28  
**Projekt:** Cudy LT500D / OpenCudy  
**Elsődleges target:** Cudy LT500D V2.0, board `R25`  
**Aktuális munkaszál:** exact R25 CSP2.5 beta/dev/support firmware felkutatása, OTA/cloud mechanika lezárása, R100 CSP2.5 activation megfigyelése fizikai R25 hybrid targeten  
**Státusz:** HANDOFF / beszélgetés lezárása  

---

## 0. Rövid vezetői összefoglaló

A beszélgetés végére az R25 OTA-kiválasztás lényegi mechanikáját fizikailag sikerült lezárni, de **az exact hivatalos vagy support-only LT500/LT500D R25 CSP2.5 firmware artifact továbbra sincs meg**.

A legfontosabb új eredmények:

1. A fizikai LT500D V2.0 továbbra is `R25` identitással fut, `bdinfo checkuuid=OK` mellett.
2. A target jelenleg egy **R100-ból származó / hibrid CSP2.5 userspace állapotot** futtat, amely `/etc/rom_version` szerint:
   `2.5.12-20260518-234632`.
   Ezt **nem szabad hivatalos R25 release-nek nevezni**; ez targeten futó hybrid állapot.
3. Probe-97 bizonyította, hogy a tesztelt `checkupdate` útvonalon a firmware kiválasztását a JSON `firmwarevr` mező vezérli; a HTTP `vr` header három külön exact buildértéke között nem volt megfigyelhető selection-hatás.
4. `firmwarevr=2.1.1-20240419-090237` esetén TEST és PROD is mindig a stock R25 `2.4.16-20250804-150319` firmware-t ajánlja fel, akkor is, ha a HTTP `vr` header a hybrid `2.5.12-20260518-234632`.
5. `firmwarevr=2.4.16-20250804-150319` és `firmwarevr=2.5.12-20260518-234632` esetén TEST és PROD egyaránt üres firmware objektumot ad a jelenlegi eszközidentitásnak.
6. A normál R25 OTA TEST/PROD ág tehát jelenleg nem publikál 2.4.16-nál újabb eligible firmware-t ennek a device identitynek.
7. A support/private firmware distribution viszont dokumentált Cudy gyakorlat, és kifejezetten LT500/LT500D családban is előfordult; ezért a keresett CSP2.5 image még lehet email/support-only vagy más szerveroldali cohort mögött.
8. Az R100 CSP2.5 `/usr/sbin/activate` mechanizmusa átkerült a hybrid R25 targetre, enabled `S99activate` init service-ként, és **ténylegesen fut**.
9. A targeten a `/tmp/.timeclock` létrejött (`Sep 28 01:37`), `system.@system[0].activate` még üres volt, az `activate` shell process futott. A későbbi process-listában látszott egy `sleep 86400`, ami összhangban van a gyári activation script 24 órás késleltetésével.
10. A hybrid targetet ezért most **nem szabad rebootolni**, ha a cél a természetes gyári activation lifecycle megfigyelése. A várható activation időpont hozzávetőleg 2026-09-29 01:37 helyi idő, feltéve hogy a sleep közvetlenül a `.timeclock` megjelenése után indult és a router addig nem indul újra.
11. A legnagyobb nyitott kérdés: a gyári activation event után változik-e az OTA eligibility. Ezt csak activation UTÁN, ugyanazon eszközön, azonos read-only `checkupdate` kontrollal érdemes összevetni.

---

# 1. Projektfókusz és evidencia-szabályok

A jelenlegi P0 feladat **nem frontend, nem OPKG, nem Developer, nem újabb általános donor RE**, hanem:

> **Megtalálni az exact LT500/LT500D V2 / R25 CSP2.5 firmware-t, vagy legalább az exact build identityt, fájlnevet, support-delivery bizonyítékot vagy közvetlen letöltési objektumot.**

Elsődleges hardver és truth:

- **TARGET:** LT500D V2.0 / `R25`.
- **R100:** kizárólag donor/corroboration; soha nem írhatja felül az R25 truthot.
- TR-069/CWMP továbbra is kizárt az OpenCudy célból.
- 4G működő baseline-hoz nem szabad mellékesen hozzányúlni.
- `bdinfo` írás nem megengedett rutin tesztekben.
- `/etc/rom_alpha` valós létrehozása/engedélyezése nem megengedett, ha ideiglenes vagy statikus vizsgálat elég.
- Talált beta/dev image-et nem szabad flash-elni külön compatibility gate nélkül.

Használt evidence-osztályok:

- `TARGET_VERIFIED`
- `SOURCE_VERIFIED`
- `R25_SOURCE_VERIFIED`
- `WEB_VERIFIED`
- `CROSS_DONOR_CORROBORATED`
- `ARCHITECTURAL_LEAD`
- `SOURCE_GAP`
- `UNKNOWN`
- `NOT FOUND`
- `TARGET_REQUIRED`

---

# 2. R25 alapazonosság és ismert firmware-ek

## 2.1 Fizikai R25 target – stock referencia

Stock R25 build:

`LT500V2-R25-2.4.16-20250804-150319`

Fő ismert adatok:

- board/devtype: `R25`
- firmware: `2.4.16-20250804-150319`
- platform: LEDE 17.01.5 / ramips mt76x8 / mipsel_24kc
- SoC: MT7628AN
- RAM: 128 MiB
- flash: 16 MiB NOR
- régió: EU
- country: DE
- modem: `EC200AELV1LAR02A03M08`
- working cellular interface: `usb0`
- `bdinfo checkuuid = OK`

Stock outer flash SHA-256:

`57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`

Stock extracted rootfs ZIP SHA-256:

`f587fa2c36d479e0a6223191546f9db5df6482ff2099d761ddd646d9b89a6fb0`

## 2.2 R100 CSP2.5 donor

Donor identity:

`LT300V3-R100-2.5.12-20260518-234632`

Donor package SHA-256:

`8cd02de01b9db1caff6046d65768c9ce6f2c8db0913f6f7faa831971b5e46653`

Donor flash version:

`2.5.12-20260518-234632`

Inner flash MD5:

`7c8cf596029d0ce5940c5bafbb7a0fbd`

Inner flash SHA-256:

`03641ed863911618155ddb55ed2c45f4c23abd330a4e171bff4491ffcda49a82`

A donor csak mechanika/naming/cross-generation evidence. Nem hivatalos R25 image.

---

# 3. Stock R25 OTA mechanika – statikus RE

A stock R25 `/sbin/autoupgrade` a következő Cudy API-kat használja.

## 3.1 i18n

TEST:

`https://i18n-test.cudycloud.com/device/v1/auth`

`https://i18n-test.cudycloud.com/device/v1/checkupdate`

PROD:

`https://i18n.cudycloud.com/device/v1/auth`

`https://i18n.cudycloud.com/device/v1/checkupdate`

Event endpointok:

`https://event-test.cudycloud.com/device/v1/event`

`https://event-i18n.cudycloud.com/device/v1/event`

## 3.2 CN

TEST:

`https://cn-api-test.cudycloud.com/device/v1/auth`

`https://cn-api-test.cudycloud.com/device/v1/checkupdate`

PROD:

`https://cn-api.cudycloud.com/device/v1/auth`

`https://cn-api.cudycloud.com/device/v1/checkupdate`

## 3.3 Request identity

A stock kliens a kérésben többek közt használja:

- `fuuid`
- raw `vr` HTTP header = `/etc/rom_version`
- `devtype` = `system.board.rom`
- `lan`
- `token`

JSON oldalon:

- `mac`
- `firmwarevr`
- `region`
- opcionális `modulevr`
- opcionális `isfull`

A régi R25 normalizáció:

`${firmwarevr/Beta/}`

Az R100 CSP2.5 donor normalizáció:

`${firmwarevr/b/}`

Ez source-verifikált generációs különbség.

TEST választó:

- `bdinfo rdtest == 1`, vagy
- `/etc/rom_alpha` létezik.

A stock `checkupdate` requestben nincs külön explicit `beta`, `gray`, `canary`, `cohort` mező.

---

# 4. Korábbi R25 OTA boundary eredmények

A korábbi fizikai split/boundary tesztekből:

- `0.0.0` -> 2.4.16 ajánlat
- `1.15.28` -> 2.4.16 ajánlat
- `2.1.1` -> 2.4.16 ajánlat
- `2.4.15` -> 2.4.16 ajánlat
- `2.4.16` régi/jelenlegi/új timestamp variáns -> nincs update
- `2.4.17` -> nincs update
- `9.9.9` -> nincs update

Split test:

- HTTP header CURRENT + JSON OLD -> update offered
- HTTP header OLD + JSON CURRENT -> no update

Ebből már korábban az látszott, hogy a JSON semantic firmware version sokkal fontosabb a selectionben, mint a raw HTTP header.

Nyelv/full probe (`auto`, `en`, `zh-cn`) nem változtatta meg a selectiont.

Beta spelling próbák a 2.4.16 környékén nem nyitottak új ágat.

---

# 5. Négy független stock 2.4.16 OTA objektum

Korábbi ellenőrzésben négy külön OTA publication objektum került elő.

i18n TEST:

`https://d1jvyy13vm72kv.cloudfront.net/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_48004.bin`

i18n PROD:

`https://d1jvyy13vm72kv.cloudfront.net/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_20729.bin`

CN TEST:

`https://cn-cf.cudycloud.com/mytest/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_95221.bin`

CN PROD:

`https://cn-cf.cudycloud.com/device/upgrade/upgrade_LT500V2-R25-2.4.16-20250804-150319-flash_30196.bin`

Mind a négy:

- size: `12,124,315` byte
- MD5: `dc9ac8a6cae00621ab42536e35701d6a`
- SHA-256: `57aed945a9f485d178d73a844e420fc2b441e60821e243d3d19d07dd4a3143d6`
- byte-identical a retail stock 2.4.16 image-dzsel.

A TEST és PROD metadata időbélyege különbözik, ami valódi staging -> production pipeline-ra utal, de a staged payload ugyanaz a retail 2.4.16.

---

# 6. Probe-81 / 82 – lowercase-b CSP2.5 lead

Az R100 CSP2.5 source-ban a firmware versionből a kliens kiszedi a lowercase `b` suffixet. Cudy saját CSP2.5 kommentjeiben más modellekből valódi `2.5.0b` és `2.5.28b` beta tokenek kerültek elő.

Ez alapján Probe-81 kizárólag evidence-backed formákat próbált:

- raw `2.5.0b`, JSON `2.5.0`
- raw `2.5.0b`, JSON `2.5.0b`

Eredmény:

- mindkét exact shape: firmware `{}`
- pozitív kontroll továbbra is működött.

Következtetés:

`TARGET_VERIFIED NEGATIVE` csak ezekre az exact request shape-ekre.

Nem bizonyítja, hogy R25 CSP2.5 beta nem létezik.

Fontos döntés már ekkor:

> ne spray-eljünk random `2.5.xb` értékeket.

---

# 7. Exact build hunt / public web / support csatorna

## 7.1 Public állapot

A Cudy LT500/LT500D 3.0 publikus download oldalain a vizsgált időpontban továbbra is a következő volt a legújabb R25 firmware:

`LT500V2-R25-2.4.16-20250804-150319-flash.zip`

A public CSP2.5 support plan tartalmazta az LT500 3.0 és LT500D 3.0 modellt, de publikus R25 2.5.x artifact nem jelent meg.

Célzott keresések:

- `LT500V2-R25-2.5`
- `LT500V2-R25 CSP2.5`
- `upgrade_LT500V2-R25`
- Shopify `/cdn/shop/files/LT500V2-R25-2.5...`
- CloudFront exact filename pattern
- GitHub code
- Cudy support comments
- 4PDA indexek

nem adtak exact R25 CSP2.5 fájlnevet vagy URL-t.

## 7.2 Support/private distribution

A private support channel viszont **VERIFIED gyakorlat**.

Rögzített példák LT500/LT500D vonalon:

- 2024-08-26: LT500 V1 user -> support szerint firmware emailben elküldve.
- 2024-09-23: LT500 V2 / 2.1.1 issue -> support emailben kontaktált.
- 2025-04-29: LT500D cellular issue -> support solutions emailben.
- 2025-07-28: explicit beta firmware kérés T-Mobile problémára -> support emailes megoldás.
- 2026-02-03: LT500 V1 firmware kérés -> technikai support emailben kontaktál.

CSP2.5 platform comment flow:

- 2026-08-14: bizonyos modellekhez CSP2.5 beta firmware support emailben.
- 2026-08-17: más modellekhez explicit válasz, hogy nincs CSP2.5 beta.

Következtetés:

- LT500/LT500D private support delivery: `VERIFIED`
- CSP2.5 private support delivery más modelleken: `VERIFIED`
- exact R25 CSP2.5 support build: `UNKNOWN / NOT FOUND`

## 7.3 4PDA korrekció

A user által korábban adott:

`showtopic=1104378`

indexelve WR1300/WR1300S témának látszik, nem LT500-specifikus firmware threadnek. Exact post evidence nélkül nem használható LT500 forrásként.

A `showtopic=1109448` relevánsabb Cudy LTE discussion, de exact R25 CSP2.5 leak ott sem lett bizonyítva.

---

# 8. Modem-family blocker hipotézis lezárása

A target modem:

`EC200AELV1LAR02A03M08`

Az R100 CSP2.5 userspace továbbra is tartalmaz supportot többek közt:

- `EC200*`
- `EC200AEU*`
- `EC200AEL*`
- `SLM770A*`

és megvannak a Quectel/Meig útvonalak (`quectel.sh`, `quectel2.sh`, `quectel-5g.sh`, `meig.sh`, `4gup.sh`).

Ezért a leegyszerűsített hipotézis:

> „CSP2.5 azért nincs R25-re, mert az új userspace már nem támogatja az R25 modemcsaládját”

forrás alapján nem tartható.

Classification:

`SOURCE_VERIFIED_NEGATIVE` erre az egyszerű blocker hipotézisre.

A valós release blocker továbbra is `UNKNOWN`.

---

# 9. R25 cloud/App firmware control plane – fontos statikus RE

Stock R25-ben több firmware-control útvonal van.

## 9.1 Path A – normál OTA

`/sbin/autoupgrade`
-> `/device/v1/auth`
-> `/device/v1/checkupdate`
-> `/etc/fwinfo.json`
-> download
-> local upgrade

## 9.2 Path B – Cudy App / remote cloud

Forrás-ellenőrzött high-level chain:

`Cudy App/cloud binding`
-> `cmsd.cloud.enabled=1`
-> `/usr/sbin/cmsd-control`
-> `/device/v1/iot/getall` + cert provisioning
-> remote MQTT topics
-> `/usr/sbin/cmsd`
-> `msgtype=apprpc`
-> `/usr/lib/lua/cmsd/apprpc.lua`
-> `luci.app.resolve(method)`
-> `luci.jsonrpc.proxy(...)`
-> `luci.apprpc.system.*`
-> `/sbin/autoupgrade`

A `luci.apprpc.system` firmware függvényei:

- `upgrade_check`
- `upgrade_fwinfo`
- `upgrade_download`
- `upgrade_checkstatus`
- `upgrade`
- `bind_token`
- `bind_success`

`bind_success`:

- `cmsd.cloud.enabled=1`
- UCI commit
- cmsd restart

Stock `/etc/config/cmsd`:

`config mqtt cloud`
`option enabled '0'`

A remote cloud instance tehát immutable stockban disabled, binding után runtime engedélyezhető.

## 9.3 Path C – cmagent local mesh/control firmware handler

`/usr/lib/lua/cmagent/router/upgrade.lua`

képes:

- autoupgrade check
- download
- upgrade

és van közvetlen:

`url + md5 + tries`
-> `/usr/sbin/firmware.sh`
-> `/tmp/firmware.img`
-> MD5 check
-> `sysupgrade -T`
-> `sysupgrade`

De stock R25 cmagent broker:

`127.0.0.1:8883`

Ezért ez source szerint lokális mesh/control plane; **nem bizonyított remote support-beta channel**.

Fontos különválasztás:

`cmsd != cmagent`.

---

# 10. Probe-90, 91, 92

## 10.1 Probe-90

A 90-es probe első target futása hibás volt:

`set -u` + régi stock `jshn.sh` együtt `JSON_PREFIX: parameter not set` hibát okozott.

Ez nem server eredmény, hanem probe implementation bug.

## 10.2 Probe-91

A bug javítása köztes verzióban történt; nem ez a végső evidence checkpoint.

## 10.3 Probe-92 – döntő stock target kontroll

Fizikai R25 stock állapot:

- `rom_version=2.4.16-20250804-150319`
- `devtype=R25`
- `region=EU`
- `country=DE`
- `checkuuid=OK`

Local cloud/App state:

- `cmsd.cloud.enabled=0`
- `cmsd.cloud.certvr_present=0`
- `cmsd.cloud.cid_present=0`
- `cmsd.cloud.mac_present=0`
- `/etc/token` present, size 32
- `/etc/cmsd` absent
- `/tmp/cmsd` absent
- `/tmp/.timeclock` present
- `cmsd_process=STOPPED`
- `cmagent_process=RUNNING`
- `cmsd_ubus_object=ABSENT`
- `cmagent_router_ubus=PRESENT`

A probe semmilyen identity secretet nem nyomtatott ki.

### TEST

AUTH:

`ret=0`, HTTP 200.

CURRENT 2.4.16:

`{"data":{"firmware":{},"module":{}},"msg":"","ret":0}`

OLD 2.1.1 pozitív kontroll:

- `vr = 2.4.16-20250804-150319`
- `dtime = 1754294870`
- URL = TEST `/mytest/` stock object
- MD5 = `dc9ac8a6cae00621ab42536e35701d6a`
- message = `TOM自动化测试固件发布0804`
- `force=false`

### PROD

AUTH:

`ret=0`, HTTP 200.

CURRENT 2.4.16:

firmware `{}`.

OLD 2.1.1 pozitív kontroll:

- `vr = 2.4.16-20250804-150319`
- `dtime = 1754527466`
- URL = PROD `/device/upgrade/` stock object
- MD5 = `dc9ac8a6cae00621ab42536e35701d6a`
- message = `Fix some bugs`
- `force=false`

Interpretáció:

- auth/request path valós és működik;
- TEST és PROD külön publication metadata;
- current R25 stocknak nincs újabb ajánlat;
- old-version control visszaadja a stock 2.4.16-ot.

---

# 11. Live R25 flash capture – Audit-95

A physical target current-running firmware source bundle:

`RE-LT500D-R25-CURRENT-FIRMWARE-SOURCE.tar.gz`

SHA-256:

`c8bbaa61703198551ace0c2da3e680e0f1e4fdd59fd7b221caab708e32fa0a94`

A dumpból kiderült, hogy a korábbi engineering target nem egyszerűen stock SquashFS + overlay volt, hanem:

`stock R25 kernel/uImage`
+
`reconstructed engineering SquashFS`
+
`persistent JFFS2 overlay`

Current raw MTD firmware SHA-256:

`0508aceca5e394596902fb4cec54d770d55d4eaf1bbb42be79ca5e4cca7e8d7b`

Current uImage+payload SHA-256:

`980cf67797a75dac702218f48beebb92fd0343542ddaa5325db3c850e7d22b22`

uImage:

- magic `0x27051956`
- name `R25`
- payload `2456845` bytes
- SquashFS start `0x257d4d`
- build `2025-08-04 07:04:59 UTC`
- LZMA / MIPS

Current SquashFS:

- 2646 inodes
- mkfs timestamp `2026-09-22 15:31:45 UTC`
- XZ
- block size 512 KiB
- bytes_used `8,910,370`

Stock rootfs reference:

- 256 KiB block
- bytes_used `9,120,182`

Unambiguous baked modifications:

- `/etc/pingcheck/online.d/99-autoupgrade` -> report suppression / `true`
- `/lib/preinit/99_00_console` -> debug gate bypass
- `/lib/upgrade/platform.sh` -> engineering sysupgrade unlock
- `/usr/lib/lua/luci/view/themes/bootstrap/sysauth.htm` -> username visibility

A core OTA/cloud fájlok viszont a korábbi live dumpban stock-identikusak voltak, vagyis Probe-92 ténylegesen a gyári R25 OTA protokollt mérte, nem egy átírt OpenCudy OTA klienst.

Live residue scan:

- `2.5.0b` NOT FOUND
- `LT500V2-R25-2.5*` NOT FOUND
- `allow_ver` NOT FOUND
- `/device/v1/activate` NOT FOUND a stock/R25 core lineage-ban
- nincs exact R25 CSP2.5 residue

Ez a szál később szándékosan le lett állítva, mert elvitte a fókuszt az exact CSP2.5 artifact huntból.

---

# 12. Hybrid CSP2.5 target – új állapot

A user később egy olyan fizikai állapotot hozott létre, ahol az LT500D V2.0 targeten CSP2.5 UI/userspace fut.

Fizikai parancsok:

`uci -q get system.board.rom`
-> `R25`

`cat /etc/rom_version`
-> `2.5.12-20260518-234632`

`bdinfo checkuuid`
-> `OK`

Ez kulcsfontosságú, de az evidence-label helyes megfogalmazása:

> **TARGET_VERIFIED: fizikai R25 board identity + CSP2.5 2.5.12 hybrid userspace/version state.**

Nem:

> „official R25 2.5.12 firmware”.

Utóbbi továbbra sem bizonyított.

---

# 13. Probe-96 – version-chain próbák hybrid targeten

Probe-96 megtartotta:

- real `devtype=R25`
- real HTTP `vr=2.5.12-20260518-234632`
- valós FUUID/MAC/HMAC auth identitást
- JSON `firmwarevr` változtatása בלבד

Tesztelt semantic értékek:

- 2.4.16
- 2.5.0
- 2.5.4
- 2.5.6
- 2.5.7
- 2.5.8
- 2.5.9
- 2.5.10
- 2.5.11
- 2.5.12
- 2.5.22
- 2.5.25

TEST és PROD authentication: OK.

Minden tesztelt értékre firmware `{}`.

Fontos hiba a probe-designban:

A 96-osból kimaradt az exact teljes OLD pozitív kontroll (`2.1.1-20240419-090237`), ezért az all-empty eredmény önmagában nem volt elég a selection mechanika végleges lezárásához.

Ez vezetett Probe-97-hez.

---

# 14. Probe-97 – cross-field döntő kísérlet

Exact build stringek:

- OLD = `2.1.1-20240419-090237`
- STOCK = `2.4.16-20250804-150319`
- REAL = `2.5.12-20260518-234632`

A probe TEST és PROD alatt 3 x 3 mátrixot futtatott:

HTTP `vr` header:

- OLD
- STOCK
- REAL

JSON `firmwarevr`:

- OLD
- STOCK
- REAL

Minden auth variáns sikeres volt.

## 14.1 TEST eredmény

Minden HTTP header mellett:

JSON OLD:

-> stock R25 2.4.16 firmware object.

JSON STOCK:

-> `{}`.

JSON REAL:

-> `{}`.

TEST object:

- `vr=2.4.16-20250804-150319`
- `dtime=1754294870`
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`
- `force=false`
- `/mytest/` publication namespace

## 14.2 PROD eredmény

Ugyanez:

JSON OLD:

-> stock R25 2.4.16.

JSON STOCK:

-> `{}`.

JSON REAL:

-> `{}`.

PROD object:

- `vr=2.4.16-20250804-150319`
- `dtime=1754527466`
- MD5 `dc9ac8a6cae00621ab42536e35701d6a`
- `force=false`
- `/device/upgrade/` namespace

## 14.3 Döntő következtetés

A tesztelt R25 identityn:

> **a HTTP `vr` headernek nincs megfigyelhető firmware-selection hatása; a JSON `firmwarevr` az authoritative tested selection field.**

A hybrid `2.5.12` HTTP header:

- nem blokkolja a known-old -> 2.4.16 választ;
- nem unlockol új firmware-t;
- stock/current firmwarevr mellett nem ad 2.5.x ajánlatot.

Ezért:

> **random `firmwarevr` enumerationt nem érdemes tovább folytatni.**

A normál TEST/PROD R25 channel jelenlegi eszközidentitásnak nem kínál 2.4.16-nál újabb firmware-t.

---

# 15. R100 CSP2.5 activation – statikus RE

A user egy új „csontot” adott: `/usr/sbin/activate` shell scriptet.

Korábbi static RE alapján ez byte-for-byte egyezik az R100 CSP2.5 2.5.12 donor scriptjével.

`/usr/sbin/activate` SHA-256:

`a0dbc74614d8215106eae442ec4e6305aa49ebd8fb8e399fb9e1fff557797d93`

R100 init:

`/etc/init.d/activate`

SHA-256:

`f3eead49944df74dc83966d9e2ef190f6749768c2548e85b2532db6fc7b49193`

Enabled boot link:

`/etc/rc.d/S99activate -> ../init.d/activate`

`START=99`.

## 15.1 Init gate

A service csak akkor indul, ha:

1. `bdinfo checkuuid == OK`
2. van non-empty serial
3. country nem `CN`
4. `system.@system[0].activate` még nincs beállítva

## 15.2 Endpoint választás

Ha `/etc/rom_alpha` létezik:

`https://event-test.cudycloud.com/device/v1/activate`

különben:

`https://event-i18n.cudycloud.com/device/v1/activate`

HTTPS akkor, ha `/usr/bin/curl` executable.

Ez fontos bizonyíték, hogy `/etc/rom_alpha` szélesebb Cudy cloud test-environment selector, nem pusztán OTA switch.

## 15.3 Payload

A script:

- beolvassa `bdinfo sn`
- beolvassa `/etc/rom_version`
- egy hardcoded 32-byte ASCII secretet hex key-vé alakít
- az SN-t `crypt -e -n -l 256 -k "$KEY"` úton titkosítja
- vár `/tmp/.timeclock`-ra
- utána `sleep 86400`
- generál `dtime`
- generál nonce-t 8 random byte MD5-jéből
- sign = MD5(`serial + nonce + dtime + VR + hardcoded suffix`)
- POST mezők:
  - `data`
  - `nonce`
  - `vr`
  - `dtime`
  - `sign`

Nincs külön visible `devtype` vagy FUUID mező ebben a shell requestben.

Up to 3 network attempt.

Ha nem üres response érkezik:

- JSON parse
- `ret==0` esetén:
  - `uci set system.@system[0].activate='1'`
  - `uci commit system`
- ezután break.

Fontos nuance:

Ha a server response non-empty, de `ret != 0`, a process akkor is kilép az adott futásból, viszont `activate=1` nem íródik. Következő bootkor újrapróbálhatja.

## 15.4 Crypt binary generációs változás

R100 CSP2.5 `/usr/bin/crypt`:

- size 12339
- SHA-256 `9e3f84906c5ff11f15cec3df27a1cb1f1d309511b63938f2870ead267bd2961b`

R25 2.4.16 `/usr/bin/crypt`:

- size 8243
- SHA-256 `cecd85b3162678612d713882468be37229964bf1af0de9dc539bb31a5f74a3b5`

R100 új CLI opciókat tartalmaz a normal AES / key length / key / IV kezelésre.

Az activation feature és a crypt helper bővülése erősen kapcsolódó generációs változás.

---

# 16. Activation és OTA kapcsolat – mi bizonyított / mi nem

Bizonyított:

- activation authentic serial-derived payloadot küld;
- exact `/etc/rom_version` értéket küld `vr`-ként;
- server-visible device/version activation eventet hoz létre;
- R100 local OTA code nem olvassa közvetlenül a `system.@system[0].activate` flaget;
- OTA auth/checkupdate külön API family;
- visible activation shell request nem küld külön devtype/FUUID mezőt.

NEM bizonyított:

- activation vezérli az OTA eligibilityt;
- activation beta cohortba enrollol;
- checkupdate activation DB-t használ;
- R25 beta activationt igényel;
- synthetic version activationből R25 beta lenne felfedhető.

Classification:

`ARCHITECTURAL_LEAD / SERVER_SIDE_RELATION_UNKNOWN`

Fontos korábbi döntés:

> activationt nem indítunk kézzel synthetic R25 state-tel, mert ez server-side write/event lenne.

---

# 17. A nagy fordulat: az activation most TERMÉSZETESEN fut a hybrid R25-ön

A hybrid target vizsgálata:

`ls -l /etc/init.d/activate /etc/rc.d/S99activate`

kimutatta:

- `/etc/init.d/activate` executable
- `/etc/rc.d/S99activate -> ../init.d/activate`

`uci -q get system.@system[0].activate`

-> üres.

`ps | grep '[a]ctivate'`

-> `/bin/sh /usr/sbin/activate` futó process.

A korábbi pillanatban:

- activate PID: `4886`
- uptime: `7697` sec (~2h08m)
- `/tmp/.timeclock` present
- `.timeclock` timestamp: `Sep 28 01:37`
- activate flag: empty

Ez azt jelenti, hogy a vendor saját init service-e teljesen természetesen elindult a hybrid R25 userspace-en.

Ez **nem kézi synthetic activation trigger**.

---

# 18. Utolsó runtime vizsgálat és a terminál-paste incidens

A user megpróbálta lefuttatni a read-only process-state parancsokat, de a terminálba nem csak a parancsok, hanem korábbi prompt/output sorok is vissza lettek másolva, például:

`root@LT500D:~# ...`

és már kiírt output sorok.

Ennek következménye sok ilyen hiba lett:

- `-ash: root@LT500D:~#: not found`
- `-ash: ===: not found`
- output sorok parancsként való értelmezése
- malformed `curl` próbálkozás blank argumenttel
- malformed `wget` próbálkozás (`Failed to allocate uclient context`)

A fontos biztonsági rész:

- a malformed `curl` nem kapott valid célt;
- a malformed `wget` nem hajtotta végre az intended requestet;
- a bemásolt `uci set ... activate='1'` sor előtt ott volt a grep sorszám prefix (`45:`), ezért shellben `45:` command-not-found lett; **nem bizonyított UCI írás történt**;
- nincs jel arra, hogy firmware download vagy sysupgrade történt volna.

A zajos kimenetből viszont egy fontos valódi process-lista sor kiolvasható volt:

`11510 root 1184 S sleep 86400`

és egy másik, nem activation-specifikusan azonosított:

`16564 root 1184 S sleep 2743`

A `sleep 86400` pontosan egyezik az activation script gyári várakozásával.

Ez erős runtime corroboration arra, hogy az activation process a 24 órás delay fázisban van/volt.

A parent shell `wchan=do_wait` szintén kompatibilis a child sleepre váró ash process-szel.

Az előző `/proc/.../children` üres eredményt nem szabad abszolút cáfolatként kezelni, mert a későbbi `ps` explicit mutatta a `sleep 86400` processzt; PID/parent visibility és a zajos paste miatt az első próbából nem volt tiszta process-tree capture.

---

# 19. Aktiváció várható időpont és következő megfigyelés

A `.timeclock` timestamp:

`Sep 28 01:37`

A source szerint utána jön:

`sleep 86400`

Ez alapján a várható activation POST hozzávetőleg:

**2026-09-29 01:37 helyi idő**

Feltételek:

- a router nem rebootol;
- a process nem lett kill-elve;
- a sleep közvetlenül a `.timeclock` megjelenése után indult.

Ez becslés, nem exact scheduler timestamp.

A beszélgetés lezárásakor ezért a legfontosabb operációs szabály:

> **NE rebootold a routert, ha meg akarod figyelni a természetes activation cycle végét.**

Reboot esetén az üres activation flag miatt az init gate újraindíthatja a teljes delayed lifecycle-t.

---

# 20. Activation után végrehajtandó minimális read-only ellenőrzés

Első lépés csak állapotlekérés legyen.

A következő chatben a parancsokat **csak a code blockból másold**, a `root@LT500D...#` promptot és a korábbi outputot soha ne másold vissza.

Javasolt minimális ellenőrzés:
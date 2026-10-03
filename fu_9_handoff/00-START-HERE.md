# Firmware Unlock 9 — START HERE

**Dátum:** 2026-10-03  
**Előd:** Firmware Unlock 8  
**Új kolléga neve:** Firmware Unlock 9  
**Nyelv:** magyar  
**Projekt:** Cudy LT500D / OpenCudy + új Belkin F9K1103 v1 OpenCudy/LEDE port szakág

## 1. Azonnali prioritás

A beszélgetés végén a felhasználó egyértelműen átpriorizálta a munkát.

**P0 elsődleges feladat:**
> A Belkin F9K1103 v1 számára készült natív LEDE 17.01.5 port buildjét kell működőképessé és reprodukálhatóvá tenni.

A Cudy WebGUI/userspace Belkinre portolása addig **PARKED**, amíg nincs sikeres, statikusan validált F9K1103 LEDE 17.01.5 image.

## 2. Kritikus Belkin-korrekció

A fizikai Belkin F9K1103 v1-en jelenleg futó OpenWrt **nem natív F9K1103 target image**.

A felhasználó által ténylegesen használt referencia:
`openwrt-19.07.0-ramips-rt3883-belkin_f9k1109v1-squashfs-sysupgrade.bin`

A jelenlegi értelmezés:
- a fizikai hardver: **Belkin F9K1103 v1 / N750 DB**;
- a működő OpenWrt referencia: **F9K1109 v1 OpenWrt 19.07.0 image**;
- ez bizonyítja, hogy az F9K1109 platformleírás erős hardver-reference;
- **nem bizonyítja**, hogy az F9K1103 és F9K1109 minden board-részlete azonos;
- az új LEDE port célja saját F9K1103 board target, nem donor image átnevezés.

## 3. Jelenlegi LEDE-port

Repo:
`diablomike20/Belkin-F9K1103-Firmware`

Fontos könyvtár:
`firmware/f9k1103-lede-17.01.5/`

Már létezik:
- `F9K1103.dts`;
- saját LEDE build script;
- RT3883 target;
- 8 MiB SPI NOR layout;
- RTL8367R-VB;
- LAN 0..3 / WAN 4 / CPU 5 switch mapping;
- HW_WAN_MAC / HW_LAN_MAC kezelés;
- WMAC factory + 0x0000;
- PCI RT3091/3092 factory + 0x8000;
- USB;
- LED/button GPIO-k;
- firmware partition 0x050000 + 0x7a0000;
- `N750F9K1103VB` uImage név;
- sysupgrade támogatási backport;
- host-glibc kompatibilitási patchek.

**Állapot:** PORT-WIP. Build még nem SUCCESS. Physical boot nincs igazolva.

## 4. Legutóbbi build — innen folytasd

Workflow:
`Build F9K1103 LEDE 17.01.5`

Run:
`36959975523`

Job:
`110691296857`

Branch:
`lede-17.01.5-fix-board-token`

Head:
`3ef3cb7f6291d6b91ed09cf2a1cd15ece5fd5a86`

Result:
`completed / failure`

### Fontos előrelépés

A korábbi lzma-loader PLATFORM/board token hiba **már nem az aktuális blocker**.

A logban sikeresen fordul:
- `head.o`
- `loader.o`
- `cache.o`
- `board-ralink.o`
- `printf.o`
- `LzmaDecode.o`
- `data.o`

A linker is elkészíti a `loader` fájlt.

### Aktuális konkrét blocker

Az `objcopy` lépés bukik:

```
mipsel-openwrt-linux-musl-objcopy:
Warning: Writing section '.text' to huge (ie negative) file offset 0xffffffff81800000.
loader.bin[.text]: File truncated
```

A következő kolléga **ne menjen vissza** a régi `PLATFORM="ralink"` hibához. Az már továbbhaladt.

Első RE/build feladat:
1. hasonlítsa össze a LEDE 17.01.5 és OpenWrt 19.07 ramips lzma-loader link/objcopy pipeline-t;
2. inspect `readelf -S/-l` a loaderen közvetlenül objcopy előtt;
3. minimal backport/fix a magas `0x81800000` VMA bináris kivonására;
4. rebuild;
5. csak SUCCESS után statikus image-validáció.

## 5. Miért LEDE 17.01.5 az elsődleges?

A Cudy donor audit alapján az LT500D R25 és több közeli Cudy stock firmware szintén LEDE 17.01.5 userspace-re épül.

A Belkin hardver-reference és a Cudy userspace-donor tehát külön szerepet kap:

```
F9K1109/OpenWrt 19.x  -> hardver-reference
F9K1103 saját DTS     -> board truth
LEDE 17.01.5          -> elsődleges runtime base
WR1200 V2 / LT500D    -> Cudy UI/userspace donor
```

## 6. R25/OpenCudy ág

Az LT500D R25 ág **nem törlődött és nem lett lezárva**. Nagyon sok fizikailag és statikusan bizonyított eredménye van. A teljes állapot a master dokumentációban van.

A fontos szabály:
- ne keverd össze a Belkin LEDE build evidence-et az R25 target evidence-dzsel;
- ne nevezd Belkin truthnak a Cudy donor viselkedést;
- ne nevezd R25 truthnak a P2/C200P/Cudy más-model donor eredményt.

## 7. Első olvasási sorrend Firmware Unlock 9 számára

1. `00-START-HERE.md`
2. `Firmware Unlock 9.txt`
3. `01-FU9-MASTER-DOCUMENTATION.md`
4. `02-BELKIN-LEDE-17.01.5-PRIMARY-MISSION.md`
5. `03-CURRENT-STATE-MATRIX.csv`
6. `04-FIRMWARE-INVENTORY.csv`
7. `05-ARTIFACT-AND-SOURCE-INDEX.md`
8. `06-DO-NOT-REPEAT-AND-SAFETY.md`
9. `source-extracts/`
10. `raw-evidence/`

## 8. Felhasználói munkastílus

A felhasználó magyarul kommunikál.

Ha azt írja:
- „hajrá”
- „mehet”
- „csináld”
- „folytasd”

akkor **dolgozz azonnal**, ne adj újabb általános tervet.

A felhasználó kifejezetten nem szereti:
- a fölösleges várakozást;
- ugyanazon RE újrakezdését;
- olyan állítást, hogy valami kész, amikor még nincs kész;
- a target/donor/static evidence összemosását.

Hosszú feladatoknál kevés chat-update legyen; a build/RE munkát inkább GitHub Actions vigye, hogy a chat időkorlát ne akadályozza.

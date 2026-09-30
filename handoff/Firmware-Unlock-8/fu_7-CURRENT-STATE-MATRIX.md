# Current state matrix

| Area | Status | Notes |
|---|---|---|
| Physical LT500D V2 / R25 identity | TARGET_VERIFIED | authoritative |
| Stock R25 2.4.16 | SOURCE_VERIFIED | canonical stock |
| 4G usb0 | TARGET + LIFECYCLE VERIFIED | preserve |
| Dropbear local unlock | TARGET_VERIFIED | local startup gate bypass |
| Telnet local unlock | TARGET_VERIFIED | engineering policy |
| Normal global bdinfo dbg | FAIL / retail | do not globally forge |
| Factory Debug lifecycle | TARGET + LIFECYCLE VERIFIED | enable/disable baseline restoration |
| H09 OPKG | TARGET + LIFECYCLE VERIFIED | frozen |
| C27 runtime package | TARGET_VERIFIED | current proven cumulative runtime lineage |
| Candidate47 image format | TARGET_VERIFIED | stock GUI / sysupgrade -T |
| Candidate47 actual boot | TARGET_REQUIRED | not done |
| H11 branding | PARTIAL | 3 known misses |
| Developer V4 CLEAN-06 | proven branch | cleaned Developer lineage |
| IPTV Hybrid-58 | STATIC_VERIFIED / TARGET_REQUIRED | preserve 4G |
| V69 Truth-04 | SOURCE/STATIC integration truth | separate OpenWrt23 lineage |
| R100 CSP2.5 | SOURCE_VERIFIED donor | not official R25 |
| R25 CSP2.5 hybrid | TARGET_VERIFIED lab state | not official artifact |
| Exact R25 CSP2.5 firmware | UNKNOWN / NOT FOUND | active hunt |
| C200P R74 2.5.14 | SOURCE + EMULATOR VERIFIED | unlisted/internal inference |
| C200P debug/developer label | NOT PROVEN | deep audit pending |
| P2 2.4.29b | SOURCE_VERIFIED beta payload | donor |
| P2 rom_research | SOURCE_VERIFIED marker | consumer not proven |
| RG500 A09 engineering modes | SOURCE_VERIFIED | modem donor |
| Candidate-02 | STATIC_VERIFIED / TARGET_UNVERIFIED | no boot claim |
| CLEAN-MERGE-03 | prepared, not installed | no runtime credit |
| Captive Portal Candidate-03 | DID NOT INSTALL | no backup; exact failure unknown |

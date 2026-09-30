# fu_7 — Project source catalog

This is a navigation catalog for Firmware Unlock 8. It is not a replacement for the actual Project Sources.

## Major conversation/source dump families

Firmware unlock / physical target:
- Firmware-Unlock.txt
- Firmware-Unlock_2.txt
- Firmware-Unlock_3.txt

Integration / Boss:
- Boss.txt
- Boss_2.txt
- Folytatás várakozás nélkül.txt

Reverse Engineering:
- RE-Kollega.txt

Emulator / web forensics:
- EM-Kollega.txt

Frontend / Workspace:
- Frontend fejlesztési frissítés.txt
- FE_2-Kollega.txt
- WS-related handoffs and V69 frontend bundles

Donor / firmware hunt:
- Cudy donor firmwareek felkutatása.txt
- Belkin N750 OpenWrt.txt
- FU6/FU7 firmware hunt artifacts and GitHub Actions outputs

## Important standalone project documents

- fu_6-PROJECT-MASTER-DOCUMENTATION
- fu_6-FIRMWARE-UNLOCK-6-DEEP-HANDOFF
- RE-OPENCUDY-LT500D-R25-FULL-DOCUMENTATION-24
- RE-OPENCUDY-COMPLETE-COLLECTOR-80
- RE-SUCCESSOR-CHAT-PROMPT-24
- RE-R25-RAW-CANDIDATE-47-VALIDATION
- RE-OPENCUDY-PROJECT-READY-STATE-87
- current FU7 handoff package

## Source precedence

When different historical files disagree:

1. newest physical TARGET_VERIFIED evidence wins for target state;
2. newer explicit user decision wins over older intermediate design decisions;
3. source-level donor evidence remains valid for its own donor/version but must not overwrite physical R25 truth;
4. V69/OpenWrt23 frontend truth is separate from the later physical C27 engineering runtime lineage;
5. historical drafts remain regression/evidence references, not automatic current baselines.

## Common historical contradictions already resolved

- Technical-looking donor pages are not automatically Developer features.
- Kernel/Wireless logs and charts may be normal donor routes.
- OPKG belongs under Advanced/System, not Developer.
- 4G changes were not necessary unlock deltas.
- hcshd disable was not an unlock requirement; stock startup was later restored.
- CWMP exclusion does not imply disabling every Cudy management/cloud component.
- C200P 2.5.14 is internal/unlisted strongly inferred, but not proven developer/debug.
- R25 hybrid 2.5.12 is not proof of an official R25 2.5.12 artifact.
- Candidate47 format validation is not a boot test.
- Candidate-03 did not install and has no backup.

## Retrieval rule for successor

Before asking the user to re-upload or repeat old work:
search Project Sources for the exact artifact/file/chat family first.

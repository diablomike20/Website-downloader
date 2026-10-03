# RE-LT500V2-R25 — PATCH MANIFEST PREBUILD 06

Source of truth: `squashfs-root-LT500V2-R25-2.4.16-20250804-150319-flash.zip`.
Target: Cudy LT500V2 R25, LEDE 17.01.5 / Cudy 2.4.16.

## Corrected hidden-route classification

The following routes are **normal Cudy child/detail routes**, not Developer Features:
- `admin/system/status/dmesg` — Kernel Log, part of System Status.
- `admin/network/wireless/chart` — Wireless chart child route + polling data endpoint.
- `admin/network/wireless/probelist` — Wireless probe-list child route.
- `admin/network/wireless/logread` — Wireless log child route.

The `luci.gui` `hidden` classification therefore does not by itself mean developer-only. These four stay in their normal Cudy route chains and MUST NOT be gated by the Developer Features switch.

## Proven developer/engineering functions

- `admin/system/terminal`
  - controller/model exists;
  - CBI executes entered commands with `luci.util.exec`;
  - explicitly denied by `luci.forbidden`;
  - strong retail-hidden engineering function.
- `admin/system/sandbox` (Telnet)
  - controller/model exists;
  - CBI changes sandbox/Telnet setting and reloads `/etc/init.d/telnet`;
  - present in generic description but omitted from the R25 normal GUI layout;
  - retain as Developer Features candidate.

Future UI contract remains:
`Advanced Settings -> System -> Developer Features`, default OFF, UCI-persistent, factory reset OFF. It controls visibility/enablement only and MUST NOT set `bdinfo dbg`.

## Build-now scope: working engineering image first

### Root / service access
- Remove Dropbear `bdinfo dbg` start gate.
- Remove Telnet `bdinfo dbg` start gate for recovery/testing build.
- Keep password authentication; do not force global Cudy debug mode.
- Install a known temporary root password and prevent firstboot from replacing it with SHA256(FUUID||HMAC).
- Keep normal `/bin/login` semantics for console; expose askconsole without passwordless debug-shell bypass.

### Web login
- Default `luci.main.showuser=1`.
- Force the username/password labels and username field to remain visible even if an old preserved overlay still has `showuser=0`.
- Keep Cudy `admin` web authentication semantics unchanged.

### OTA
- Disable cron-created automatic `autoupgrade` job.
- Disable `/etc/pingcheck/online.d/99-autoupgrade` automatic `autoupgrade report` trigger.
- Preserve manual/local firmware update UI and binaries.

### CWMP / TR-069
- Preserve package/config/UI for reversibility.
- Stock default remains `cwmp.info.enable=off`.
- Neutralize `/tmp/vendor_spc` logic that writes `cwmp.info.enable=on`.
- With enable remaining OFF, boot/hotplug cannot start the daemon or open the CWMP WAN firewall chains.
- Manual deliberate re-enable remains possible.

### Cudy management stack
- Keep `cmagent`: verified dependencies include mesh/topology and network scripts.
- Keep `cmsd`: init script respects `cmsd.cloud.enabled=0`.
- Keep Mosquitto: Cudy mesh/cmagent uses it; anonymous access is disabled and TLS listener requires client certificate. Do not break it before runtime testing.
- Default-disable `hcshd` by returning before its procd instance starts. Binary remains present for reversibility. Static evidence shows socket/RSA/system/popen behavior, but full protocol RE is explicitly deferred.

### Firmware-update policy
- Standard R25 legacy-uImage sysupgrade is accepted without Cudy OEM RSA.
- OEM full-flash path retains `oem-check`.
- U-Boot HTTP recovery RSA is NOT modified.

## Deferred
- OPKG restoration.
- Full `hcshd` protocol RE.
- U-Boot recovery RSA changes.
- Developer Features UI implementation after the first working target-tested image.
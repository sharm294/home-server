<!--
Copyright (c) 2026 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
-->

# host_vars

Place per-host override files here named after the host as it appears in
`inventory.yml`, e.g. `host_vars/pve1.yml`.

Typical overrides:

```yaml
# host_vars/pve1.yml
lvm_drive: /dev/disk/by-id/ata-SAMSUNG_SSD_123
zfs_drive_1: /dev/disk/by-id/ata-WDC_WD40_AAA
zfs_drive_2: /dev/disk/by-id/ata-WDC_WD40_BBB
default_gateway: 192.168.1.1
```

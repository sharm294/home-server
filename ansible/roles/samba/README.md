<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

Samba role
============

Installs Samba, creates a system user/group, deploys a sensible `smb.conf` and ensures `smbd` is running.

Usage
-----

Include the role in a playbook and override defaults as required. Example:

```yaml
- hosts: proxmox_hosts
  roles:
    - role: samba
      vars:
        samba_password: "supersecret"
```

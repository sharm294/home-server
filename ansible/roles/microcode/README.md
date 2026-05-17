<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

# Microcode Role

This Ansible role installs CPU microcode updates for Intel and AMD processors on Proxmox VE hosts.

## Overview

The microcode role automates the installation of processor microcode updates, which are essential for system stability and security. It:

- Verifies that Proxmox VE is installed
- Detects the CPU vendor (Intel or AMD)
- Downloads and installs the appropriate microcode package
- Cleans up temporary files
- Notifies about required system reboot

## Requirements

- Proxmox VE must be installed
- Internet connectivity to download microcode packages
- Root privileges for package installation

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `microcode_install_intel` | `true` | Enable Intel microcode installation |
| `microcode_install_amd` | `true` | Enable AMD microcode installation |
| `microcode_cache_dir` | `/tmp/microcode` | Directory for microcode package caching |

## Example Usage

```yaml
- name: Configure Proxmox VE
  hosts: pve_hosts
  roles:
    - role: microcode
      vars:
        microcode_install_intel: true
        microcode_install_amd: true
```

## Notes

- A system reboot is required after microcode installation to apply updates
- The role automatically downloads the latest available microcode package from Debian repositories
- Microcode updates are non-interactive when run via Ansible

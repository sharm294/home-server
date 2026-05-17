<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

# Proxmox VE Post-Install Configuration Role

This Ansible role performs post-installation configuration of Proxmox VE, including APT sources and repository setup.

## Overview

The `pve_post_install` role handles version-specific post-installation configuration for Proxmox VE. It:

- Detects the installed Proxmox VE version
- Configures appropriate APT sources based on PVE version
  - **PVE 8.x**: Uses Debian Bookworm sources and legacy .list format
  - **PVE 9.x**: Uses Debian Trixie sources and modern deb822 format
- Manages repository configurations (enterprise, no-subscription, ceph, pvetest)
- Handles migration from legacy sources to deb822 format on PVE 9.x

## Requirements

- Proxmox VE 8.x or 9.x
- Root privileges for APT configuration

## Role Variables

| Variable | Default | Description |
| ---------- | --------- | ------------- |
| `pve_enable_no_subscription` | `true` | Enable pve-no-subscription repository |
| `pve_disable_enterprise` | `true` | Disable pve-enterprise repository |
| `pve_setup_ceph_repos` | `true` | Configure Ceph package repositories |
| `pve_setup_pvetest` | `false` | Add pvetest repository (disabled by default) |

## Supported Versions

- **Proxmox VE 8.0-8.9.x**: Bookworm-based configuration
- **Proxmox VE 9.0-9.1.x**: Trixie-based deb822 format configuration

## Example Usage

```yaml
- name: Configure Proxmox VE
  hosts: pve_hosts
  roles:
    - role: pve_post_install
      vars:
        pve_enable_no_subscription: true
        pve_disable_enterprise: true
        pve_setup_ceph_repos: true
```

## Version-Specific Behavior

### PVE 8.x Behavior

- Sets up Debian Bookworm sources
- Disables non-free firmware warnings
- Configures repository files in .list format

### PVE 9.x Behavior

- Detects existing deb822 sources
- Migrates legacy .list files to .bak backups
- Sets up Debian Trixie sources
- Uses modern deb822 .sources format for all repositories

## Notes

- The role automatically backs up legacy sources before migration
- Repository enablement/disablement is controlled by role variables
- All configuration changes trigger APT cache updates

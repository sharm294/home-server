<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

# Proxmox Host Configuration Roles

This directory contains Ansible roles for configuring Proxmox hosts, creating Debian 13 templates, and provisioning VMs and LXC containers.

## Roles Overview

### networking

Configures the Proxmox host networking, including vmbr0 bridge setup, IP addressing, and DNS configuration.

**Variables:**

- `default_gateway` - Default gateway IP (default: `192.168.0.1`)
- `search_domain` - DNS search domain (default: `home.arpa`)

### proxmox_setup

Installs required Proxmox VE packages and runs community installation scripts.

**Variables:**

- `proxmox_required_packages` - List of packages to install

### debian_template

Creates a Debian 13 cloud-init template VM from official cloud images.

**Variables:**

- `template_vm_id` - VM ID for template (default: `8000`)
- `template_name` - Template name (default: `debian-13-template`)
- `template_memory` - Memory in MB (default: `2048`)
- `template_cores` - CPU cores (default: `2`)
- `template_image_url` - Cloud image URL
- `template_image_filename` - Cloud image filename
- `cloud_user` - Cloud-init user (default: `varunsh`)
- `cloud_password` - Cloud-init password (default: `changeme`)

### vm_instance

Clones the template to create new VMs and configures them.

**Variables:**

- `target_vm_id` - New VM ID (default: `100`)
- `target_name` - New VM name (default: `main`)
- `target_disk_size` - Disk size (default: `50G`)
- `target_additional_tags` - Additional tags for VM

### storage_lvm

Configures LVM storage for Proxmox VMs.

**Variables:**

- `lvm_drive` - Physical drive path
- `lvm_vg_name` - Volume group name (default: `vm`)
- `lvm_thinpool_name` - Thin pool name (default: `vm-thin`)
- `lvm_storage_id` - Proxmox storage ID (default: `local-lvm`)

### storage_zfs

Configures ZFS mirrored storage pools and datasets for NAS functionality.

**Variables:**

- `zfs_pool_name` - ZFS pool name (default: `storage`)
- `zfs_drive_1` - First drive path
- `zfs_drive_2` - Second drive path (for mirroring)

### lxc_container

Creates and configures LXC containers with NAS mounts.

**Variables:**

- `lxc_container_id` - Container ID (default: `1000`)
- `lxc_container_password` - Root password (default: `changeme`)
- `lxc_container_cores` - CPU cores (default: `1`)
- `lxc_container_memory` - Memory in MB (default: `1024`)
- `lxc_nas_user` - NAS admin username (default: `nas_admin`)
- `lxc_nas_group` - NAS group name (default: `nas_users`)
- `lxc_nas_uid` - UID for NAS user (default: `101000`)
- `lxc_nas_gid` - GID for NAS group (default: `110000`)

## Usage

The main playbook [proxmox_host.yml](../proxmox_host.yml) orchestrates all roles. You can run the full playbook:

```bash
ansible-playbook -i inventory.yaml proxmox_host.yml
```

Or run specific roles by using tags or limiting hosts in your playbook.

## Customization

Each role has a `defaults/main.yml` containing default variables. Override these in:

1. Your `group_vars/` or `host_vars/` directories
2. The playbook's `vars:` section
3. Command-line with `-e` flags

Example override:

```bash
ansible-playbook -i inventory.yaml proxmox_host.yml \
  -e "template_memory=4096" \
  -e "target_disk_size=100G"
```

## Notes

- All roles expect to run with `become: true` (sudo)
- Requires `community.general` Ansible collection for Proxmox modules
- Update drive paths and passwords in `vars.yml` or playbook before running
- Some commands check for idempotency by examining exit codes

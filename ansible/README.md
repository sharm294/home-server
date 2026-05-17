<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

# Ansible Playbook for Proxmox Host Configuration

This directory contains an Ansible playbook that replicates the functionality of `src/home_server/configure/proxmox_host.py` using Ansible and the Proxmox community modules.

## Prerequisites

1. Ansible installed on your control machine
2. Proxmox community collection: `ansible-galaxy collection install community.general`
3. Access to the Proxmox host via SSH (for host configuration tasks)
4. Proxmox API access (for VM management tasks)

## Usage

1. Set environment variables for Proxmox API access:

   ```bash
   export PROXMOX_API_HOST=your-proxmox-host
   export PROXMOX_API_USER=root@pam
   export PROXMOX_API_TOKEN_ID=your-token-id
   export PROXMOX_API_TOKEN_SECRET=your-token-secret
   export PROXMOX_NODE=pve
   ```

2. Update the inventory file to point to your Proxmox host. Create an inventory file (e.g., `inventory.ini`):

   ```ini
   [proxmox_host]
   your-proxmox-host ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa
   ```

3. Run the playbook:

   ```bash
   ansible-playbook -i inventory.ini ansible/proxmox_host.yml
   ```

## What it does

The playbook performs the following tasks:

1. Installs required packages on the Proxmox host
2. Removes unnecessary packages
3. Runs installation and configuration scripts
4. Downloads the Debian 13 cloud image
5. Creates a Proxmox VM template from the image
6. Configures the template with cloud-init settings
7. Clones the template to create a new VM
8. Resizes the VM disk
9. Starts the VM

## Variables

You can override default variables by creating a `vars.yml` file or passing them via command line:

- `template_vm_id`: VM ID for the template (default: 8000)
- `template_name`: Name for the template (default: "debian-13-template")
- `storage`: Storage pool (default: "local-lvm")
- `target_vm_id`: VM ID for the cloned VM (default: 100)
- `target_name`: Name for the cloned VM (default: "main")
- `disk_size`: Disk size for the cloned VM (default: "50G")
- And more...

## Security Notes

- The default cloud password is "changeme" - override this securely
- Use API tokens instead of passwords for Proxmox API access
- Ensure SSH keys are properly configured for host access

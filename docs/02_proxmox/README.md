<!--
Copyright (c) 2025 sharm294
SPDX-License-Identifier: MIT
--->

# Proxmox

Proxmox is an open-source server virtualization platform that uses a single web interface to manage virtual machines (KVM) and containers (LXC), offering an enterprise-grade, cost-effective alternative to solutions like VMware for managing servers, storage, and networks.

## Installation

1. Download the [latest Proxmox Virtual Environment (VE) ISO](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/iso).
2. Using [Rufus](https://rufus.ie/en/) or a similar tool for your platform, create a bootable USB using the downloaded ISO.
3. On your server machine, insert the USB and enter the BIOS to boot from the USB. You may need to enable booting from USB and/or disable Secure Boot for this to work.
4. Don't connect your server to the network (yet).

### Proxmox Settings

1. Select `Install Proxmox VE (Graphical)`
2. Read and accept the EULA
3. Select the disk to install Proxmox onto. You can also change the file system using `Options` if you'd like. The default is `ext4`.
4. Select your location, time zone and keyboard layout
5. Select the root password and enter an email address (for notifications to the system admin)
6. Configure the network settings.
    a) For hostname (FQDN), you can enter something like `pve.<your domain>` if you have a domain you'd like to use. If you don't have one, you can use `pve.home.arpa`. See [RFC 8375](https://datatracker.ietf.org/doc/html/rfc8375#section-4) for more information on the `home.arpa` domain.
    b) Set a static IP address for Proxmox
    c) Set a DNS server
7. Review the settings and install Proxmox

See the [offical walkthrough](https://pve.proxmox.com/wiki/Installation) of the installation for more details on the available options.

### Post-Installation

- In the BIOS boot menu, you may want to reorder the boot order so your Proxmox install will boot first. You can also disable the other drives from the boot menu if you'd like.
- Plug in a network cable after configuring the server's static IP in your router. Use `ip addr show` on the server to view the MAC address and set your router to assign this MAC address your chosen static IP.

## Hardening

After installation, follow the [Proxmox Hardening Guide](https://github.com/HomeSecExplorer/Proxmox-Hardening-Guide) to secure your server.
The relevant guide for this version of Proxmox is the [PVE 9](https://github.com/HomeSecExplorer/Proxmox-Hardening-Guide/blob/main/docs/pve9-hardening-guide.md).
There are also scripts online on hardening Debian e.g. from [OVHcloud](https://github.com/ovh/debian-cis/blob/master/README.md) and from [a Github user](https://github.com/abualialfatih23/PVE-9-Hardening/blob/main/PVE9-Harden-FinalVersion-v1.sh).
Use these at your own risk and after auditing them yourself.
Selected portions of these guides and scripts are duplicated below and through the scripts in `harden/`.
Of course, read through the documentation yourself and understand the risks before running any scripts you find online.

###

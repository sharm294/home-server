#! /usr/bin/env bash

# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

# This script will install PVE onto Debian Trixie based on the instructions in
# https://pve.proxmox.com/wiki/Install_Proxmox_VE_on_Debian_13_Trixie. It's
# invoked automatically during the preseeded install of Debian 13 for Proxmox.

set -euo pipefail

# apt install proxmox-default-kernel
# systemctl reboot
# apt install proxmox-ve postfix open-iscsi chrony
# apt remove os-prober

if ip link show vmbr0 type bridge > /dev/null 2>&1; then
    echo "Bridge vmbr0 already exists"
    exit 0
fi

ip_addr=$(ip route get 1.2.3.4 | awk '{print $7}' | head -n 1)
# get first non-loopback network interface
nic=$(ip -o link show | awk -F': ' '$2 != "lo" {print $2; exit}')

# create the bridge for the VMs to use
ip link add name vmbr0 type bridge forward_delay 0 stp_state 0
ip link set vmbr0 up
ip addr flush dev "$nic"
ip link set "$nic" master vmbr0
ip link set "$nic" up
ip addr add "$ip_addr"/24 dev vmbr0
ip route add default via 192.168.0.1

# proxmox needs the hostname to resolve the IP address
sed -i "s+127.0.1.1+$ip_addr+g" /etc/hosts
systemctl restart pve-cluster

drive="/dev/disk/by-id/<ID>"
vg_name="vm"
thinpool_name="$vg_name-thin"
storage_id="local-lvm"
wipefs -a "$drive"
pvcreate "$drive"
vgcreate "$vg_name" "$drive"
lvcreate -l 100%FREE --thinpool "$thinpool_name" "$vg_name"
pvesm add lvmthin "$storage_id" --vgname "$vg_name" --thinpool "$thinpool_name" --content images,rootdir

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
echo "search home.arpa" >> /etc/resolv.conf

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

zpool create -o ashift=12 storage mirror "/dev/disk/by-id/<ID>" "/dev/disk/by-id/<ID>"
pvesm add zfspool zfs-storage -pool storage -content images,rootdir

# https://blog.kye.dev/proxmox-zfs-mounts/
zfs create storage/media_root
zfs create storage/nas

# create a mapped group and user for LXC
groupadd -g 110000 nas_users
useradd -u 101000 -s /usr/sbin/nologin -M -g nas_users nas_admin
chown -R nas_admin:nas_users /storage/media_root
chown -R nas_admin:nas_users /storage/nas

pveam download local debian-13-standard_13.1-2_amd64.tar.zst
pct create 1000 local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst --rootfs local-lvm:8 --password yourpassword --net0 name=eth0,bridge=vmbr0,ip=dhcp --cores 1 --memory 1024
# fix "Systemd 257 detected. You may need to enable nesting." warning
pct set 1000 --features nesting=1
pct set 1000 --mp0 /storage/nas,mp=/mnt/nas
pct set 1000 --mp1 /storage/media_root,mp=/mnt/media_root
pct start 1000
pct push 1000 ~/.ssh/authorized_keys /root/.ssh/authorized_keys

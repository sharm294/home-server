#! /usr/bin/env bash

# Copyright (c) 2022 modem7
# Copyright (c) 2023 UntouchedWagons
# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

# This script will create a VM template for Proxmox based on the work in:
# - https://github.com/modem7/public_scripts: create-ubuntu-cloud-template.sh
# - https://github.com/UntouchedWagons/Ubuntu-CloudInit-Docs: debian-13-cloudinit.sh
# Instructions:
#   - Set any of the VM variables below as needed in your environment
#   - Run this script in the Proxmox host

set -euo pipefail

# User Parameters (update or set via env as needed) ----------------------------

VM_ID_DEFAULT="${VM_ID_DEFAULT:-8000}"
STORAGE="${STORAGE:-vm}" # Name of disk storage within Proxmox

## VM variables
TEMPLATE_NAME="${TEMPLATE_NAME:-debian-13-template}"
AGENT_ENABLE="${AGENT_ENABLE:-1}" # Change to 0 if you don't want the guest agent
BALLOON="${BALLOON:-768}" # Minimum ballooning size (MB) with ballooning enabled
BIOS="${BIOS:-ovmf}" # Choose between ovmf (UEFI) or seabios
CORES="${CORES:-2}"
DISK_SIZE="${DISK_SIZE:-1G}"
SSD="${SSD:-1}" # set to "" if the VM storage drive is not an SSD
MACHINE="${MACHINE:-q35}" # Type of machine. Q35 or i440fx
MEM="${MEM:-2048}" # Max RAM: arbitrary value since this VM will be a template
NET_BRIDGE="${NET_BRIDGE:-vmbr0}" # Network bridge name
TAG="${TAG:-template,debian-template,debian,debian-13}"
VLAN="${VLAN:-}" # set to a VLAN ID if using a VLAN
CLOUD_USER="${CLOUD_USER:-varunsh}"
CLOUD_PASSWORD="${CLOUD_PASSWORD:-insecure}"

# Constants --------------------------------------------------------------------

IMG="debian-13-generic-amd64.qcow2"
BASE_URL="https://cloud.debian.org/images/cloud/trixie/latest"
EXPECTED_SHA=$(wget -qO- "$BASE_URL/SHA512SUMS" | awk '/'$IMG'/{print $1}')

WORK_DIR="/tmp"

# Functions --------------------------------------------------------------------

proxmox_check() {
    # Check if the script is running on a Proxmox system
    echo "### System Check"
    if pveversion &>/dev/null; then
        echo "This is a Proxmox system. Proceeding."
    else
        echo "This script is intended to run only on Proxmox. Exiting."
        exit 1
    fi
}

_compute_sha512() {
    sha512sum "$1" | awk '{print $1}'
}

download() {
    mkdir -p $WORK_DIR
    cd $WORK_DIR
    echo "### Downloading image $IMG"

    if [ ! -f "$IMG" ]; then
        wget -q "$BASE_URL/$IMG"

        local actual_sha
        actual_sha=$(_compute_sha512 "$IMG")

        if [ "$EXPECTED_SHA" != "$actual_sha" ]; then
            echo "File download failed: computed SHA sum does not match expected"
            exit 1
        fi

        qemu-img resize $IMG "$DISK_SIZE"
    fi
}

# Check if VM ID exists
_vm_id_exist() {
    local vm_id="$1"
    # Check if the VM ID exists in the list
    if qm list | awk '{print $1}' | grep -q "^$vm_id$"; then
        return 0 # VM exists
    else
        return 1 # VM does not exist
    fi
}

get_valid_vm_id() {
    VM_ID=$VM_ID_DEFAULT

    while _vm_id_exist "$VM_ID"; do
        echo "VM with ID $VM_ID exists."
        read -r -p "Enter a new VM ID: " VM_ID
    done
}

create_vendor_config() {
    if [ ! -d "/var/lib/vz/snippets" ]; then
        mkdir -p "/var/lib/vz/snippets"
    fi

    cat << EOF | tee /var/lib/vz/snippets/debian-13.yaml
#cloud-config
# for Proxmox, root login is needed
disable_root: false

runcmd:
    - apt-get update
    - apt-get install -y qemu-guest-agent
    - reboot
# Taken from https://forum.proxmox.com/threads/combining-custom-cloud-init-with-auto-generated.59008/page-3#post-428772
EOF
}

create_vm() {
    # Create or restore a virtual machine
    # --vga serial0 --serial0 socket: set display to serial
    # --net0 virtio,bridge=vmbr0: create default network bridge to Proxmox
    echo "### Creating VM"
    qm create "$VM_ID" --name "$TEMPLATE_NAME" \
        --memory "$MEM" --balloon "$BALLOON" \
        --cpu host --cores "$CORES" --numa 1 --bios "$BIOS" --machine "$MACHINE" \
        --net0 virtio,bridge="${NET_BRIDGE}"${VLAN:+,tag=$VLAN}
    qm set "$VM_ID" --agent enabled="$AGENT_ENABLE"${SSD:+,fstrim_cloned_disks=1}
    # --ostype l26: Linux 2.6 kernel
    qm set "$VM_ID" --ostype l26

    qm importdisk "$VM_ID" $WORK_DIR/$IMG "$STORAGE"
    qm set "$VM_ID" --scsihw virtio-scsi-single \
        --scsi0 "$STORAGE":vm-"$VM_ID"-disk-0,cache=writethrough,iothread=1${SSD:+,ssd=1,discard=on}
    # efidisk0 ...: Using UEFI requires creating an EFI disk
    qm set "$VM_ID" --efidisk0 "$STORAGE":0,efitype=4m,,pre-enrolled-keys=1,size=1M

    create_vendor_config

    qm set "$VM_ID" --tags "$TAG"
    qm set "$VM_ID" --scsi1 "$STORAGE":cloudinit
    qm set "$VM_ID" --rng0 source=/dev/urandom
    qm set "$VM_ID" --ciuser "$CLOUD_USER"
    qm set "$VM_ID" --cipassword "$CLOUD_PASSWORD"
    qm set "$VM_ID" --boot c --bootdisk scsi0
    qm set "$VM_ID" --tablet 0
    qm set "$VM_ID" --ipconfig0 ip=dhcp,ip6=dhcp
    qm set "$VM_ID" --sshkeys ~/.ssh/authorized_keys
    qm set "$VM_ID" --cicustom "vendor=local:snippets/debian-13.yaml"
    qm cloudinit update "$VM_ID"
    qm set "$VM_ID" --description "Some notes"

    qm template "$VM_ID"
}

cleanup() {
    rm -f $WORK_DIR/$IMG
}

# make sure you're running on Proxmox host
proxmox_check
# download the base cloud image
download
# make sure VM ID is unused
get_valid_vm_id
# create vendor config for cloudinit first boot
create_vendor_config
# create the VM template
create_vm
# cleanup files
cleanup

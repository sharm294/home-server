#! /usr/bin/env bash
# MIT License
#
# Copyright (c) 2022 modem7
# Copyright (c) 2023 UntouchedWagons
# Copyright (c) 2026 sharm294
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This script will create a VM template for Proxmox based on the work in:
# - https://github.com/modem7/public_scripts: create-ubuntu-cloud-template.sh
# - https://github.com/UntouchedWagons/Ubuntu-CloudInit-Docs: debian-13-cloudinit.sh
# Instructions:
#   - Set any of the VM variables below as needed in your environment
#   - Run this script in the Proxmox host

set -euo pipefail

# User Parameters (update or set via env as needed) ----------------------------

VMID_DEFAULT="${VMID_DEFAULT:-8000}"
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
_vmidexist() {
    local vmid="$1"
    # Check if the VM ID exists in the list
    if qm list | awk '{print $1}' | grep -q "^$vmid$"; then
        return 0 # VM exists
    else
        return 1 # VM does not exist
    fi
}

get_valid_vmid() {
    VMID=$VMID_DEFAULT

    while _vmidexist "$VMID"; do
        echo "VM with ID $VMID exists."
        read -r -p "Enter a new VM ID: " VMID
    done
}

create_vendor_config() {
    if [ ! -d "/var/lib/vz/snippets" ]; then
        mkdir -p "/var/lib/vz/snippets"
    fi

    cat << EOF | tee /var/lib/vz/snippets/debian-13.yaml
#cloud-config
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
    qm create "$VMID" --name "$TEMPLATE_NAME" \
        --memory "$MEM" --balloon "$BALLOON" \
        --cpu host --cores "$CORES" --numa 1 --bios "$BIOS" --machine "$MACHINE" \
        --net0 virtio,bridge="${NET_BRIDGE}"${VLAN:+,tag=$VLAN}
    qm set "$VMID" --agent enabled="$AGENT_ENABLE"${SSD:+,fstrim_cloned_disks=1}
    # --ostype l26: Linux 2.6 kernel
    qm set "$VMID" --ostype l26

    qm importdisk "$VMID" $WORK_DIR/$IMG "$STORAGE"
    qm set "$VMID" --scsihw virtio-scsi-single \
        --scsi0 "$STORAGE":vm-"$VMID"-disk-0,cache=writethrough,iothread=1${SSD:+,ssd=1,discard=on}
    # efidisk0 ...: Using UEFI requires creating an EFI disk
    qm set "$VMID" --efidisk0 "$STORAGE":0,efitype=4m,,pre-enrolled-keys=1,size=1M

    create_vendor_config

    qm set "$VMID" --tags "$TAG"
    qm set "$VMID" --scsi1 "$STORAGE":cloudinit
    qm set "$VMID" --rng0 source=/dev/urandom
    qm set "$VMID" --ciuser "$CLOUD_USER"
    qm set "$VMID" --cipassword "$CLOUD_PASSWORD"
    qm set "$VMID" --boot c --bootdisk scsi0
    qm set "$VMID" --tablet 0
    qm set "$VMID" --ipconfig0 ip=dhcp,ip6=dhcp
    qm set "$VMID" --sshkeys ~/.ssh/authorized_keys
    qm set "$VMID" --cicustom "vendor=local:snippets/debian-13.yaml"
    qm cloudinit update "$VMID"
    qm set "$VMID" --description "Some notes"

    qm template "$VMID"
}

cleanup() {
    rm -f $WORK_DIR/$IMG
}

# make sure you're running on Proxmox host
proxmox_check
# download the base cloud image
download
# make sure VM ID is unused
get_valid_vmid
# create vendor config for cloudinit first boot
create_vendor_config
# create the VM template
create_vm
# cleanup files
cleanup

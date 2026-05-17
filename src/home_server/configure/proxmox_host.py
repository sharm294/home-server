# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Configure the Proxmox host.

This file defines how to configure the Proxmox host after installation.
"""

from pyinfra.api import State
from pyinfra.api.operation import add_op
from pyinfra.operations import apt, files, server

from home_server.operations import qm


def create_debian_13_template(  # noqa: PLR0913
    state: State,
    template_vm_id: int = 8000,
    template_name: str = "debian-13-template",
    storage: str = "local-lvm",
    image_url: str = ("https://cloud.debian.org/images/cloud/trixie/latest"),
    image_filename: str = "debian-13-generic-amd64.qcow2",
    agent_enable: int = 1,
    cores: int = 2,
    memory: int = 2048,
    tag: str = "template,debian-template,debian,debian-13",
    cloud_user: str = "varunsh",
    cloud_password: str = "changeme",  # noqa: S107
    ci_password: str | None = None,
) -> None:
    """
    Create a Debian 13 template for Proxmox using idempotent operations.

    This function orchestrates the creation of a Proxmox VM template from a
    Debian cloud image using idempotent qm operations. It replaces the
    shell script approach with reliable, reproducible pyinfra operations.

    Args:
        state (State): pyinfra State object for operation tracking
        template_vm_id (int): VM ID for the template (default: 8000)
        template_name (str): Display name for the template
        storage (str): Target storage pool (default: local-lvm)
        image_url (str): Base URL for Debian cloud images
        image_filename (str): Filename of the cloud image to download
        agent_enable (int): Enable Proxmox guest agent (0 or 1)
        cores (int): Number of CPU cores (default: 2)
        memory (int): RAM in MB (default: 2048)
        tag (str): Comma-separated VM tags
        cloud_user (str): Cloud-init username
        cloud_password (str): Cloud-init password
        ci_password (str | None): Override cloud password (optional)

    Returns:
        None - Adds operations to the provided State object

    Notes:
        - The function adds operations to the state; call run_ops(state)
          to execute them
        - Each operation is idempotent: running twice produces same result
        - Requires pveversion to be available (Proxmox host)

    Example:
        >>> from pyinfra.api import State, connect_all, run_ops
        >>> state = State()
        >>> create_debian_13_template(state, template_vm_id=8000)
        >>> connect_all(state)
        >>> run_ops(state)

    """
    # Resolve password
    actual_password = ci_password if ci_password is not None else cloud_password

    # Step 1: Download the cloud image
    image_path = f"/tmp/{image_filename}"  # noqa: S108
    add_op(state, files.download, f"{image_url}/{image_filename}", image_path)

    # Step 2: Create the template VM
    add_op(
        state,
        qm.create,
        template_vm_id,
        template_name,
        memory=memory,
        cores=cores,
        sockets=1,
        cpu="host",
        balloon=int(memory * 0.375),  # 37.5% of max memory
        bios="ovmf",
        machine="q35",
        net0="virtio,bridge=vmbr0",
    )

    # Step 3: Import the disk image
    add_op(
        state,
        qm.importdisk,
        template_vm_id,
        image_path,
        storage,
    )

    # Step 4: Configure the VM with multiple qm set operations
    # Using a single batch set operation for efficiency
    add_op(
        state,
        qm.set,
        template_vm_id,
        agent=f"enabled={agent_enable}",
        ostype="l26",
        scsihw="virtio-scsi-single",
        efidisk0=f"{storage}:0,efitype=4m,pre-enrolled-keys=1,size=1M",
        tags=tag,
        scsi1=f"{storage}:cloudinit",
        rng0="source=/dev/urandom",
        ciuser=cloud_user,
        cipassword=actual_password,
        boot="c",
        bootdisk="scsi0",
        tablet=0,
        ipconfig0="ip=dhcp,ip6=dhcp",
        sshkeys="~/.ssh/authorized_keys",
        cicustom="vendor=local:snippets/debian-13.yaml",
        description="Debian 13 Cloud-Init Template",
    )

    # Step 5: Update cloud-init
    add_op(state, qm.cloudinit_update, template_vm_id)

    # Step 6: Convert to template
    add_op(state, qm.template, template_vm_id)


def clone_template_to_vm(  # noqa: PLR0913
    state: State,
    source_template_id: int,
    target_vm_id: int,
    target_name: str = "main",
    disk_size: str = "50G",
    additional_tags: str | None = None,
) -> None:
    """
    Clone a template VM to create a new VM instance.

    This function creates a full clone of a template VM and resizes its disk.

    Args:
        state (State): pyinfra State object for operation tracking
        source_template_id (int): ID of the template VM to clone from
        target_vm_id (int): VM ID for the new cloned VM
        target_name (str): Display name for the new VM (default: "main")
        disk_size (str): Desired disk size (default: "50G")
        additional_tags (str | None): Additional tags to add to the cloned VM

    Returns:
        None - Adds operations to the provided State object

    Example:
        >>> from pyinfra.api import State, connect_all, run_ops
        >>> state = State()
        >>> clone_template_to_vm(state, 8000, 100, "web-server-1")
        >>> connect_all(state)
        >>> run_ops(state)

    """
    # Clone the template
    add_op(
        state,
        qm.clone,
        source_template_id,
        target_vm_id,
        target_name,
        full=1,
    )

    # Resize the disk
    add_op(state, qm.resize, target_vm_id, "scsi0", disk_size)

    # Add tags if provided
    if additional_tags:
        add_op(state, qm.set, target_vm_id, tags=additional_tags)


def start_vm(state: State, vm_id: int) -> None:
    """
    Start a VM.

    This is an idempotent operation: if the VM is already running, it noops.

    Args:
        state (State): pyinfra State object for operation tracking
        vm_id (int): ID of the VM to start

    Returns:
        None - Adds operation to the provided State object

    Example:
        >>> from pyinfra.api import State, connect_all, run_ops
        >>> state = State()
        >>> start_vm(state, 100)
        >>> connect_all(state)
        >>> run_ops(state)

    """
    add_op(state, qm.start, vm_id)


def main(state: State) -> None:
    """Entrypoint for configuring the Proxmox host."""
    add_op(
        state,
        server.script,
        "src/home_server/configure/install_pve.sh",
    )

    add_op(
        state, apt.packages, ["proxmox-ve", "postfix", "open-iscsi", "chrony"]
    )
    add_op(state, apt.packages, ["os-prober"], present=False)

    add_op(
        state,
        server.script,
        "src/home_server/configure/proxmox_community_scripts/microcode.sh",
    )

    add_op(
        state,
        server.script,
        "src/home_server/configure/proxmox_community_scripts/post-pve-install.sh",
    )

    create_debian_13_template(state)
    clone_template_to_vm(state, 8000, 100)
    start_vm(state, 100)

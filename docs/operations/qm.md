<!--
Copyright (c) 2026 sharm294
SPDX-License-Identifier: AGPL-3.0-or-later
--->

# qm Operations Guide

This guide demonstrates how to use the idempotent Proxmox qm operations instead of shell scripts.

## Overview

The `home_server.operations.qm` module provides idempotent pyinfra operations for managing QEMU/KVM virtual machines on Proxmox:

- **`create(vm_id, vm_name, **kwargs)`** — Create a new VM
- **`set(vm_id, **config)`** — Configure VM settings (memory, CPU, devices, etc.)
- **`start(vm_id)`** — Start a VM
- **`resize(vm_id, disk_id, size)`** — Resize a VM disk
- **`importdisk(vm_id, source_image, storage, disk_format)`** — Import a disk image
- **`template(vm_id)`** — Convert a VM to a template
- **`clone(source_vm_id, target_vm_id, target_name, full)`** — Clone a template VM
- **`cloudinit_update(vm_id)`** — Update cloud-init metadata

All operations are **idempotent**: running them multiple times produces the same result as running once.

## Supporting Facts

The operations use custom facts to determine idempotency:

- **`qm.List`** — Get list of all VMs on the host
- **`qm.VmIdExists`** — Check if a VM ID exists
- **`qm.VmStatus`** — Get VM status (running, stopped, paused)
- **`qm.VmConfig`** — Parse current VM configuration from `qm config`
- **`qm.DiskSize`** — Get current disk size for a specific disk

## Usage Examples

### Example 1: Create a Template VM and Configure It

Replace shell scripts with idempotent operations:

```python
from pyinfra.api import State
from pyinfra.api.operation import add_op
from home_server.operations import qm

state = State()

# Create the template VM
add_op(state, qm.create, 8000, "debian-13-template",
       memory=2048, cores=2, sockets=1)

# Import disk image
add_op(state, qm.importdisk, 8000,
       "/tmp/debian-13-generic-amd64.qcow2", "local-lvm")

# Configure the VM with multiple settings (idempotent set)
add_op(state, qm.set, 8000,
       agent="enabled=1",
       ostype="l26",
       scsihw="virtio-scsi-single",
       tags="template,debian-13")

# Update cloud-init
add_op(state, qm.cloudinit_update, 8000)

# Convert to template
add_op(state, qm.template, 8000)
```

### Example 2: Clone a Template and Resize

```python
from pyinfra.api import State, connect_all, run_ops
from pyinfra.api.operation import add_op
from home_server.operations import qm

state = State()

# Clone the template
add_op(state, qm.clone, 8000, 100, "web-server-1", full=1)

# Resize the disk
add_op(state, qm.resize, 100, "scsi0", "50G")

# Start the VM
add_op(state, qm.start, 100)

# Execute all operations
connect_all(state)
run_ops(state)
```

### Example 3: Using the Helper Functions

The `home_server.configure.proxmox_template` module provides high-level functions:

```python
from pyinfra.api import State, connect_all, run_ops
from home_server.configure.proxmox_template import (
    create_debian_13_template,
    clone_template_to_vm,
    start_vm,
)

state = State()

# Create a template with all settings
create_debian_13_template(
    state,
    template_vm_id=8000,
    template_name="debian-13-template",
    storage="local-lvm",
    cores=2,
    memory=2048,
)

# Clone it to create a new VM
clone_template_to_vm(
    state,
    source_template_id=8000,
    target_vm_id=100,
    target_name="web-server-1",
    disk_size="50G",
)

# Start the VM
start_vm(state, 100)

# Execute all operations
connect_all(state)
run_ops(state)
```

## Idempotency Behavior

Each operation checks the current state before taking action:

| Operation | Check | Noop Condition |
| --------- | ----- | -------------- |
| `create` | `qm list` | VM already exists with same ID and name |
| `set` | `qm config` | All settings match desired configuration |
| `start` | `qm status` | VM is already running |
| `resize` | `qm config` | Disk is already >= desired size |
| `importdisk` | `qm config` | Disk already configured for VM |
| `template` | `qm config` | `template=1` in config |
| `clone` | `qm list` | Target VM ID already exists |
| `cloudinit_update` | N/A | Always executes (regenerates metadata) |

## Migration from Shell Scripts

To migrate from shell script qm commands:

### Before (Shell Script)

```bash
#!/bin/bash
qm create 100 --name "vm-name" --memory 2048 --cores 2
qm set 100 --agent enabled=1
qm set 100 --ostype l26
qm start 100
```

### After (Python + pyinfra)

```python
from pyinfra.api import State, connect_all, run_ops
from pyinfra.api.operation import add_op
from home_server.operations import qm

state = State()

add_op(state, qm.create, 100, "vm-name", memory=2048, cores=2)
add_op(state, qm.set, 100, agent="enabled=1", ostype="l26")
add_op(state, qm.start, 100)

connect_all(state)
run_ops(state)
```

## Integration with proxmox_host.py

To use these operations in the Proxmox host configuration:

```python
# src/home_server/configure/proxmox_host.py
from pyinfra.api import State
from pyinfra.api.operation import add_op
from home_server.configure.proxmox_template import create_debian_13_template

def main(state: State) -> None:
    """Entrypoint for configuring the Proxmox host."""

    # Install Proxmox packages...

    # Create template using idempotent operations
    create_debian_13_template(state, template_vm_id=8000)
```

## Error Handling

Operations raise `OperationError` on fatal conditions:

```python
from pyinfra.api.exceptions import OperationError

try:
    add_op(state, qm.set, 999, agent="enabled=1")
    # If this is the only operation, connect and run
    connect_all(state)
    run_ops(state)
except OperationError as e:
    print(f"Operation failed: {e}")
```

## Performance Considerations

- **Fact queries are fresh**: Each operation queries current state to ensure idempotency
- **Batch operations**: Use a single `qm.set()` call for multiple settings instead of multiple calls
- **Disk size comparison**: `resize` checks current size to avoid unnecessary operations

## Troubleshooting

### VM doesn't exist error

```python
# Use VmIdExists fact to check first
from home_server.facts import qm
if not host.get_fact(qm.VmIdExists, vm_id=100):
    print("VM 100 does not exist")
```

### Configuration not applied

Ensure the key names match Proxmox's `qm config` format:

```text
agent → agent=enabled=1 (not just enabled)
ostype → ostype=l26
```

### Import disk already exists

The `importdisk` operation is idempotent and skips if `scsi0` is already configured.

## See Also

- [home_server.operations.qm](src/home_server/operations/qm.py)
- [home_server.facts.qm](src/home_server/facts/qm.py)
- [home_server.configure.proxmox_template](src/home_server/configure/proxmox_template.py)
- [Proxmox QM Documentation](https://pve.proxmox.com/wiki/Qm)

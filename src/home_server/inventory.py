# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""Inventories define the system to configure."""

from pathlib import Path
from typing import Any

import yaml
from pyinfra.api import Inventory


def make_inventory_from_yaml(path: Path) -> Inventory:
    """
    Construct an inventory object from a YAML config file.

    Args:
        path (Path): Path to the yaml config file

    Returns:
        Inventory: Built Inventory

    """
    with path.open() as f:
        inventory_yaml: dict[str, Any] = yaml.safe_load(f)
    names = []
    groups: dict[str, tuple[list[str], dict[str, str]]] = {}
    for group_name, group in inventory_yaml.items():
        hosts = group["hosts"]
        group_data = group.get("data", {})
        groups[group_name] = ([], group_data)
        for host in hosts:
            host_name, host_data = next(iter(host.items()))
            groups[group_name][0].append(host_name)
            names.append((host_name, host_data or {}))

    return Inventory((names, {}), **groups)


def make_inventory(inventory_path: Path) -> Inventory:
    """
    Parse a file as an inventory.

    Args:
        inventory_path (Path): Path to inventory

    Raises:
        ValueError: Raised on error

    Returns:
        Inventory: Inventory object

    """
    if inventory_path.exists():
        inventory = make_inventory_from_yaml(inventory_path)
    else:
        err_msg = f"Cannot find inventory at {inventory_path}"
        raise ValueError(err_msg)
    return inventory

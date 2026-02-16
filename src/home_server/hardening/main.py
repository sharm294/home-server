# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""
Entry point for home_server harden CLI.

Hardening is used to run a set of established rules on a host machine to improve
its security. Currently, hardening uses CIS benchmarks to define the rules and
settings to configure on the target host machine.
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import yaml
from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.operations import run_ops
from pyinfra_cli.prints import print_meta

from . import Feature, Preset
from .checks import CheckMeta, get_profile
from .checks.debian_13 import REGISTRY


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
        group_data = group["data"]
        groups[group_name] = ([], group_data)
        for host in hosts:
            host_name, host_data = next(iter(host.items()))
            groups[group_name][0].append(host_name)
            names.append((host_name, host_data or {}))

    return Inventory((names, {}), **groups)


def set_presets(args: argparse.Namespace) -> None:
    """Configure CLI arguments based on the set preset."""
    preset = args.preset
    if preset is None:
        return
    if preset == Preset.AZURE:
        # CIS 1.1.1.8 notes this for Azure
        args.features.append(Feature.PHYSICAL_MEDIA)


def main(args: argparse.Namespace) -> None:
    """Entry point for home_server harden CLI."""
    logging.basicConfig(level=logging.INFO)
    set_presets(args)

    profile = get_profile(args.platform, args.level)

    inventory_path = Path(args.inventory)
    if inventory_path.exists():
        inventory = make_inventory_from_yaml(inventory_path)
    else:
        err_msg = f"Cannot find inventory at {inventory_path}"
        raise ValueError(err_msg)

    config = Config()
    state = State(inventory, config)

    connect_all(state)

    requested_features = set(args.features)
    op_metas: dict[str, CheckMeta] = {}

    for check in REGISTRY:
        if check.enabled(profile, requested_features, audit=args.audit):
            op_meta = check.run(state)
            op_metas[check.name] = op_meta

    print_meta(state)

    if args.dry_run:
        return

    run_ops(state)

    for check_name, meta in op_metas.items():
        print(check_name)
        meta.print()

    # ruff: disable[ERA001]
    # for check_name, retval in cmd_outputs.items():
    #     print(check_name)
    #     for host_name, op_meta in retval.items():
    #         print(host_name)
    #         # print(op_meta._commands)
    #         print(op_meta.stdout)
    #         print(op_meta.stderr)
    # ruff: enable[ERA001]

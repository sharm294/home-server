# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import argparse
from pathlib import Path
from typing import Any

import yaml
from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.operations import run_ops
from pyinfra_cli.prints import print_meta

from . import Feature, Preset
from .checks import get_profile
from .checks.debian_13 import REGISTRY


def make_inventory_from_yaml(path: Path):
    with path.open() as f:
        inventory_yaml: dict[str, Any] = yaml.safe_load(f)
    names = []
    groups = {}
    for group_name, group in inventory_yaml.items():
        hosts = group["hosts"]
        group_data = group["data"]
        groups[group_name] = ([], group_data)
        for host in hosts:
            host_name, host_data = next(iter(host.items()))
            groups[group_name][0].append(host_name)
            names.append((host_name, host_data or {}))

    return Inventory((names, {}), **groups)


def set_presets(args: argparse.Namespace):
    preset = args.preset
    if preset is None:
        return
    if preset == Preset.AZURE:
        # CIS 1.1.1.8 notes this for Azure
        args.features.append(Feature.PHYSICAL_MEDIA)


def main(args: argparse.Namespace) -> None:
    # logging.basicConfig(level=logging.INFO)
    set_presets(args)

    profile = get_profile(args.platform, args.level)

    inventory_path = Path(args.inventory)
    if inventory_path.exists():
        inventory = make_inventory_from_yaml(inventory_path)
    else:
        raise ValueError(f"Cannot find inventory at {inventory_path}")

    config = Config()
    state = State(inventory, config)

    connect_all(state)

    requested_features = set(args.features)

    for check in REGISTRY:
        if check.enabled(profile, requested_features):
            check.run(state)

    print("Running operations...")
    print_meta(state)

    if args.dry_run:
        return

    run_ops(state)

# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import argparse
import logging
from pathlib import Path
from typing import Any

import yaml
from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.facts import get_facts
from pyinfra.api.operations import run_ops
from pyinfra.facts.server import Os
from pyinfra_cli.prints import print_meta

from .checks.debian_13 import cis_1_1_1_x


def make_inventory_from_yaml(path: Path):
    with path.open() as f:
        inventory_yaml: dict[str, Any] = yaml.safe_load(f)
    names = []
    groups = {}
    for group_name, group in inventory_yaml.items():
        hosts = group["hosts"]
        group_data = group["data"]
        groups[group_name] = ([], group_data)
        # hosts, group_data = group
        for host in hosts:
            host_name, host_data = next(iter(host.items()))
            groups[group_name][0].append(host_name)
            names.append(host_name)

    return Inventory((names, {}), groups=groups)


def main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO)

    inventory_path = Path(args.inventory)
    if inventory_path.exists():
        inventory = make_inventory_from_yaml(inventory_path)
        # inventory = make_inventory(args.inventory)
    else:
        raise ValueError(f"Cannot find inventory at {inventory_path}")

    # inventory = Inventory((["192.168.0.79"], {'ssh_user': "root"}))
    # inventory = Inventory((["192.168.0.79"], {}))
    config = Config()
    state = State(inventory, config)

    connect_all(state)

    cramfs = cis_1_1_1_x.CIS_1()
    cramfs.run(state)

    # foo = ensure_unzip_present(state)

    print("Running operations...")
    print_meta(state)

    run_ops(state)

    host = state.inventory.hosts["192.168.0.79"]
    # print(foo[host].changed, foo[host].stdout, foo[host].stderr)

    print(get_facts(state, Os))

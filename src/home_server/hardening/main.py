# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""
Entry point for home_server harden CLI.

Hardening is used to run a set of established rules on a host machine to improve
its security. Currently, hardening uses CIS benchmarks to define the rules and
settings to configure on the target host machine.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from pyinfra.api import Config, State
from pyinfra.api.connect import connect_all
from pyinfra.api.operations import run_ops
from pyinfra_cli.prints import print_meta

from home_server.inventory import make_inventory

from . import Feature, Preset
from .checks import CheckMeta, get_profile
from .checks.debian_13 import REGISTRY

if TYPE_CHECKING:
    import argparse
    from argparse import ArgumentParser, _SubParsersAction


def configure_parser(subparser: _SubParsersAction[ArgumentParser]) -> None:
    """
    Define the subparser for the harden command.

    Args:
        subparser (_SubParsersAction[ArgumentParser]): Parent parser

    """
    harden = subparser.add_parser(
        "harden",
        help="Run CIS Benchmark hardening checks",
    )
    inventory_help = (
        "Path to an inventory file or hostname/IP address to run"
        "commands on. Use @local to run on this host."
    )
    harden.add_argument(
        "inventory",
        type=Path,
        help=inventory_help,
    )
    harden.add_argument(
        "--platform",
        choices=["server", "workstation"],
        default="server",
        help="Choose the CIS platform type to harden. Defaults to 'server'.",
    )
    harden.add_argument(
        "--level",
        choices=[1, 2],
        default=1,
        help="Enable CIS rules up to a level. Defaults to '1'.",
    )
    feature_help = textwrap.dedent("""
        Some hardening rules interfere with features you may want to use. Pass
        any features you want to keep to disable rules that affect them, even if
        the default CIS platform/level enable them.""")
    harden.add_argument(
        "--features",
        choices=[x.value for x in Feature],
        action="extend",
        nargs="+",
        help=feature_help,
        default=[],
    )
    harden.add_argument(
        "--preset",
        choices=[x.value for x in Preset],
        help="Presets to set a variety of options in one convenient flag",
    )
    harden.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't execute operations on target hosts",
    )
    harden.add_argument(
        "--audit",
        action="store_true",
        help="Audit the system and view any manual fixes needed",
    )
    harden.set_defaults(func=main)


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
    set_presets(args)

    profile = get_profile(args.platform, args.level)

    inventory = make_inventory(args.inventory)

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

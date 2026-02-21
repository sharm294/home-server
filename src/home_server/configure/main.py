# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""
Entry point for home_server configure CLI.

Configuring is used to ensure a host system is configured according to some
preset.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pyinfra.api import Config, State
from pyinfra.api.connect import connect_all
from pyinfra.api.operation import add_op
from pyinfra.api.operations import run_ops
from pyinfra.operations import server
from pyinfra_cli.prints import print_meta

from home_server.inventory import make_inventory

from . import Preset

if TYPE_CHECKING:
    import argparse
    from argparse import ArgumentParser, _SubParsersAction


def configure_parser(subparser: _SubParsersAction[ArgumentParser]) -> None:
    """
    Define the subparser for the configure command.

    Args:
        subparser (_SubParsersAction[ArgumentParser]): Parent parser

    """
    configure = subparser.add_parser(
        "configure",
        help="Configure the inventory hosts",
    )
    inventory_help = (
        "Path to an inventory file or hostname/IP address to run"
        "commands on. Use @local to run on this host."
    )
    configure.add_argument(
        "inventory",
        type=Path,
        help=inventory_help,
    )
    configure.add_argument(
        "--preset",
        choices=[x.value for x in Preset],
        type=Preset,
        help="Presets to set a variety of options in one convenient flag",
    )
    configure.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't execute operations on target hosts",
    )
    configure.set_defaults(func=main)


def set_presets(args: argparse.Namespace) -> None:
    """Configure CLI arguments based on the set preset."""
    preset = args.preset
    if preset is None:
        return
    if preset == Preset.PROXMOX_HOST:
        pass


def main(args: argparse.Namespace) -> None:
    """Entry point for home_server configure CLI."""
    set_presets(args)

    inventory = make_inventory(args.inventory)

    config = Config()
    state = State(inventory, config)

    connect_all(state)

    print_meta(state)

    if args.preset == Preset.PROXMOX_HOST:
        add_op(
            state,
            server.script,
            "src/home_server/configure/cloud_debian_13.sh",
        )
    else:
        pass

    if args.dry_run:
        return

    run_ops(state)

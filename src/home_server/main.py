# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""Entry point for home_server."""

import argparse
import textwrap
from pathlib import Path

from home_server import hardening


def main() -> None:
    """Entry point for home_server."""
    parser = argparse.ArgumentParser(description="Home Server Management Tool")

    subparser = parser.add_subparsers(dest="command", required=True)

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
        choices=[x.value for x in hardening.Feature],
        action="extend",
        nargs="+",
        help=feature_help,
        default=[],
    )
    harden.add_argument(
        "--preset",
        choices=[x.value for x in hardening.Preset],
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
    harden.set_defaults(func=hardening.main)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        err_msg = "No subparser function found"
        raise argparse.ArgumentError(None, err_msg)
    args.func(args)


if __name__ == "__main__":
    main()

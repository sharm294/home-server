# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import argparse

from home_server import hardening


def main():
    parser = argparse.ArgumentParser(description="Home Server Management Tool")

    subparser = parser.add_subparsers(dest="command", required=True)

    harden = subparser.add_parser(
        "harden", help="Run CIS Benchmark hardening checks"
    )
    harden.add_argument(
        "--platform",
        choices=["server", "workstation"],
        default="server",
        help="Choose the platform type to harden. Defaults to 'server'.",
    )
    harden.add_argument(
        "--level",
        choices=[1, 2],
        default=1,
        help="Enable rules up to a level. Defaults to '1'.",
    )
    harden.add_argument(
        "--dry-run",
        action="store_true",
        help="Run checks without making changes",
    )
    harden.set_defaults(func=hardening.main)

    args = parser.parse_args()

    assert hasattr(args, "func")
    args.func(args)


if __name__ == "__main__":
    main()

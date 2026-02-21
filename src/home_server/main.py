# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""Entry point for home_server."""

import argparse
import logging

from home_server import configure, hardening


def main() -> None:
    """Entry point for home_server."""
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Home Server Management Tool")

    subparser = parser.add_subparsers(dest="command", required=True)

    hardening.configure_parser(subparser)
    configure.configure_parser(subparser)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        err_msg = "No subparser function found"
        raise argparse.ArgumentError(None, err_msg)
    args.func(args)


if __name__ == "__main__":
    main()

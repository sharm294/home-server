# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import argparse
import logging

from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.facts import get_facts
from pyinfra.api.operations import run_ops
from pyinfra.facts.server import Os
from pyinfra_cli.prints import print_meta

from .operations.apt import ensure_unzip_present


def main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO)
    inventory = Inventory((["@local"], {}))
    config = Config()
    state = State(inventory, config)

    connect_all(state)

    foo = ensure_unzip_present(state)

    print("Running operations...")
    print_meta(state)

    run_ops(state)

    host = state.inventory.hosts["@local"]
    print(foo[host].changed, foo[host].stdout, foo[host].stderr)

    print(get_facts(state, Os))

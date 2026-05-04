# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

import enum


class Preset(enum.StrEnum):
    PROXMOX_HOST = "proxmox-host"
    PROXMOX_VM = "proxmox-vm"
    PROXMOX_CONTAINER = "proxmox-container"


from .main import configure_parser, main  # noqa: E402

__all__ = ["configure_parser", "main"]

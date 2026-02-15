# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import enum


class Feature(enum.StrEnum):
    CONTAINERS = "containers"  # for containerization like Docker and LXC
    SNAP = "snap"  # for Linux Snap packages
    PHYSICAL_MEDIA = "physical_media"  # for writing DVDs, CDs and Blu-Rays
    USB_STORAGE = "usb_storage"  # for USB storage devices


class Preset(enum.StrEnum):
    PROXMOX = "proxmox"
    AZURE = "azure"


from .main import main  # noqa: E402

__all__ = ["main"]

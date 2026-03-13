# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

# this needs to be done to match the patching in pyinfra's CLI
from gevent import monkey

monkey.patch_all()

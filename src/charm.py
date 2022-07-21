#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Kubernetes Operator for the Meilisearch search engine."""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class MeilisearchOperatorCharm(CharmBase):
    """Charmed Operator for the Meilisearch search engine."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.meilisearch_pebble_ready, self._on_meilisearch_pebble_ready)

    def _on_meilisearch_pebble_ready(self, event):
        """Define and start a workload using the Pebble API."""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        pebble_layer = {
            "summary": "meilisearch layer",
            "description": "pebble config layer for meilisearch",
            "services": {
                "meilisearch": {
                    "override": "replace",
                    "summary": "meilisearch",
                    "command": "/bin/meilisearch",
                    "startup": "enabled",
                }
            },
        }
        # Add initial Pebble config layer using the Pebble API
        container.add_layer("meilisearch", pebble_layer, combine=True)
        # Autostart any services that were defined with startup: enabled
        container.autostart()
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(MeilisearchOperatorCharm)

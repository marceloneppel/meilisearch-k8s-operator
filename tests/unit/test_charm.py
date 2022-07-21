# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest

from ops.model import ActiveStatus
from ops.testing import Harness

from charm import MeilisearchOperatorCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(MeilisearchOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_meilisearch_pebble_ready(self):
        # Check the initial Pebble plan is empty
        initial_plan = self.harness.get_container_pebble_plan("meilisearch")
        self.assertEqual(initial_plan.to_yaml(), "{}\n")
        # Expected plan after Pebble ready with default config
        expected_plan = {
            "services": {
                "meilisearch": {
                    "override": "replace",
                    "summary": "meilisearch",
                    "command": "/bin/meilisearch",
                    "startup": "enabled",
                }
            },
        }
        # Get the meilisearch container from the model
        container = self.harness.model.unit.get_container("meilisearch")
        # Emit the PebbleReadyEvent carrying the meilisearch container
        self.harness.charm.on.meilisearch_pebble_ready.emit(container)
        # Get the plan now we've run PebbleReady
        updated_plan = self.harness.get_container_pebble_plan("meilisearch").to_dict()
        # Check we've got the plan we expected
        self.assertEqual(expected_plan, updated_plan)
        # Check the service was started
        service = self.harness.model.unit.get_container("meilisearch").get_service("meilisearch")
        self.assertTrue(service.is_running())
        # Ensure we set an ActiveStatus with no message
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

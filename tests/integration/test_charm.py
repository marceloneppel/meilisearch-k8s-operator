#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import meilisearch
import pytest
import yaml
from pytest_operator.plugin import OpsTest

from tests.integration.helpers import search

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test: OpsTest):
    """Build the charm-under-test and deploy it.

    Assert on the unit status before any other checks.
    """
    # Build and deploy charm from local source folder.
    charm = await ops_test.build_charm(".")
    resources = {
        "meilisearch-image": METADATA["resources"]["meilisearch-image"]["upstream-source"]
    }
    await ops_test.model.deploy(charm, resources=resources, application_name=APP_NAME)

    # Wait for the desired status.
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        raise_on_blocked=True,
        timeout=1000,
    )
    assert ops_test.model.applications[APP_NAME].units[0].workload_status == "active"


@pytest.mark.abort_on_fail
async def test_search_engine_is_up(ops_test: OpsTest):
    # Get the IP address of the deployed unit.
    status = await ops_test.model.get_status()
    address = status["applications"][APP_NAME]["units"][f"{APP_NAME}/0"]["address"]

    # Create the meilisearch client.
    client = meilisearch.Client(f"http://{address}:7700", "masterKey")

    # Define some documents.
    documents = [
        {"id": 1, "title": "Carol", "genres": ["Romance", "Drama"]},
        {"id": 2, "title": "Wonder Woman", "genres": ["Action", "Adventure"]},
    ]

    # Get a reference to the index that will be created.
    index = client.index("movies")

    # Add some documents to the index and wait for the update to finish.
    index.add_documents(documents)

    # Search for a document using a query containing a typo.
    result = search(index, "caorl")
    assert result["hits"][0]["id"] == 1

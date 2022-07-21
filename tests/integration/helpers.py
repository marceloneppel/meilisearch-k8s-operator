#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from typing import Any, Dict

import meilisearch
from meilisearch.index import Index
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@retry(
    retry=retry_if_exception_type(meilisearch.errors.MeiliSearchApiError),
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=2, max=30),
)
def search(index: Index, query: str) -> Dict[str, Any]:
    """Search for a document using a query.

    Args:
        index: The index to search.
        query: The query to search for.
    """
    return index.search(query)

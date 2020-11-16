import json
from typing import Dict

import requests

from ohsome_quality_tool.utils.config import OHSOME_API
from ohsome_quality_tool.utils.definitions import logger


def query_ohsome_api(endpoint: str, categories: Dict, bpolys: str) -> Dict:
    """Query ohsome api endpoint for categories and respective filters."""

    # TODO: Use threading here to run multiple queries at a time
    query_results = {}
    for cat, filter_string in categories.items():
        url = f"{OHSOME_API}{endpoint}"
        params = {"bpolys": bpolys, "filter": filter_string}
        result = json.loads(requests.get(url, params).text)
        query_results[cat] = result
        logger.info(f"got query results for: cat='{cat}', filter='{filter_string}'")

    return query_results

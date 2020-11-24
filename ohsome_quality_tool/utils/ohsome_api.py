import json
from typing import Dict

import requests

from ohsome_quality_tool.utils.config import OHSOME_API
from ohsome_quality_tool.utils.definitions import logger


def process_ohsome_api(
    endpoint: str, layers: Dict, bpolys: str, time: str = None
) -> Dict:
    """Process many ohsome api queries for layers and respective filters."""

    # TODO: Use threading here to run multiple queries at a time
    query_results = {}
    for layer in layers.keys():
        filter_string = layers[layer]["filter"]
        unit = layers[layer]["unit"]
        result = query_ohsome_api(
            endpoint=endpoint, filter_string=filter_string, unit=unit, bpolys=bpolys
        )
        query_results[layer] = result
        logger.info(f"got query results for: cat='{layer}', filter='{filter_string}'")

    return query_results


def query_ohsome_api(
    endpoint: str, filter_string: str, unit: str, bpolys: str, time: str = None
) -> Dict:
    """Query ohsome api endpoint for respective filter."""

    # TODO: Use threading here to run multiple queries at a time
    url = f"{OHSOME_API}{endpoint}/{unit}/"
    params = {"bpolys": bpolys, "filter": filter_string, "time": time}
    result = json.loads(requests.post(url, data=params).text)
    logger.info(f"got query results for: {url}, filter='{filter_string}'")

    return result

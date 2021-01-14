import json
from typing import Dict

import requests

from ohsome_quality_tool.utils.definitions import OHSOME_API, logger


def process_ohsome_api(
    endpoint: str, layers: Dict, bpolys: str, time: str = None
) -> Dict:
    """Process many ohsome api queries for layers and respective filters."""
    logger.info("start to query ohsome api for all layers")
    # TODO: Use threading here to run multiple queries at a time
    query_results = {}
    for layer in layers.keys():
        filter_string = layers[layer]["filter"]
        unit = layers[layer]["unit"]
        result = query_ohsome_api(
            endpoint=endpoint,
            filter_string=filter_string,
            unit=unit,
            bpolys=bpolys,
            time=time,
        )
        query_results[layer] = result

    logger.info("finished ohsome query for all layers")
    return query_results


def query_ohsome_api(
    endpoint: str, filter_string: str, bpolys: str, time: str = None
) -> Dict:
    """Query ohsome api endpoint for respective filter."""
    logger.info("start to query ohsome api")
    url = f"{OHSOME_API}{endpoint}"
    params = {"bpolys": bpolys, "filter": filter_string, "time": time}
    result = json.loads(requests.post(url, data=params).text)
    logger.info(f"got query results for: {url}, filter='{filter_string}'")

    return result

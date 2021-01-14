import os
from typing import Dict

import requests
import yaml

from ohsome_quality_tool.utils.definitions import OHSOME_API, logger


# TODO: Add documentation on time string format.
def query(layer, bpolys: str, time: str = None) -> Dict:
    """Query ohsome API endpoint with filter."""
    url = OHSOME_API + layer["endpoint"]
    data = {"bpolys": bpolys, "filter": layer.filter, "time": time}
    response = requests.post(url, data=data)

    logger.info("Query ohsome API.")
    logger.info("Query URL: " + url)
    logger.info("Query Filter: " + layer.filter)
    if response.status_code == 200:
        logger.info("Query successful!")
    elif response.status_code == 404:
        logger.info("Query failed!")

    return response.json()


def load_layer_definitions() -> Dict:
    """Read ohsome API parameter of each layer from text file."""
    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, "layer_definitions.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)

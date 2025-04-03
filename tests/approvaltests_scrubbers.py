import json
import math
import re


def round_fitted_y_values(figure: dict) -> dict:
    for data in figure["data"]:
        for i, number in enumerate(data["y"]):
            data["y"][i] = round(number)
    return figure


def round_axis_range(figure: dict) -> dict:
    figure["layout"]["yaxis"]["range"][1] = math.ceil(
        figure["layout"]["yaxis"]["range"][1]
    )
    return figure


def replace_float_in_hovertext(figure: dict) -> dict:
    for data in figure["data"]:
        if "hovertext" in data.keys():
            data["hovertext"] = re.sub(
                "[+-]?([0-9]*[.])?[0-9]+",
                "scrubbed",
                data["hovertext"],
            )
    return figure


def scrub_mapping_saturation_figure(figure: str):
    fig = json.loads(figure)
    fig = round_fitted_y_values(fig)
    fig = replace_float_in_hovertext(fig)
    fig = round_axis_range(fig)
    return json.dumps(fig)

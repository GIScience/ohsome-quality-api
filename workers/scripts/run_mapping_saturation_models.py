"""Run all statistical models of the Mapping Saturation indicator and plot them."""

import asyncio
import pickle
from os.path import exists

import matplotlib.pyplot as plt
import numpy as np
from dacite import from_dict

import ohsome_quality_analyst.geodatabase.client as db_client
import ohsome_quality_analyst.ohsome.client as ohsome_client
from ohsome_quality_analyst.base.indicator import LayerDefinition
from ohsome_quality_analyst.indicators.mapping_saturation.fit import run_all_models
from ohsome_quality_analyst.utils.definitions import get_layer_definition


def plot(xdata, ydata, fitted_models):
    plt.figure()
    prev_ax = None
    for i, model in enumerate(fitted_models):
        if i == 0:
            ax = plt.subplot(2, 3, i + 1)
        else:
            ax = plt.subplot(2, 3, i + 1, sharex=prev_ax, sharey=prev_ax)
        ax.plot(xdata, ydata, label="OSM Data")
        ax.plot(
            xdata,
            model.fitted_values,
            label="{0}: {1}".format(model.metric_name, model.metric),
        )
        ax.axhline(y=model.asymptote, color="pink", linestyle="--", label="Asymptote")
        ax.set_title(model.model_name)
        ax.legend()
        ax.set(xlabel="time", ylabel="features")
        ax.label_outer()
        prev_ax = ax
    plt.show()


async def query_ohsome_api(features, layers) -> list:
    time_range = "2008-01-01//P1M"
    list_of_values = []
    for feature in features:
        for layer in layers:
            query_results = await ohsome_client.query(
                layer=layer, bpolys=feature.geometry, time=time_range
            )
            list_of_values.append([item["value"] for item in query_results["result"]])
    return list_of_values


def get_layers(layer_names) -> list:
    layers = []
    for layer_name in layer_names:
        layers.append(
            from_dict(data_class=LayerDefinition, data=get_layer_definition(layer_name))
        )
    return layers


async def get_features() -> list:
    fids = await db_client.get_feature_ids("regions")
    features = []
    for fid in fids:
        features.append(await db_client.get_feature_from_db("regions", fid))
    return features


if __name__ == "__main__":
    file_path = "data.pkl"
    if exists(file_path):
        with open(file_path, "rb") as f:
            list_of_values = pickle.load(f)
    else:
        features = asyncio.run(get_features())
        layers = get_layers(("building_count", "major_roads_length"))
        list_of_values = asyncio.run(query_ohsome_api(features, layers))
        with open(file_path, "wb") as f:
            pickle.dump(list_of_values, f)
    total_num_of_models = 0
    for values in list_of_values:
        xdata = np.asarray(range(len(values)))
        ydata = np.asarray(values)
        fitted_models = run_all_models(xdata, ydata)
        plot(xdata, ydata, fitted_models)
        total_num_of_models += len(fitted_models)
    print("Expected number of models: " + str(len(list_of_values) * 6))
    print("Total number of models: " + str(total_num_of_models))
    # Expected number of models: 192
    # Total number of models: 143

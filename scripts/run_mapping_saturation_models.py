"""Run all statistical models of the Mapping Saturation indicator and plot them."""

import asyncio
import logging
import pickle
from os.path import exists

import matplotlib.pyplot as plt
import numpy as np
from rpy2.rinterface_lib.embedded import RRuntimeError

import ohsome_quality_api.geodatabase.client as db_client
import ohsome_quality_api.ohsome.client as ohsome_client
from ohsome_quality_api.indicators.mapping_saturation import models
from ohsome_quality_api.topics.definitions import get_topic_preset


def plot(xdata, ydata, model_list):
    plt.figure()
    prev_ax = None
    for i, m in enumerate(model_list):
        if i == 0:
            ax = plt.subplot(2, 3, i + 1)
        else:
            ax = plt.subplot(2, 3, i + 1, sharex=prev_ax, sharey=prev_ax)
        ax.plot(xdata, ydata, label="OSM Data")
        ax.plot(
            xdata,
            m.fitted_values,
            label="Mean Absolute Error: {0}".format(m.mae),
        )
        ax.axhline(y=m.asymptote, color="pink", linestyle="--", label="Asymptote")
        ax.set_title(m.name)
        ax.legend()
        ax.set(xlabel="time", ylabel="features")
        ax.label_outer()
        prev_ax = ax
    plt.show()


async def query_ohsome_api(features, topics) -> list:
    time_range = "2008-01-01//P1M"
    results = []
    for feature in features:
        for topic in topics:
            query_results = await ohsome_client.query(
                topic,
                feature.geometry,
                time=time_range,
            )
            results.append([item["value"] for item in query_results["result"]])
    return results


def get_topics(topic_keys) -> list:
    topics = []
    for topic_key in topic_keys:
        topics.append(get_topic_preset(topic_key))
    return topics


async def get_features() -> list:
    fids = await db_client.get_feature_ids("regions")
    features = []
    for fid in fids:
        features.append(await db_client.get_feature_from_db("regions", fid))
    return features


def run_all_models(list_of_values):
    total_num_of_models = 0
    for val in list_of_values:
        xdata = np.asarray(range(len(val)))
        ydata = np.asarray(val)
        fitted_models = []
        for model in (
            models.Sigmoid,
            models.SSlogis,
            models.SSdoubleS,
            models.SSfpl,
            models.SSasymp,
            models.SSmicmen,
        ):
            logging.info("Run {}".format(model.name))  # noqa
            try:
                fm = model(xdata=xdata, ydata=ydata)
            except RRuntimeError as error:
                logging.warning(  # noqa
                    "Could not run model {0} due to RRuntimeError: {1}".format(
                        model.name, error
                    )
                )
                continue
            if fm.name == "Two-Steps-Sigmoidal Model (Tangens Hyperbolicus)":
                plot(xdata, ydata, [fm])
            if fm.name == "Self-Starting Nls Michaelis-Menten Model":
                param = fm.coefficients["K"]
            elif fm.name == "Self-Starting Nls Asymptotic Regression Model":
                param = (fm.coefficients["asym"] + fm.coefficients["R0"]) / 2
            else:
                param = fm.inflection_point
            xdata_max = len(xdata)
            if xdata_max <= param:
                continue

            avg_last_2_years = np.sum(ydata[-24]) / 24
            if avg_last_2_years >= fm.asym_conf_int[1]:
                continue
            fitted_models.append(fm)
        plot(xdata, ydata, fitted_models)
        total_num_of_models += len(fitted_models)
    print("Expected number of models: " + str(len(list_of_values) * 6))
    print("Total number of models: " + str(total_num_of_models))


if __name__ == "__main__":
    file_path = "data.pkl"
    if exists(file_path):
        with open(file_path, "rb") as f:
            values = pickle.load(f)
    else:
        features_ = asyncio.run(get_features())
        topic_ = get_topics(("building-count", "roads"))
        values = asyncio.run(query_ohsome_api(features_, topic_))
        with open(file_path, "wb") as f:
            pickle.dump(values, f)
    run_all_models(values)

import os
from string import Template

import dateutil.parser
import pandas as pd

# import matplotlib.pyplot as plt
from geojson import Feature

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.raster import client as raster_client
from ohsome_quality_analyst.utils.definitions import get_raster_dataset
from ohsome_quality_analyst.utils.helper import load_sklearn_model


class BuildingArea(BaseIndicator):
    """Building Area Indicator

    Predict the expected building area covering the feature based on population,
    nighttime light, subnational HDI value, and GHS Settlement Model grid using a
    trained random forest regressor. The expected building area is compared to the
    building area mapped in OSM.

    The result depends on the percentage the OSM mapping reaches compared of the
    expected area.

    Args:
        layer_name (str): Layer name has to reference a building area Layer.
            Unit is in meter.
        feature (Feature): GeoJSON Feature object

    """

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            feature=feature,
        )
        self.model_name = ""  # TODO
        self.area = None
        self.building_area = None
        self.predicted_building_area = None
        self.percentage_mapped = None
        self.attrdict = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry
        )
        self.area = await db_client.get_area_of_bpolys(self.feature.geometry)
        self.building_area = query_results["result"][0]["value"]
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

        # get all categorical count values from the SMOD raster
        smod = raster_client.get_zonal_stats(
            self.feature, get_raster_dataset("GHS_SMOD_R2019A"), categorical=True
        )
        # get total pixel count of SMOD raster in order to be able to calculate
        #  percentages per class
        smod_pixelno = raster_client.get_zonal_stats(
            self.feature, get_raster_dataset("GHS_SMOD_R2019A"), stats="count"
        )[0].get("count")

        # write all data required by the regressor into a dict
        self.attrdict = {
            "ghspop": raster_client.get_zonal_stats(
                self.feature, get_raster_dataset("GHS_POP_R2019A"), stats="sum"
            )[0].get("sum")
        }
        self.attrdict["ghspop_density_per_sqkm"] = self.attrdict["ghspop"] / self.area
        # get count per class-value. If unavailable, use '0'
        self.attrdict["water"] = smod[0].get(10, 0) / smod_pixelno
        self.attrdict["very_low_rural"] = smod[0].get(11, 0) / smod_pixelno
        self.attrdict["low_rural"] = smod[0].get(12, 0) / smod_pixelno
        self.attrdict["rural_cluster"] = smod[0].get(13, 0) / smod_pixelno
        self.attrdict["suburban"] = smod[0].get(21, 0) / smod_pixelno
        self.attrdict["semi_dense_urban_cluster"] = smod[0].get(22, 0) / smod_pixelno
        self.attrdict["dense_urban_cluster"] = smod[0].get(23, 0) / smod_pixelno
        self.attrdict["urban_centre"] = smod[0].get(30, 0) / smod_pixelno
        self.attrdict["shdi_mean"] = 0.5  # TODO: implement shdi mean
        self.attrdict["vnl_sum"] = raster_client.get_zonal_stats(
            self.feature, get_raster_dataset("VNL"), stats="sum"
        )[0].get("sum")

    def calculate(self) -> None:
        directory = os.path.dirname(os.path.abspath(__file__))
        scaler = load_sklearn_model(os.path.join(directory, "scaler.joblib"))
        model = load_sklearn_model(os.path.join(directory, "model.joblib"))

        # create a DataFrame from dict, as the regressor was trained with one
        x = pd.DataFrame.from_dict([self.attrdict])

        # define which values in the df must be normalised
        columns_to_normalize = [
            "ghspop",
            "ghspop_density_per_sqkm",
            "vnl_sum",
        ]

        # get the values to be normalized
        values_unnormalized = x[columns_to_normalize].values  # returns a numpy array
        # get normalized values
        values_scaled = scaler.transform(values_unnormalized)
        # insert normalized values in original df
        x[columns_to_normalize] = values_scaled

        # use model to predict building area
        y = model.predict(x)
        self.predicted_building_area = y[0]

        # calculate percentage OSm reached compared to expected value
        self.percentage_mapped = (
            self.building_area / self.predicted_building_area
        ) * 100

        description = Template(self.metadata.result_description).substitute(
            building_area=self.building_area,
            predicted_building_area=self.predicted_building_area,
            percentage_mapped=self.percentage_mapped,
        )
        # TODO: adjust percentage boundaries for green/yellow/red. Adjust in medata.yaml
        #       as well
        if self.percentage_mapped >= 95.0:
            self.result.label = "green"
            self.result.value = 1.0
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        # growth is larger than 3% within last 3 years
        elif 95.0 > self.percentage_mapped >= 75.0:
            self.result.label = "yellow"
            self.result.value = 0.5
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        # growth level is better than the red threshold
        else:
            self.result.label = "red"
            self.result.value = 0.0
            self.result.description = (
                description + self.metadata.label_description["red"]
            )

    def create_figure(self) -> None:
        raise NotImplementedError


# TOOO: define self.model_name (see TODO above)
# TODO: check, whether raster containing no value and therefore indicator should be
#           undefined
# TODO: implement shdi mean querry (see TODO above)
# TODO: discuss & adjust percentage boundaries for green/yellow/red. Adjust values in
#           metadata.yaml as well(see TODO above)
# TODO: discuss: as the regressor is only trained with samples from africa, make it
#           usable for features in africa only?

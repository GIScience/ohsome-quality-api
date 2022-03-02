import logging
import os

from string import Template

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.utils.helper import load_sklearn_model


#TODO: write metadata.yaml

class BuildingArea(BaseIndicator):
    """Building Area Indicator

    TODO: Describe model

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
        self.model_name = ""
        self.building_area = None
        self.predicted_building_area = None
        self.percentage_mapped = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry
        )
        self.building_area = query_results["result"][0]["value"]
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        # TODO: Use rasterstats to retrive data from raster files (Waiting for PR 227)

    def calculate(self) -> None:
        directory = os.path.dirname(os.path.abspath(__file__))
        scaler = load_sklearn_model(os.path.join(directory, "scaler.joblib"))
        model = load_sklearn_model(os.path.join(directory, "model.joblib"))
        # TODO: per data: drop na, normalize, bring in correct form
        """data.dropna(
        subset=[
            "ghspop",
            "ghspop_density_per_sqkm",
            "water",
            "very_low_rural",
            "low_rural",
            "rural_cluster",
            "suburban",
            "semi_dense_urban_cluster",
            "dense_urban_cluster",
            "urban_centre",
            "shdi_mean",
            "vnl_sum",
        ],
        inplace=True,
        
        
        # define which values must be normalised
        columns_to_normalize = [
            "ghspop",
            "ghspop_density_per_sqkm",
            "vnl_sum",
        ]
        # get the values to be normalized
        values_unnormalized = df[columns_to_normalize].values  # returns a numpy array
        # get normalized values
        values_scaled = scaler.transform(values_unnormalized)
        #hier nur methode transform statt fit_transform
        # insert normalized values in original df
        df[columns_to_normalize] = values_scaled
        return (df, min_max_scaler)
        
        
        x = (df_normalised[["ghspop",
            "ghspop_density_per_sqkm",
            "water",
            "very_low_rural",
            "low_rural",
            "rural_cluster",
            "suburban",
            "semi_dense_urban_cluster",
            "dense_urban_cluster",
            "urban_centre",
            "shdi_mean",
            "vnl_sum",]])
        
    )"""

        y = model.predict(x)

        self.predicted_building_area = y

        self.percentage_mapped = (self.predicted_building_area / self.building_area) * 100

        description = Template(self.metadata.result_description).substitute(
            percentage=self.percentage_mapped,
        )
        # TODO set percentage boundaries for green/yellow/red
        if self.percentage_mapped >= 95:
            self.result.label = "green"
            self.result.value = 1.0
            self.result.description = (
                    description + self.metadata.label_description["green"]
            )
        # growth is larger than 3% within last 3 years
        elif 95 > self.percentage_mapped >= 75:
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

        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Buildings per person against people per $km^2$")
        ax.set_xlabel("Population Density [$1/km^2$]")
        ax.set_ylabel("Building Density [$1/km^2$]")

        # Set x max value based on area
        if self.pop_count_per_sqkm < 100:
            max_area = 10
        else:
            max_area = round(self.pop_count_per_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 20)

        # Plot thresholds as line.
        y1 = [self.green_threshold_function(xi) for xi in x]
        y2 = [self.yellow_threshold_function(xi) for xi in x]
        line = line = ax.plot(
            x,
            y1,
            color="black",
            label="Threshold A",
        )
        plt.setp(line, linestyle="--")

        line = ax.plot(
            x,
            y2,
            color="black",
            label="Threshold B",
        )
        plt.setp(line, linestyle=":")

        # Fill in space between thresholds
        ax.fill_between(x, y2, 0, alpha=0.5, color="red")
        ax.fill_between(x, y1, y2, alpha=0.5, color="yellow")
        ax.fill_between(
            x,
            y1,
            max(max(y1), self.feature_count_per_sqkm),
            alpha=0.5,
            color="green",
        )

        # Plot pont as circle ("o").
        ax.plot(
            self.pop_count_per_sqkm,
            self.feature_count_per_sqkm,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")

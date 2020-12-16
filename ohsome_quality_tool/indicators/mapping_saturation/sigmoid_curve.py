import json
import os
import uuid
from typing import Dict, Tuple

import dateutil.parser
import pygal
from geojson import FeatureCollection
import numpy as np
import pandas as pd

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS
from ohsome_quality_tool.utils.label_interpretations import (
    MAPPING_SATURATION_LABEL_INTERPRETATIONS,
)



# sigmoid stuff
class sigmoidCurve():
    """Sigmoid stuff."""
    # sigmoid curve functions inspired by Sven Lautenbach
    # simple logistic curve
    def logistic1(self, x, L, k, x0):
        return L / (1 + np.exp(k * (x - x0)))

    # logistic curve with 2 jumps
    def logistic2(self, x, x2, L, L2, k, k2, x0):
        return L / (1 + np.exp(k * (x - x0))) + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))

    # find initial values for the double curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor2JumpsCurve(self, xdata, ydata):
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties, but xdata could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 5:
            return ([np.nan] * 10)
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]

        flatter = dydata < dydata.mean()
        boundaries = np.hstack([np.array(False), np.diff(flatter.astype(int)).astype(
            bool)])  # hstack is because boundaries needs to be the same length as flatter; np.diff will be one short
        try:  # These seems to work on every case except non-changing ydata (with one change only)
            iBoundaries = flatter[boundaries].index  # This is where slope changes (crosses) its mean value
            # Here is the index from which (inclusive) we should start masking away:, ie  ind the latest boundary before our jump, and the first following it:
            startMask, endMask = iBoundaries[iBoundaries < xjump1.index.values[0]].max(), iBoundaries[
                iBoundaries > xjump1.index.values[0]].min()
            dydata.iloc[startMask:endMask] = 0  # This zeros out the slope on a contiguous region around our first jump.

            xjump2 = xdata.shift(1)[dydata == dydata.max()]
            dy2 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually really pathalogical.
            xjump2 = xjump1
            dy2 = dy1

        try:  # These seems to work on every case except non-changing ydata (with one change only)
            iBoundaries = flatter[boundaries].index  # This is where slope changes (crosses) its mean value
            # Here is the index from which (inclusive) we should start masking away:, ie  ind the latest boundary before our jump, and the first following it:
            startMask, endMask = iBoundaries[iBoundaries < xjump2.index.values[0]].max(), iBoundaries[
                iBoundaries > xjump2.index.values[0]].min()
            dydata.iloc[startMask:endMask] = 0  # This zeros out the slope on a contiguous region around our first jump.

            xjump3 = xdata.shift(1)[dydata == dydata.max()]
            dy3 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually really pathalogical.
            xjump3 = xjump2
            dy3 = dy2
        return (
            [(min(xdata) + max(xdata)) / 2.0, 10.0 / (max(xdata) - min(xdata)), min(ydata), max(ydata), xjump1.values[0],
            dy1.values[0], xjump2.values[0], dy2.values[0], xjump3.values[0], dy3.values[0]])

    # don't know why, result of initparamsFor2JumpsCurve() is not sorted
    def sortInits2curves(self, xdata, ydata):
        inits = self.initparamsFor2JumpsCurve(xdata, ydata)
        allL = []
        lx = []
        ly = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
                ly.append(inits[i + 1])

        x = sorted(lx)
        y = sorted(ly)

        allL.append(x[0])
        allL.append(y[0])
        allL.append(x[1])
        allL.append(y[1])
        allL.append(x[2])
        allL.append(y[2])

        result = []
        x2 = x[0] + ((x[1] - x[0]) / 2)
        y2 = y[0] + ((y[1] - y[0]) / 2)

        result.append(x2)
        result.append(inits[3] - y2)
        result.append(x[2])
        result.append(inits[3])

        return result, x, y, inits[0], inits[2]

    # TODO define initparamsFor2JumpsCurve(self, xdata, ydata) and sortInits2curves(self, xdata, ydata) for other
    # sigmoid functions, too

    # logistic curve with 3 jumps
    def logistic3(self, x, x2, x3, L, L2, L3, k, k2, k3, x0):
        return L / (1 + np.exp(k * (x - x0))) + (L2 - L) / (1 + np.exp(k2 * (x2 - x0))) + (L3 - L2) / (
                    1 + np.exp(k3 * (x3 - x0)))

    # logistic curve with 4 jumps
    def logistic4(self, x, x2, x3, x4, L, L2, L3, L4, k, k2, k3, k4, x0):
        return (L / (1 + np.exp(k * (x - x0))) + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))
                + (L3 - L2) / (1 + np.exp(k3 * (x3 - x0))) + (L4 - L3) / (1 + np.exp(k4 * (x4 - x0))))

    # logistic curve with 5 jumps
    def logistic5(self, x, x2, x3, x4, x5, L, L2, L3, L4, L5, k, k2, k3, k4, k5, x0):
        return (L / (1 + np.exp(k * (x - x0))) + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))
                + (L3 - L2) / (1 + np.exp(k3 * (x3 - x0))) + (L4 - L3) / (1 + np.exp(k4 * (x4 - x0))) + (L5 - L4) / (
                            1 + np.exp(k5 * (x5 - x0))))

    # get gradient/slope in last 3 years of the logistic curve
    # pass as ydata the sigmoid function with init params logistic2(110, 135, 10000, 28900, 0.3, 0.3, df1.li)
    def getSaturationInLast3Years(self, earlyX, lastX, xdata, ydata):
        earlyY = np.interp(earlyX, xdata, ydata)
        lastY = np.interp(lastX, xdata, ydata)
        return (earlyY / lastY)

    # in a single sigmoid curve get estimated y values for start and end of growth
    def getFirstLastY(self, inits):
        yList = [inits[5], inits[7], inits[9]]
        yList = sorted(yList)
        return yList
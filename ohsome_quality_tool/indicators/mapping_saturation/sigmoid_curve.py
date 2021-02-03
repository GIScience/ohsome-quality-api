import math
from typing import Dict

import numpy as np
import pandas as pd


class sigmoidCurve:
    """Calculate different sigmoid curves and
    find the best fitting one."""

    # get the y values where one curve ends and the next begins,
    # there where the data show sth like a plateau
    def getYvaluesAtPlateaus(self, x, xdata, ydata) -> list:
        yValsAtPlateaus = []
        # x = list of xmid values
        for i, xVal in enumerate(x):
            # collect y values for start/end of curves
            if i <= len(x) - 1:
                # for last xmid in list
                if i == len(x) - 1:
                    # xbtw: check the "distance" to next xmid and
                    # get a possible y of start/end of curves
                    xbtw = max(xdata) - xVal
                    if xbtw > 17:
                        yAtX = np.interp(xVal + 15, xdata, ydata)
                    elif 10 < xbtw <= 17:
                        yAtX = np.interp(xVal + 8, xdata, ydata)
                    elif 4 < xbtw <= 10:
                        yAtX = np.interp(xVal + 3, xdata, ydata)
                    elif 2 < xbtw <= 4:
                        yAtX = np.interp(xVal + 1, xdata, ydata)
                    else:
                        # next xmid to near, ignore
                        yAtX = np.interp(xVal, xdata, ydata)
                    yValsAtPlateaus.append(yAtX)
                # all other xmids
                else:
                    # xbtw: check the "distance" to next xmid and
                    # get a possible y of start/end of curves
                    xbtw = x[i + 1] - x[i]
                    if xbtw > 17:
                        yAtX = np.interp(xVal + 15, xdata, ydata)
                    elif 10 < xbtw <= 17:
                        yAtX = np.interp(xVal + 8, xdata, ydata)
                    elif 4 < xbtw <= 10:
                        yAtX = np.interp(xVal + 3, xdata, ydata)
                    elif 2 < xbtw <= 4:
                        yAtX = np.interp(xVal + 1, xdata, ydata)
                    else:
                        # next xmid to near, ignore
                        yAtX = np.interp(xVal, xdata, ydata)
                    yValsAtPlateaus.append(yAtX)
        return yValsAtPlateaus

    # get the y value at the beginning of the curve, but not 0
    def getYatCurveStart(self, xmids, xdata, ydata) -> float:
        # check the distance between first xmid and x=0
        # and define a x value in between to get a
        # start y value!=0
        # assumption: between first xmid and x=0 data have
        # been mapped, if not, there wuld not be a xmid
        # so y will be > 0
        if 10 < xmids[0] < 15:
            ystart = np.interp(xmids[0] - 8, xdata, ydata)
        elif 5 < xmids[0] < 10:
            ystart = np.interp(xmids[0] - 4, xdata, ydata)
        # TODO what if first xmid is much higher than eg 20?
        elif xmids[0] >= 15:
            ystart = np.interp(xmids[0] - 15, xdata, ydata)
        else:
            # first xmid is very close to x=0, eg import
            ystart = np.interp(xmids[0] - 0.5, xdata, ydata)
        return ystart

    # sigmoid curve functions inspired by Sven Lautenbach
    # simple logistic curve
    def logistic1(self, xmid, ymax, slope, x) -> float:
        # ymax: max(y-value) / asymptote
        # slope: slope, growth rate
        # x: x value
        # xmid: x value of midpoint of sigmoid curve
        return ymax / (1 + np.exp(slope * (xmid - x)))

    # init params for single curve returns x0, k,miny,maxy, xjump1,dy1
    def initparamsingle(self, xdata, ydata) -> list:
        # Find the steepest single step
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 4:
            return [np.nan] * 6
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        # to have an other x0 than min(x) and max(x)
        minx = min(xdata) + (xjump1.values[0] / 2)
        maxx = xjump1.values[0] + ((max(xdata) - xjump1.values[0]) / 2)
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (maxx - minx),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
        ]

    # init params for single curve returns x0, k,miny,maxy, xjump1,dy1
    def initparamsingleB(self, xdata, ydata) -> list:
        # Find the steepest single step
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 4:
            return [np.nan] * 6
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (max(xdata) - min(xdata)),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
        ]

    # logistic curve with 2 jumps
    def logistic2(self, xmid, xmid2, ymax, ymax2, slope, slope2, x) -> float:
        # ymax, ymax2: max(y-value) / asymptote
        # slope, slope2: slope, growth rate
        # x: x value
        # xmid, xmid2: x value of midpoint of sigmoid curve
        return ymax / (1 + np.exp(slope * (xmid - x))) + (ymax2 - ymax) / (
            1 + np.exp(slope2 * (xmid2 - x))
        )

    # find initial values for the double curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor2JumpsCurve(self, xdata, ydata) -> list:
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties,
        # but xdata could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 4:
            return [np.nan] * 8
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        flatter = dydata < dydata.mean()
        boundaries = np.hstack(
            [np.array(False), np.diff(flatter.astype(int)).astype(bool)]
        )
        # hstack is because boundaries needs to be the same
        # length as flatter
        # np.diff will be one short
        # These seems to work on every case except non-changing ydata
        # (with one change only)
        try:
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive)
            # we should start masking away:
            # ie  ind the latest boundary before our jump,
            # and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump1.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump1.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[startMask:endMask] = 0
            # This zeros out the slope on a contiguous
            # region around our first jump.
            xjump2 = xdata.shift(1)[dydata == dydata.max()]
            dy2 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump2 = xjump1
            dy2 = dy1
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (max(xdata) - min(xdata)),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
            xjump2.values[0],
            dy2.values[0],
        ]

    # don't know why, result of initparamsFor2JumpsCurve() is not sorted
    def sortInits2curves(self, xdata, ydata) -> tuple:
        inits = self.initparamsFor2JumpsCurve(xdata, ydata)
        lx = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
        # list of x values of mid points of the curves
        xmids = sorted(lx)
        # y values at start/end of curves
        yValsAtPlateaus = self.getYvaluesAtPlateaus(xmids, xdata, ydata)
        # highest y value
        ymax = inits[3]
        # y value at the beginning of data history
        ystart = self.getYatCurveStart(xmids, xdata, ydata)
        return xmids, yValsAtPlateaus, ymax, ystart

    # logistic curve with 3 jumps
    def logistic3(
        self, xmid, xmid2, xmid3, ymax, ymax2, ymax3, slope, slope2, slope3, x
    ):
        # ymax, ymax2, ymax3: max(y-value) / asymptote
        # slope, slope2, slope3: slope, growth rate
        # x: x value
        # xmid, xmid2, xmid3: x value of midpoint of sigmoid curve
        return (
            ymax / (1 + np.exp(slope * (xmid - x)))
            + (ymax2 - ymax) / (1 + np.exp(slope2 * (xmid2 - x)))
            + (ymax3 - ymax2) / (1 + np.exp(slope3 * (xmid3 - x)))
        )

    # find initial values for the triple curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor3JumpsCurve(self, xdata, ydata) -> list:
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties, but
        # xdata could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 5:
            return [np.nan] * 10
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]

        flatter = dydata < dydata.mean()
        boundaries = np.hstack(
            [np.array(False), np.diff(flatter.astype(int)).astype(bool)]
        )  # hstack is because boundaries needs to be the same length
        # as flatter; np.diff will be one short
        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive) we
            # should start masking away:,
            # ie  ind the latest boundary before our jump, and
            # the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump1.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump1.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous region
            # around our first jump.
            xjump2 = xdata.shift(1)[dydata == dydata.max()]
            dy2 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump2 = xjump1
            dy2 = dy1

        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive)
            # we should start masking away:,
            # ie  ind the latest boundary before our jump,
            # and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump2.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump2.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous
            # region around our first jump.
            xjump3 = xdata.shift(1)[dydata == dydata.max()]
            dy3 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump3 = xjump2
            dy3 = dy2
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (max(xdata) - min(xdata)),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
            xjump2.values[0],
            dy2.values[0],
            xjump3.values[0],
            dy3.values[0],
        ]

    # don't know why, result of
    # initparamsFor3JumpsCurve() is not sorted
    def sortInits3curves(self, xdata, ydata, func) -> tuple:
        inits = func(xdata, ydata)
        lx = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
        # list of x values of mid points of the curves
        x = sorted(lx)
        # y values at start/end of curves
        yValsAtPlateaus = self.getYvaluesAtPlateaus(x, xdata, ydata)
        # highest y value
        ymax = inits[3]
        # y value at the beginning of data history
        ystart = self.getYatCurveStart(x, xdata, ydata)
        return x, yValsAtPlateaus, ymax, ystart

    # logistic curve with 4 jumps
    def logistic4(
        self,
        xmid,
        xmid2,
        xmid3,
        xmid4,
        ymax,
        ymax2,
        ymax3,
        ymax4,
        slope,
        slope2,
        slope3,
        slope4,
        x,
    ) -> float:
        # ymax - ymax4: max(y-value) / asymptote
        # slope - slope4: slope, growth rate
        # x: x value
        # xmid - xmid4: x value of midpoint of sigmoid curve
        return (
            ymax / (1 + np.exp(slope * (xmid - x)))
            + (ymax2 - ymax) / (1 + np.exp(slope2 * (xmid2 - x)))
            + (ymax3 - ymax2) / (1 + np.exp(slope3 * (xmid3 - x)))
            + (ymax4 - ymax3) / (1 + np.exp(slope4 * (xmid4 - x)))
        )

    # find initial values for the 4jumps curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor4JumpsCurve(self, xdata, ydata) -> list:
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties, but
        # xdata could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 6:
            return [np.nan] * 12
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]

        flatter = dydata < dydata.mean()
        boundaries = np.hstack(
            [np.array(False), np.diff(flatter.astype(int)).astype(bool)]
        )  # hstack is because boundaries needs to be the same length
        # as flatter; np.diff will be one short
        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive) we
            # should start masking away:,
            # ie  ind the latest boundary before our jump, and
            # the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump1.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump1.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous region
            # around our first jump.
            xjump2 = xdata.shift(1)[dydata == dydata.max()]
            dy2 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump2 = xjump1
            dy2 = dy1

        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive)
            # we should start masking away:,
            # ie  ind the latest boundary before our jump,
            # and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump2.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump2.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous
            # region around our first jump.
            xjump3 = xdata.shift(1)[dydata == dydata.max()]
            dy3 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump3 = xjump2
            dy3 = dy2
        try:  # These seems to work on every case except non-changing ydata
            # (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses) its mean value
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump3.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump3.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[startMask:endMask] = 0
            xjump4 = xdata.shift(1)[dydata == dydata.max()]
            dy4 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1, 2]  # This is
            # actually really pathalogical.
            xjump4 = xjump3
            dy4 = dy3
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (max(xdata) - min(xdata)),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
            xjump2.values[0],
            dy2.values[0],
            xjump3.values[0],
            dy3.values[0],
            xjump4.values[0],
            dy4.values[0],
        ]

    # logistic curve with 5 jumps
    def logistic5(
        self,
        xmid,
        xmid2,
        xmid3,
        xmid4,
        xmid5,
        ymax,
        ymax2,
        ymax3,
        ymax4,
        ymax5,
        slope,
        slope2,
        slope3,
        slope4,
        slope5,
        x,
    ) -> float:
        # ymax - ymax5: max(y-value) / asymptote
        # slope - slope5: slope, growth rate
        # x: x value
        # xmid - xmid5: x value of midpoint of sigmoid curve
        return (
            ymax / (1 + np.exp(slope * (xmid - x)))
            + (ymax2 - ymax) / (1 + np.exp(slope2 * (xmid2 - x)))
            + (ymax3 - ymax2) / (1 + np.exp(slope3 * (xmid3 - x)))
            + (ymax4 - ymax3) / (1 + np.exp(slope4 * (xmid4 - x)))
            + (ymax5 - ymax4) / (1 + np.exp(slope5 * (xmid5 - x)))
        )

    """ can not take initparamsFor5JumpsCurve to calculate
    the intitial values for all curves (single,
    with 2 jumps, 3 jumps, ...) because for example the curve
    with 2 jumps takes not the first 2
    results of initparamsFor5JumpsCurve, but the first and the
    third.
    Can also not use sortInits5curves for all other curves,
    because sometimes one y value differs between
    yValsAtPlateaus calculates for 3+4 jumps curve and 5 jumps curve."""

    # find initial values for the triple curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor5JumpsCurve(self, xdata, ydata) -> list:
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties, but xdata
        # could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 7:
            return [np.nan] * 14
        xjump1 = xdata.shift(1)[dydata == dydata.max()]
        dy1 = (ydata - ydata.shift(1))[dydata == dydata.max()]

        flatter = dydata < dydata.mean()
        boundaries = np.hstack(
            [np.array(False), np.diff(flatter.astype(int)).astype(bool)]
        )  # hstack is because boundaries needs to be the same length as
        # flatter; np.diff will be one short
        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses) its
            # mean value
            # Here is the index from which (inclusive) we should
            # start masking
            # away:, ie  ind the latest boundary before our
            # jump, and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump1.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump1.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous
            # region around our first jump.
            xjump2 = xdata.shift(1)[dydata == dydata.max()]
            dy2 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump2 = xjump1
            dy2 = dy1

        try:  # These seems to work on every case except
            # non-changing ydata
            # (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive)
            # we should start
            # masking away:, ie  ind the latest boundary
            # before our jump,
            # and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump2.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump2.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[
                startMask:endMask
            ] = 0  # This zeros out the slope on a contiguous
            # region around our first jump.
            xjump3 = xdata.shift(1)[dydata == dydata.max()]
            dy3 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1]  # This is actually
            # really pathalogical.
            xjump3 = xjump2
            dy3 = dy2
        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump3.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump3.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[startMask:endMask] = 0
            xjump4 = xdata.shift(1)[dydata == dydata.max()]
            dy4 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1, 2]  # This is actually
            # really pathalogical.
            xjump4 = xjump3
            dy4 = dy3
        try:  # These seems to work on every case except non-changing
            # ydata (with one change only)
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump4.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump4.index.values[0]].min(),
            )
            # ToDo is this the right way to avoid "slice indices must be
            #  integers or None or have an __index__ method?"
            if math.isnan(startMask):
                startMask = None
            if math.isnan(endMask):
                endMask = None
            dydata.iloc[startMask:endMask] = 0
            xjump5 = xdata.shift(1)[dydata == dydata.max()]
            dy5 = (ydata - ydata.shift(1))[dydata == dydata.max()]
        except AttributeError:
            assert sum(boundaries) in [1, 2]  # This is actually
            # really pathalogical.
            xjump5 = xjump4
            dy5 = dy4
        return [
            (min(xdata) + max(xdata)) / 2.0,
            10.0 / (max(xdata) - min(xdata)),
            min(ydata),
            max(ydata),
            xjump1.values[0],
            dy1.values[0],
            xjump2.values[0],
            dy2.values[0],
            xjump3.values[0],
            dy3.values[0],
            xjump4.values[0],
            dy4.values[0],
            xjump5.values[0],
            dy5.values[0],
        ]

    # don't know why, result of initparamsFor5JumpsCurve() is not sorted
    def sortInits5curves(self, xdata, ydata) -> tuple:
        inits = self.initparamsFor5JumpsCurve(xdata, ydata)
        lx = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
        # list of x values of mid points of the curves
        x = sorted(lx)
        # y values at start/end of curves
        yValsAtPlateaus = self.getYvaluesAtPlateaus(x, xdata, ydata)
        # y value at the beginning of data history
        ystart = self.getYatCurveStart(x, xdata, ydata)
        # highest y value
        ymax = inits[3]
        return x, yValsAtPlateaus, ymax, ystart

    # get gradient/slope in last 3 years of the logistic curve
    # pass as ydata the sigmoid function with init params
    # logistic2(110, 135, 10000, 28900, 0.3, 0.3, df1.li)
    def getSaturationInLast3Years(self, earlyX, lastX, xdata, ydata) -> float:
        earlyY = np.interp(earlyX, xdata, ydata)
        lastY = np.interp(lastX, xdata, ydata)
        return earlyY / lastY

    def getBestFittingCurve(self, preprocessing_results: Dict) -> float:
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)
        # calculate traffic light value
        df1 = pd.DataFrame(
            {
                "timestamps": preprocessing_results["timestamps"],
                "yValues": preprocessing_results["results"],
                "li": li,
            }
        )
        # collect mse in one list
        errorslist = []
        # collect corresponding function names
        errorslistFuncs = [
            "logistic1",
            "logistic1B",
            "logistic2",
            "logistic3",
            "logistic4",
            "logistic5",
        ]
        # get init params for sigmoid curve with 2 jumps
        sigmoid_curve = sigmoidCurve()
        # initial values for the single sigmoid curve
        initParamsSingle = sigmoid_curve.initparamsingle(df1.li, df1.yValues)
        if not math.isnan(initParamsSingle[3]):
            # get possible xmids
            xmidvalues = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
            errorsListSingle = []
            # check for the xmids the mse error
            for i, xval in enumerate(xmidvalues):
                yPredX = sigmoid_curve.logistic1(
                    xval, initParamsSingle[3], initParamsSingle[1], df1.li
                )
                errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
                errorsListSingle.append(errX)
            # choose the initial x value with min mse
            minX = min(errorsListSingle)
            prefX = xmidvalues[errorsListSingle.index(minX)]
            # mse for logistic1
            # with k as 10.0 / (maxx - minx) from initparamsingle()
            yPredPref = sigmoid_curve.logistic1(
                prefX, initParamsSingle[3], initParamsSingle[1], df1.li
            )
            err1 = np.sum((yPredPref - df1.yValues) ** 2) / len(yPredPref)
            errorslist.append(err1)
            errorslistFuncs.append("logistic1")
        # initial values for the single sigmoid curve with a different slope
        initParamsSingleB = sigmoid_curve.initparamsingleB(df1.li, df1.yValues)
        if not math.isnan(initParamsSingleB[3]):
            # get possible xmids
            xmidvalues = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
            errorsListSingle = []
            # check for the xmids the mse error
            for i, xval in enumerate(xmidvalues):
                yPredX = sigmoid_curve.logistic1(
                    xval, initParamsSingle[3], initParamsSingle[1], df1.li
                )
                errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
                errorsListSingle.append(errX)
            # choose the initial x value with min mse
            minX = min(errorsListSingle)
            prefX = xmidvalues[errorsListSingle.index(minX)]
            # mse for logistic1 with
            # k as 10.0 / (max(xdata) - min(xdata)) from initparamsingleB()
            yPredB = sigmoid_curve.logistic1(
                prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
            )
            err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)
            errorslist.append(err1B)
            errorslistFuncs.append("logistic1B")
        # initial values for the sigmoid function with 2 jumps
        initParamsY = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[1]
        if not math.isnan(initParamsY[0]):
            L = round(initParamsY[0])
            initParamsX = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[0]
            x1 = round(initParamsX[0])
            x2 = round(initParamsX[1])
            # get initial slopes for the curve with 2 jumps
            ystart2 = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[3]
            k1 = 1 - (ystart2 / initParamsY[0])
            k2 = 1 - (initParamsY[0] / initParamsY[1])
            # get the max y value
            yMax = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[2]
            # mse for logistic2
            yPred2 = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
            err2 = np.sum((yPred2 - df1.yValues) ** 2) / len(yPred2)
            errorslist.append(err2)
            errorslistFuncs.append("logistic2")
        # --- sigmoid function with 3  jumps---
        # get initial y values for the curve with 3
        initParamsY3 = sigmoid_curve.sortInits3curves(
            df1.li, df1.yValues, self.initparamsFor3JumpsCurve
        )[1]
        if not math.isnan(initParamsY3[0]):
            L3 = round(initParamsY3[0])
            L23 = round(initParamsY3[1])
            # get initial xmids for the curve with 3
            initParamsX3 = sigmoid_curve.sortInits3curves(
                df1.li, df1.yValues, self.initparamsFor3JumpsCurve
            )[0]
            x13 = round(initParamsX3[0])
            x23 = round(initParamsX3[1])
            x33 = round(initParamsX3[2])
            # get initial slopes for the curves with 3
            ystart3 = sigmoid_curve.sortInits3curves(
                df1.li, df1.yValues, self.initparamsFor3JumpsCurve
            )[3]
            k313 = 1 - (ystart3 / initParamsY3[0])
            k323 = 1 - (initParamsY3[0] / initParamsY3[1])
            k333 = 1 - (initParamsY3[1] / initParamsY3[2])
            # mse for logistic3
            yPred3 = sigmoid_curve.logistic3(
                x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
            )
            err3 = np.sum((yPred3 - df1.yValues) ** 2) / len(yPred3)
            errorslist.append(err3)
            errorslistFuncs.append("logistic3")
        # --- sigmoid function with 4 jumps ---
        # get initial y values for the curve with 4 jumps
        initParamsY4 = sigmoid_curve.sortInits3curves(
            df1.li, df1.yValues, self.initparamsFor4JumpsCurve
        )[1]
        if not math.isnan(initParamsY3[0]):
            L41 = round(initParamsY4[0])
            L42 = round(initParamsY4[1])
            L43 = round(initParamsY4[2])
            # get initial xmids for the curve with 4 jumps
            initParamsX4 = sigmoid_curve.sortInits3curves(
                df1.li, df1.yValues, self.initparamsFor4JumpsCurve
            )[0]
            x41 = round(initParamsX4[0])
            x42 = round(initParamsX4[1])
            x43 = round(initParamsX4[2])
            x44 = round(initParamsX4[3])
            # get initial slopes for the curves with 4 jumps
            ystart4 = sigmoid_curve.sortInits3curves(
                df1.li, df1.yValues, self.initparamsFor4JumpsCurve
            )[3]
            k41 = 1 - (ystart4 / initParamsY4[0])
            k42 = 1 - (initParamsY4[0] / initParamsY4[1])
            k43 = 1 - (initParamsY4[1] / initParamsY4[2])
            k44 = 1 - (initParamsY4[2] / initParamsY4[3])
            # mse for logistic4
            yPred4 = sigmoid_curve.logistic4(
                x41, x42, x43, x44, L41, L42, L43, yMax, k41, k42, k43, k44, df1.li
            )
            err4 = np.sum((yPred4 - df1.yValues) ** 2) / len(yPred4)
            errorslist.append(err4)
            errorslistFuncs.append("logistic4")
        # --- sigmoid function with 5 jumps ---
        initParamsY5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[1]
        if not math.isnan(initParamsY3[0]):
            # get initial y values for the curve with 5 jumps
            L51 = round(initParamsY5[0])
            L52 = round(initParamsY5[1])
            L53 = round(initParamsY5[2])
            L54 = round(initParamsY5[3])
            # get initial xmids for the curve with 5 jumps
            initParamsX5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
            x513 = round(initParamsX5[0])
            x523 = round(initParamsX5[1])
            x533 = round(initParamsX5[2])
            x54 = round(initParamsX5[3])
            x55 = round(initParamsX5[4])
            # get initial slopes for the curve with 5 jumps
            ystart5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[3]
            k13 = 1 - (ystart5 / initParamsY5[0])
            k23 = 1 - (initParamsY5[0] / initParamsY5[1])
            k33 = 1 - (initParamsY5[1] / initParamsY5[2])
            k4 = 1 - (initParamsY5[2] / initParamsY5[3])
            k5 = 1 - (initParamsY5[3] / initParamsY5[4])
            # --- select best fitting curve, with mean_square_error ---
            # mse for logistic5
            yPred5 = sigmoid_curve.logistic5(
                x513,
                x523,
                x533,
                x54,
                x55,
                L51,
                L52,
                L53,
                L54,
                yMax,
                k13,
                k23,
                k33,
                k4,
                k5,
                df1.li,
            )
            err5 = np.sum((yPred5 - df1.yValues) ** 2) / len(yPred5)
            errorslist.append(err5)
            errorslistFuncs.append("logistic5")
        if len(errorslist) > 0:
            # get the smallest mse with its index
            minError = errorslist.index(min(errorslist))
            bestfit = errorslistFuncs[minError]
            # depending on best fitted curve calculate ydata with
            # correct function
            if bestfit == "logistic2":
                ydataForSat = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
            elif bestfit == "logistic1":
                ydataForSat = sigmoid_curve.logistic1(
                    prefX, initParamsSingle[3], initParamsSingle[1], df1.li
                )
            elif bestfit == "logistic1B":
                ydataForSat = sigmoid_curve.logistic1(
                    prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
                )
            elif bestfit == "logistic3":
                ydataForSat = sigmoid_curve.logistic3(
                    x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
                )
            elif bestfit == "logistic4":
                ydataForSat = sigmoid_curve.logistic4(
                    x41,
                    x42,
                    x43,
                    x44,
                    L41,
                    L42,
                    L43,
                    yMax,
                    k41,
                    k42,
                    k43,
                    k44,
                    df1.li,
                )
            elif bestfit == "logistic5":
                ydataForSat = sigmoid_curve.logistic5(
                    x513,
                    x523,
                    x533,
                    x54,
                    x55,
                    L51,
                    L52,
                    L53,
                    L54,
                    yMax,
                    k13,
                    k23,
                    k33,
                    k4,
                    k5,
                    df1.li,
                )
            return ydataForSat
        else:
            # no curve could be calculated
            return ["empty"]

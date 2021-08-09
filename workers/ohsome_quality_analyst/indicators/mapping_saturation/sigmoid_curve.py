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
        """
        Get the y values where one curve ends and the next begins,
        there where the data show sth like a plateau
        """
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
                        # next xmid too near, ignore
                        yAtX = np.interp(xVal, xdata, ydata)
                    yValsAtPlateaus.append(yAtX)
        return yValsAtPlateaus

    # get the y value at the beginning of the curve, but not 0
    def getYatCurveStart(self, xmids, xdata, ydata) -> float:
        """
        get the y value at the beginning of the curve, but not 0
        """
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

    # if one of the values to calculate the slope for the curve
    # is 0, 1 should be returned
    def getSlopeAndHandleZeros(self, value1, value2) -> float:
        """
        if one of the values to calculate the slope for the curve
        is 0, 1 should be returned
        """
        if value1 == 0 or value2 == 0:
            return 1
        else:
            return 1 - (value1 / value2)

    def nanToZero(self, value1) -> float:
        """
        if NaN value still left, turn them into 0
        """
        if math.isnan(value1):
            return 0
        else:
            return value1

    # function that calculates the curve params after eliminating
    # nan values in initparams, so it might be, that if initparams
    # for 5 curves were calculated but nan was deleted, curve params
    # for 4 jumps will then be chosen
    def calculateCurveParams(self, initParamsY, xvalues, yvalues):
        """
        function that calculates the curve params (not single sigmoid
        curve) after eliminating
        nan values in initparams, so it might be, that if initparams
        for 5 curves were calculated but nan was deleted, curve params
        for 4 jumps will then be chosen
        """
        # ToDo assuming if in y list is a nan value, in the x
        #  list at the same place are nan values,
        #  what if this is not true? are the corresponding
        #  y and x values taken for curve calculation?
        incoms = [incom for incom in initParamsY if str(incom) != "nan"]
        if len(incoms) == 2:
            L = round(self.nanToZero(initParamsY[0]))
            initParamsX = self.sortInits2curves(xvalues, yvalues)[0]
            x1 = round(self.nanToZero(initParamsX[0]))
            x2 = round(self.nanToZero(initParamsX[1]))
            # get initial slopes for the curve with 2 jumps
            ystart2 = self.sortInits2curves(xvalues, yvalues)[3]
            k1 = self.getSlopeAndHandleZeros(ystart2, initParamsY[0])
            k2 = self.getSlopeAndHandleZeros(initParamsY[0], initParamsY[1])
            # get the max y value
            yMax = self.sortInits2curves(xvalues, yvalues)[2]
            # mse for logistic2
            yPred2 = self.logistic2(x1, x2, L, yMax, k1, k2, xvalues)
            err2 = np.sum((yPred2 - yvalues) ** 2) / len(yPred2)
            params = [x1, x2, L, yMax, k1, k2]
            return err2, params
        if len(incoms) == 3:
            L3 = round(self.nanToZero(initParamsY[0]))
            L23 = round(self.nanToZero(initParamsY[1]))
            # get initial xmids for the curve with 3
            initParamsX3 = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor3JumpsCurve
            )[0]
            x13 = round(self.nanToZero(initParamsX3[0]))
            x23 = round(self.nanToZero(initParamsX3[1]))
            x33 = round(self.nanToZero(initParamsX3[2]))
            # get initial slopes for the curves with 3
            ystart3 = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor3JumpsCurve
            )[3]
            k313 = self.getSlopeAndHandleZeros(ystart3, initParamsY[0])
            k323 = self.getSlopeAndHandleZeros(initParamsY[0], initParamsY[1])
            k333 = self.getSlopeAndHandleZeros(initParamsY[1], initParamsY[2])
            # get the max y value
            yMax = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor3JumpsCurve
            )[2]
            # mse for logistic3
            yPred3 = self.logistic3(
                x13, x23, x33, L3, L23, yMax, k313, k323, k333, xvalues
            )
            err3 = np.sum((yPred3 - yvalues) ** 2) / len(yPred3)
            params = [x13, x23, x33, L3, L23, yMax, k313, k323, k333]
            return err3, params
        if len(incoms) == 4:
            L41 = round(self.nanToZero(initParamsY[0]))
            L42 = round(self.nanToZero(initParamsY[1]))
            L43 = round(self.nanToZero(initParamsY[2]))
            # get initial xmids for the curve with 4 jumps
            initParamsX4 = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor4JumpsCurve
            )[0]
            x41 = round(self.nanToZero(initParamsX4[0]))
            x42 = round(self.nanToZero(initParamsX4[1]))
            x43 = round(self.nanToZero(initParamsX4[2]))
            x44 = round(self.nanToZero(initParamsX4[3]))
            # get initial slopes for the curves with 4 jumps
            ystart4 = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor4JumpsCurve
            )[3]
            k41 = self.getSlopeAndHandleZeros(ystart4, initParamsY[0])
            k42 = self.getSlopeAndHandleZeros(initParamsY[0], initParamsY[1])
            k43 = self.getSlopeAndHandleZeros(initParamsY[1], initParamsY[2])
            k44 = self.getSlopeAndHandleZeros(initParamsY[2], initParamsY[3])
            # get the max y value
            yMax = self.sortInits3curves(
                xvalues, yvalues, self.initparamsFor4JumpsCurve
            )[2]
            # mse for logistic4
            yPred4 = self.logistic4(
                x41, x42, x43, x44, L41, L42, L43, yMax, k41, k42, k43, k44, xvalues
            )
            err4 = np.sum((yPred4 - yvalues) ** 2) / len(yPred4)
            params = [x41, x42, x43, x44, L41, L42, L43, yMax, k41, k42, k43, k44]
            return err4, params
        if len(incoms) == 5:
            # get initial y values for the curve with 5 jumps
            L51 = round(self.nanToZero(initParamsY[0]))
            L52 = round(self.nanToZero(initParamsY[1]))
            L53 = round(self.nanToZero(initParamsY[2]))
            L54 = round(self.nanToZero(initParamsY[3]))
            # get initial xmids for the curve with 5 jumps
            initParamsX5 = self.sortInits5curves(xvalues, yvalues)[0]
            x513 = round(self.nanToZero(initParamsX5[0]))
            x523 = round(self.nanToZero(initParamsX5[1]))
            x533 = round(self.nanToZero(initParamsX5[2]))
            x54 = round(self.nanToZero(initParamsX5[3]))
            x55 = round(self.nanToZero(initParamsX5[4]))
            # get initial slopes for the curve with 5 jumps
            ystart5 = self.sortInits5curves(xvalues, yvalues)[3]
            k13 = self.getSlopeAndHandleZeros(ystart5, initParamsY[0])
            k23 = self.getSlopeAndHandleZeros(initParamsY[0], initParamsY[1])
            k33 = self.getSlopeAndHandleZeros(initParamsY[1], initParamsY[2])
            k4 = self.getSlopeAndHandleZeros(initParamsY[2], initParamsY[3])
            k5 = self.getSlopeAndHandleZeros(initParamsY[3], initParamsY[4])
            # --- select best fitting curve, with mean_square_error ---
            # get the max y value
            yMax = self.sortInits5curves(xvalues, yvalues)[2]
            # mse for logistic5
            yPred5 = self.logistic5(
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
                xvalues,
            )
            err5 = np.sum((yPred5 - yvalues) ** 2) / len(yPred5)
            params = [
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
            ]
            return err5, params

    # depending on length of curve params, calculate
    # the sigmoid curve
    def calculateCurve(self, params, xvalues):
        """
        depending on length of curve params, calculate
        the sigmoid curve
        """
        if len(params) == 6:
            yDataForSat = self.logistic2(
                params[0],
                params[1],
                params[2],
                params[3],
                params[4],
                params[5],
                xvalues,
            )
            return yDataForSat
        if len(params) == 9:
            yDataForSat = self.logistic3(
                params[0],
                params[1],
                params[2],
                params[3],
                params[4],
                params[5],
                params[6],
                params[7],
                params[8],
                xvalues,
            )
            return yDataForSat
        if len(params) == 12:
            yDataForSat = self.logistic4(
                params[0],
                params[1],
                params[2],
                params[3],
                params[4],
                params[5],
                params[6],
                params[7],
                params[8],
                params[9],
                params[10],
                params[11],
                xvalues,
            )
            return yDataForSat
        if len(params) == 15:
            yDataForSat = self.logistic5(
                params[0],
                params[1],
                params[2],
                params[3],
                params[4],
                params[5],
                params[6],
                params[7],
                params[8],
                params[9],
                params[10],
                params[11],
                params[12],
                params[13],
                params[14],
                xvalues,
            )
            return yDataForSat

    # sigmoid curve functions inspired by Sven Lautenbach
    # simple logistic curve
    def logistic1(self, xmid, ymax, slope, x) -> float:
        """
        sigmoid curve functions inspired by Sven Lautenbach.
        simple logistic curve
        """
        # ymax: max(y-value) / asymptote
        # slope: slope, growth rate
        # x: x value
        # xmid: x value of midpoint of sigmoid curve
        return ymax / (1 + np.exp(slope * (xmid - x)))

    # init params for single curve returns x0, k,
    # miny, maxy, xjump1,dy1
    def initparamsingle(self, xdata, ydata) -> list:
        """
        Init params for single curve. Min x and max x are
        calculated a bit different to initparamsingleB()
        """
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
        """
        Init params for single curve
        """
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
        """
        sigmoid curve function inspired by Sven Lautenbach.
        double logistic curve
        """
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
        """
        find initial values for the double curve
        taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
        """
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
        """
        Sort values that initparamsFor2JumpsCurve() returns,
        sort the x values with corresponding  y values
        """
        inits = self.initparamsFor2JumpsCurve(xdata, ydata)
        # ToDo currrently sorted by size, what if curve
        #  decreases and so the max x is not the last x?
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
        """
        sigmoid curve function inspired by Sven Lautenbach.
        logistic curve with 3 jumps.
        ymax, ymax2, ymax3: max(y-value) / asymptote
        slope, slope2, slope3: slope, growth rate
        x: x value
        xmid, xmid2, xmid3: x value of midpoint of sigmoid curve
        """
        return (
            ymax / (1 + np.exp(slope * (xmid - x)))
            + (ymax2 - ymax) / (1 + np.exp(slope2 * (xmid2 - x)))
            + (ymax3 - ymax2) / (1 + np.exp(slope3 * (xmid3 - x)))
        )

    # find initial values for the triple curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor3JumpsCurve(self, xdata, ydata) -> list:
        """
        find initial values for the triple curve
        taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
        """
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
        """
        Function to sort initparams from initparamsFor3JumpsCurve()
        or initparamsFor4JumpsCurve(), so far could not see
        differences in the values returned by these 2 functions
        """
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
        """
        find initial values for the curve with 4 jumps
        taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
        """
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
        """
        find initial values for the curve with 5 jumps
        taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
        """
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
        """
        Sort values that initparamsFor5JumpsCurve() returns,
        sort the x values with corresponding  y values
        """
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

    def getSaturationInLast3Years(self, earlyX, lastX, xdata, ydata) -> float:
        """
        get gradient/slope in last 3 years of the logistic curve.
        pass as ydata the result of sigmoid function
        (sigmoid_curve.getBestFittingCurve(self.preprocessing_results))
        """
        earlyY = np.interp(earlyX, xdata, ydata)
        lastY = np.interp(lastX, xdata, ydata)
        return earlyY / lastY

    def getBestFittingCurve(self, preprocessing_results: Dict) -> list:
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
        # initial values for the single sigmoid curve
        initParamsSingle = self.initparamsingle(df1.li, df1.yValues)
        errorsListSingle = []
        if not math.isnan(initParamsSingle[3]):
            inits5curves = self.sortInits5curves(df1.li, df1.yValues)
            # add up the 2 lists and then check each of the 4 values,
            # if they are not nan
            validity_result = all(  # check if all elements are true
                map(
                    math.isfinite,  # check if number is finite --> excludes nan
                    [
                        *inits5curves[0],  # check all list elemets
                        *inits5curves[1],
                        inits5curves[2],  # check element
                        inits5curves[3],
                    ],
                )
            )
            if validity_result is True:
                # get possible xmids
                xmidvalues = self.sortInits5curves(df1.li, df1.yValues)[0]
                # check for the xmids the mse error
                for xval in xmidvalues:
                    yPredX = self.logistic1(
                        xval, initParamsSingle[3], initParamsSingle[1], df1.li
                    )
                    errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
                    errorsListSingle.append(errX)
                # choose the initial x value with min mse
                minX = min(errorsListSingle)
                prefX = xmidvalues[errorsListSingle.index(minX)]
                # mse for logistic1
                # with k as 10.0 / (maxx - minx) from initparamsingle()
                yPredPref = self.logistic1(
                    prefX, initParamsSingle[3], initParamsSingle[1], df1.li
                )
                err1 = np.sum((yPredPref - df1.yValues) ** 2) / len(yPredPref)
                errorslist.append(err1)
                errorslistFuncs.append("logistic1")
            else:
                prefX = initParamsSingle[4]
                yPredX = self.logistic1(
                    prefX, initParamsSingle[3], initParamsSingle[1], df1.li
                )
                errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
                errorslist.append(errX)
                errorslistFuncs.append("logistic1")

        # initial values for the single sigmoid curve with a different slope
        initParamsSingleB = self.initparamsingleB(df1.li, df1.yValues)
        if not math.isnan(initParamsSingleB[3]):
            errorsListSingle = []
            inits5curves = self.sortInits5curves(df1.li, df1.yValues)
            # add up the 2 lists and then check each of the 4 values,
            # if they are not nan
            validity_result = all(  # check if all elements are true
                map(
                    math.isfinite,  # check if number is finite --> excludes nan
                    [
                        *inits5curves[0],  # check all list elemets
                        *inits5curves[1],
                        inits5curves[2],  # check element
                        inits5curves[3],
                    ],
                )
            )
            if validity_result is True:
                # get possible xmids
                xmidvalues = self.sortInits5curves(df1.li, df1.yValues)[0]
                # incoms = [incom for incom in xmidvalues if str(incom) != 'nan']
                # xmidvalues = incoms
                # check for the xmids the mse error
                for xval in xmidvalues:
                    yPredX = self.logistic1(
                        xval, initParamsSingleB[3], initParamsSingleB[1], df1.li
                    )
                    errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
                    errorsListSingle.append(errX)
                # choose the initial x value with min mse
                minX = min(errorsListSingle)
                prefX = xmidvalues[errorsListSingle.index(minX)]
                # mse for logistic1 with
                # k as 10.0 / (max(xdata) - min(xdata)) from initparamsingleB()
                yPredB = self.logistic1(
                    prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
                )
                err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)
                errorslist.append(err1B)
                errorslistFuncs.append("logistic1B")
            else:
                prefX = initParamsSingleB[4]
                yPredXB = self.logistic1(
                    prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
                )
                errXB = np.sum((yPredXB - df1.yValues) ** 2) / len(yPredXB)
                errorslist.append(errXB)
                errorslistFuncs.append("logistic1B")
        # initial values for the sigmoid function with 2 jumps
        initParamsY = self.sortInits2curves(df1.li, df1.yValues)[1]
        if not math.isnan(initParamsY[0]):
            err2 = self.calculateCurveParams(initParamsY, df1.li, df1.yValues)[0]
            errorslist.append(err2)
            errorslistFuncs.append("logistic2")
        # --- sigmoid function with 3  jumps---
        # get initial y values for the curve with 3
        initParamsY3 = self.sortInits3curves(
            df1.li, df1.yValues, self.initparamsFor3JumpsCurve
        )[1]
        if not math.isnan(initParamsY3[0]):
            err3 = self.calculateCurveParams(initParamsY3, df1.li, df1.yValues)[0]
            errorslist.append(err3)
            errorslistFuncs.append("logistic3")
        # --- sigmoid function with 4 jumps ---
        # get initial y values for the curve with 4 jumps
        initParamsY4 = self.sortInits3curves(
            df1.li, df1.yValues, self.initparamsFor4JumpsCurve
        )[1]
        if not math.isnan(initParamsY4[0]):
            err4 = self.calculateCurveParams(initParamsY4, df1.li, df1.yValues)[0]
            errorslist.append(err4)
            errorslistFuncs.append("logistic4")
        # --- sigmoid function with 5 jumps ---
        initParamsY5 = self.sortInits5curves(df1.li, df1.yValues)[1]
        if not math.isnan(initParamsY5[0]):
            err5 = self.calculateCurveParams(initParamsY5, df1.li, df1.yValues)[0]
            errorslist.append(err5)
            errorslistFuncs.append("logistic5")
        if len(errorslist) > 0:
            # get the smallest mse with its index
            minError = errorslist.index(min(errorslist))
            bestfit = errorslistFuncs[minError]
            # depending on best fitted curve calculate ydata with
            # correct function
            if bestfit == "logistic2":
                params2curves = self.calculateCurveParams(
                    initParamsY, df1.li, df1.yValues
                )[1]
                ydataForSat = self.calculateCurve(params2curves, df1.li)
            elif bestfit == "logistic1":
                ydataForSat = self.logistic1(
                    prefX, initParamsSingle[3], initParamsSingle[1], df1.li
                )
            elif bestfit == "logistic1B":
                ydataForSat = self.logistic1(
                    prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
                )
            elif bestfit == "logistic3":
                params3curves = self.calculateCurveParams(
                    initParamsY3, df1.li, df1.yValues
                )[1]
                ydataForSat = self.calculateCurve(params3curves, df1.li)
            elif bestfit == "logistic4":
                params4curves = self.calculateCurveParams(
                    initParamsY4, df1.li, df1.yValues
                )[1]
                ydataForSat = self.calculateCurve(params4curves, df1.li)
            elif bestfit == "logistic5":
                params5curves = self.calculateCurveParams(
                    initParamsY5, df1.li, df1.yValues
                )[1]
                ydataForSat = self.calculateCurve(params5curves, df1.li)
            return ydataForSat
        else:
            # no curve could be calculated
            return ["empty"]

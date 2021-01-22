import numpy as np


class sigmoidCurve:
    """Sigmoid stuff."""

    # get the y values where one curve ends and the next begins,
    # there where the data show sth like a plateau
    def getYvaluesAtPlateaus(self, x, xdata, ydata) -> list:
        yValsAtPlateaus = []
        for i, xVal in enumerate(x):
            if i <= len(x) - 1:
                if i == len(x) - 1:
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
                        yAtX = np.interp(xVal, xdata, ydata)
                    yValsAtPlateaus.append(yAtX)
                else:
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
                        yAtX = np.interp(xVal, xdata, ydata)
                    yValsAtPlateaus.append(yAtX)
        return yValsAtPlateaus

    # get the y value at the beginning of the curve, but not 0
    def getYatCurveStart(self, x, xdata, ydata) -> float:
        if 10 < x[0] < 15:
            ystart = np.interp(x[0] - 9, xdata, ydata)
        elif 5 < x[0] < 10:
            ystart = np.interp(x[0] - 4, xdata, ydata)
        elif x[0] >= 15:
            ystart = np.interp(x[0] - 15, xdata, ydata)
        else:
            ystart = np.interp(x[0] - 0.5, xdata, ydata)
        return ystart

    # sigmoid curve functions inspired by Sven Lautenbach
    # simple logistic curve
    def logistic1(self, xmid, ymax, slope, x) -> float:
        # ymax: max(y-value)
        # slope: slope, growth rate
        # x: x value
        # xmid: x value of midpoint of sigmoid curve
        return ymax / (1 + np.exp(slope * (xmid - x)))

    # init params for single curve returns x0, k,miny,maxy, xjump1,dy1
    def initparamsingle(self, xdata, ydata) -> list:
        # Find the steepest single step
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 5:
            return [np.nan] * 10
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
        if len(dydata[dydata > 0]) < 5:
            return [np.nan] * 10
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
    def logistic2(self, x, x2, L, L2, k, k2, x0) -> float:
        return L / (1 + np.exp(k * (x - x0))) + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))

    # find initial values for the double curve
    # taken from: https://gitlab.com/cpbl/osm-completeness -> fits.py
    def initparamsFor2JumpsCurve(self, xdata, ydata) -> list:
        # Find the steepest single step
        # Careful... I'm making use of Pandas properties,
        # but xdata could be just a vector, rather than a pd.Series
        dydata = ydata - ydata.shift(1)
        if len(dydata[dydata > 0]) < 5:
            return [np.nan] * 10
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

        # These seems to work on every case except
        # non-changing ydata (with one change only)
        try:
            iBoundaries = flatter[
                boundaries
            ].index  # This is where slope changes (crosses)
            # its mean value
            # Here is the index from which (inclusive) we
            # should start masking away:
            # ie  ind the latest boundary before our jump,
            # and the first following it:
            startMask, endMask = (
                iBoundaries[iBoundaries < xjump2.index.values[0]].max(),
                iBoundaries[iBoundaries > xjump2.index.values[0]].min(),
            )
            dydata.iloc[startMask:endMask] = 0
            # This zeros out the slope on a contiguous region
            # around our first jump.
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

    # don't know why, result of initparamsFor2JumpsCurve() is not sorted
    def sortInits2curves(self, xdata, ydata) -> tuple:
        inits = self.initparamsFor2JumpsCurve(xdata, ydata)
        lx = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
        x = sorted(lx)
        yValsAtPlateaus = self.getYvaluesAtPlateaus(x, xdata, ydata)
        ymax = inits[3]
        ystart = self.getYatCurveStart(x, xdata, ydata)
        return x, yValsAtPlateaus, ymax, ystart

    # logistic curve with 3 jumps
    def logistic3(self, x, x2, x3, L, L2, L3, k, k2, k3, x0):
        return (
            L / (1 + np.exp(k * (x - x0)))
            + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))
            + (L3 - L2) / (1 + np.exp(k3 * (x3 - x0)))
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

    # don't know why, result of
    # initparamsFor3JumpsCurve() is not sorted
    def sortInits3curves(self, xdata, ydata) -> tuple:
        inits = self.initparamsFor3JumpsCurve(xdata, ydata)
        lx = []
        for i, j in enumerate(inits):
            if i > 3 and not i % 2:
                lx.append(j)
        x = sorted(lx)
        yValsAtPlateaus = self.getYvaluesAtPlateaus(x, xdata, ydata)
        ymax = inits[3]
        ystart = self.getYatCurveStart(x, xdata, ydata)
        return x, yValsAtPlateaus, ymax, ystart

    # logistic curve with 4 jumps
    def logistic4(self, x, x2, x3, x4, L, L2, L3, L4, k, k2, k3, k4, x0) -> float:
        return (
            L / (1 + np.exp(k * (x - x0)))
            + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))
            + (L3 - L2) / (1 + np.exp(k3 * (x3 - x0)))
            + (L4 - L3) / (1 + np.exp(k4 * (x4 - x0)))
        )

    # logistic curve with 5 jumps
    def logistic5(
        self, x, x2, x3, x4, x5, L, L2, L3, L4, L5, k, k2, k3, k4, k5, x0
    ) -> float:
        return (
            L / (1 + np.exp(k * (x - x0)))
            + (L2 - L) / (1 + np.exp(k2 * (x2 - x0)))
            + (L3 - L2) / (1 + np.exp(k3 * (x3 - x0)))
            + (L4 - L3) / (1 + np.exp(k4 * (x4 - x0)))
            + (L5 - L4) / (1 + np.exp(k5 * (x5 - x0)))
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
        if len(dydata[dydata > 0]) < 5:
            return [np.nan] * 10
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
        x = sorted(lx)
        yValsAtPlateaus = self.getYvaluesAtPlateaus(x, xdata, ydata)
        ystart = self.getYatCurveStart(x, xdata, ydata)
        ymax = inits[3]
        return x, yValsAtPlateaus, ymax, ystart

    # get gradient/slope in last 3 years of the logistic curve
    # pass as ydata the sigmoid function with init params
    # logistic2(110, 135, 10000, 28900, 0.3, 0.3, df1.li)
    def getSaturationInLast3Years(self, earlyX, lastX, xdata, ydata) -> float:
        earlyY = np.interp(earlyX, xdata, ydata)
        lastY = np.interp(lastX, xdata, ydata)
        return earlyY / lastY

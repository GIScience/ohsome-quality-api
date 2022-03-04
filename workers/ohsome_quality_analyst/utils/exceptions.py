"""Custom exception classes."""


class OhsomeApiError(Exception):
    """Request to ohsome API failed."""

    def __init__(self, message):
        self.name = "OhsomeApiError"
        self.message = message


class SizeRestrictionError(ValueError):
    """Exception raised if size of input GeoJSON Geometry is too big."""

    def __init__(self, geom_size_limit):
        self.name = "SizeRestrictionError"
        self.message = (
            "Input GeoJSON Geometry is too big. "
            + "The area should be less than {0} km².".format(geom_size_limit)
        )


class DatabaseError(Exception):
    pass


class EmptyRecordError(DatabaseError):
    def __init__(self):
        self.name = "EmptyRecordError"
        self.message = "Query returned no record."


class RasterDatasetNotFoundError(FileNotFoundError):
    def __init__(self, raster):
        self.name = "RasterDatasetNotFoundError"
        self.message = "Raster dataset {0} has not been found.".format(raster.name)


class RasterDatasetUndefinedError(ValueError):
    def __init__(self, name):
        self.name = "RasterDatasetUndefinedError"
        self.message = "Raster dataset {0} is not defined".format(name)

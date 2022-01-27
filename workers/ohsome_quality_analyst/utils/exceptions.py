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

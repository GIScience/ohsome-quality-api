"""Custom exception classes."""
from schema import SchemaError


class ValidationError(Exception):
    pass


class GeoJsonError(ValidationError):
    """Invalid GeoJSON Object."""

    def __init__(self, errors):
        self.name = "GeoJsonError"
        self.message = "Invalid GeoJSON Object: {}".format(errors)


class GeoJsonObjectTypeError(ValidationError):
    """Invalid GeoJSON object type."""

    def __init__(self):
        self.name = "GeoJsonObjectTypeError"
        self.message = (
            "Unsupported GeoJSON object Type. GeoJSON object has to be of type "
            + "FeatureCollection or Feature."
        )


class GeoJsonGeometryTypeError(ValidationError):
    """Invalid GeoJSON geometry type."""

    def __init__(self):
        self.name = "GeoJsonGeometryTypeError"
        self.message = (
            "Unsupported GeoJSON geometry Type. GeoJSON geometry has to be of type "
            + "Polygon or MultiPolygon"
        )


class IndicatorTopicError(ValidationError):
    """Invalid indicator topic error."""

    def __init__(self, indicator, topic):
        self.name = "IndicatorTopicError"
        self.message = "Invalid combination of indicator and topic: {} and {}".format(
            indicator,
            topic,
        )


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


class HexCellsNotFoundError(DatabaseError):
    def __init__(self):
        self.name = "HexCellsNotFoundError"
        self.message = (
            "No hex-cells found for the given AOI. "
            + "The AOI is probably outside Africa."
        )


class RasterDatasetNotFoundError(FileNotFoundError):
    def __init__(self, raster):
        self.name = "RasterDatasetNotFoundError"
        self.message = "Raster dataset {0} has not been found.".format(raster.name)


class RasterDatasetUndefinedError(ValueError):
    def __init__(self, raster_name: str):
        self.name = "RasterDatasetUndefinedError"
        self.message = "Raster dataset {0} is not defined".format(raster_name)


class TopicDataSchemaError(Exception):
    def __init__(self, message, schema_error: SchemaError):
        self.name = "TopicDataSchemaError"
        self.message = "{0}\n{1}".format(message, schema_error)

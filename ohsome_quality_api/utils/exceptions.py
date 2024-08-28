"""Custom exception classes."""

from schema import SchemaError


class ValidationError(Exception):
    def __init__(self):
        self.name = ""
        self.message = ""


class GeoJSONError(ValidationError):
    """Invalid GeoJSON object."""

    def __init__(self, errors):
        self.name = "GeoJSONError"
        self.message = "Invalid GeoJSON object: {}".format(errors)


class GeoJSONObjectTypeError(ValidationError):
    """Invalid GeoJSON object type."""

    def __init__(self):
        self.name = "GeoJSONObjectTypeError"
        self.message = (
            "Unsupported GeoJSON object type. GeoJSON object has to be of type "
            + "FeatureCollection or Feature."
        )


class GeoJSONGeometryTypeError(ValidationError):
    """Invalid GeoJSON geometry type."""

    def __init__(self):
        self.name = "GeoJSONGeometryTypeError"
        self.message = (
            "Unsupported GeoJSON geometry type. GeoJSON geometry has to be of type "
            + "Polygon or MultiPolygon"
        )


class InvalidCRSError(ValidationError):
    def __init__(self):
        self.name = "InvalidCRSError"
        self.message = (
            "Invalid CRS. The FeatureCollection must have the EPSG:4326 CRS or none."
        )


class AttributeTopicCombinationError(ValidationError):
    """Invalid attribute topic combination error."""

    def __init__(self, attribute, topic):
        self.name = "AttributeTopicCombinationError"
        self.message = "Invalid combination of attribute and topic: {} and {}".format(
            attribute,
            topic,
        )


class IndicatorTopicCombinationError(ValidationError):
    """Invalid indicator topic combination error."""

    def __init__(self, indicator, topic):
        self.name = "IndicatorTopicCombinationError"
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

    def __init__(self, geom_size_limit, geom_size):
        self.name = "SizeRestrictionError"
        self.message = (
            f"Input GeoJSON Geometry is too big ({geom_size} km²). "
            f"The area should be less than {geom_size_limit} km²."
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


class TopicDataSchemaError(Exception):
    def __init__(self, message, schema_error: SchemaError):
        self.name = "TopicDataSchemaError"
        self.message = "{0}\n{1}".format(message, schema_error)

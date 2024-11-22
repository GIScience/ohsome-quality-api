"""Custom exception classes."""

from schema import SchemaError


class ValidationError(Exception):
    def __init__(self):
        self.name = ""
        self.message = ""


class AttributeTopicCombinationError(ValidationError):
    """Invalid attribute topic combination error."""

    def __init__(self, attribute, topic, valid_attribute_names):
        self.name = "AttributeTopicCombinationError"
        self.message = (
            "Invalid combination of attribute and topic: {} and {}. "
            "Topic '{}' supports these attributes: {}"
        ).format(attribute, topic, topic, valid_attribute_names)


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


class TopicDataSchemaError(Exception):
    def __init__(self, message, schema_error: SchemaError):
        self.name = "TopicDataSchemaError"
        self.message = "{0}\n{1}".format(message, schema_error)

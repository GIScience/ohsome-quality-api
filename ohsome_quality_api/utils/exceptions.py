"""Custom exception classes."""

from fastapi_i18n import _
from schema import SchemaError


class OhsomeApiError(Exception):
    """Request to ohsome API failed."""

    def __init__(self, message):
        self.name = "OhsomeApiError"
        self.message = message


class SizeRestrictionError(ValueError):
    """Exception raised if size of input GeoJSON Geometry is too big."""

    def __init__(self, geom_size_limit, geom_size):
        self.name = "SizeRestrictionError"
        self.message = _(
            "Input GeoJSON Geometry is too big ({geom_size} km²). "
            "The area should be less than {geom_size_limit} km²."
        ).format(geom_size=geom_size, geom_size_limit=geom_size_limit)


class DatabaseError(Exception):
    pass


class EmptyRecordError(DatabaseError):
    def __init__(self):
        self.name = "EmptyRecordError"
        self.message = _("Query returned no record.")


class TopicDataSchemaError(Exception):
    def __init__(self, message, schema_error: SchemaError):
        self.name = "TopicDataSchemaError"
        self.message = "{0}\n{1}".format(message, schema_error)

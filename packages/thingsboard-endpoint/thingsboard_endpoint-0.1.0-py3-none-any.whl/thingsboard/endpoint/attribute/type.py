# -*- coding: utf-8 -*-

from thingsboard.endpoint.exception.invalid_attribute_type_exception import InvalidAttributeTypeException


class AttributeType(object):
    """Identifies the different data types of attributes currently supported by endpoint.
    """
    Invalid = 0  # Invalid data type
    Boolean = 1  # The attribute's value is of type boolean
    Integer = 2  # The attribute's value is of type short, int or long
    Number = 3  # The attribute's value is of type float or double
    String = 4  # The attribute's value is of type String

    def __init__(self, attribute_type):
        super(AttributeType, self).__init__()
        # Check if parameter is valid and yell otherwise
        if attribute_type in (self.Invalid, self.Boolean, self.Integer, self.Number, self.String):
            self._type = attribute_type
        else:
            raise InvalidAttributeTypeException(attribute_type)

    @classmethod
    def from_raw_type(cls, raw_type) -> int:
        """Converts a standard type to its endpoint type representation.
        :raw_type The standard type to convert from.
        :return The corresponding endpoint type.
        """
        if isinstance(raw_type, bool):
            return cls.Boolean
        elif isinstance(raw_type, int):
            return cls.Integer
        elif isinstance(raw_type, float):
            return cls.Number
        elif isinstance(raw_type, str) or isinstance(raw_type, bytes):
            return cls.String
        else:
            return cls.Invalid

    @classmethod
    def from_raw_type_to_string(cls, raw_type) -> str:
        """Converts a standard type to a string.
        :raw_type The standard type to convert from.
        :return The type represented as a string.
        """
        if isinstance(raw_type, bool):
            return 'Boolean'
        elif isinstance(raw_type, int):
            return 'Integer'
        elif isinstance(raw_type, float):
            return 'Number'
        elif isinstance(raw_type, str) or isinstance(raw_type, bytes):
            return 'String'
        else:
            return 'Invalid'

    @property
    def type(self):
        return self._type

    def to_string(self) -> str:
        """Converts AttributeType to string.
        :return The type in string format
        """
        if self._type == self.Boolean:
            return 'Boolean'
        elif self._type == self.Integer:
            return 'Integer'
        elif self._type == self.Number:
            return 'Number'
        elif self._type == self.String:
            return 'String'
        else:
            return 'Invalid'

    def __eq__(self, other):
        """== operator to work with attribute types."""
        if isinstance(other, int):
            return self._type == other
        else:
            raise InvalidAttributeTypeException(other)

    def __ne__(self, other):
        """!= operator to work with attribute types."""
        return not self.__eq__(other)

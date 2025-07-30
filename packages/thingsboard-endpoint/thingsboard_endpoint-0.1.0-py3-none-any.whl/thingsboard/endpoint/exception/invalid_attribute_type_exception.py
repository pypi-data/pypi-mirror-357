# -*- coding: utf-8 -*-

class InvalidAttributeTypeException(Exception):
    def __init__(self, type):
        super(InvalidAttributeTypeException, self).__init__(
            str(type) + ' is not a valid endpoint attribute type!')

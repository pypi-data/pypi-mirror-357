# -*- coding: utf-8 -*-

class InvalidAttributeException(Exception):
    def __init__(self, value):

        if isinstance(value, str):
            message = value
            assert message != ''
            super(InvalidAttributeException, self).__init__(message)
        else:
            type = value
            super(InvalidAttributeException, self).__init__(
                'Data type ' + str(type) + ' not supported!')

# -*- coding: utf-8 -*-

from .json_format import JsonMessageFormat
from .jsonzip_format import JsonZipMessageFormat


class MessageFormatFactory(object):
    """Provides the necessary MessageFormat converter in order to serialize/deserialize a message.

    Currently supported message formats are:
    - '{': json format
    - 'z': zipped json format
    """

    formats = {}  # key: int, values: MessageFormat

    @classmethod
    def message_format(cls, message_format_id):
        """Returns the MessageFormat needed to serialize/deserialize a message.

        :param message_format_id The message format identifying the format of a message.
        """
        if message_format_id in cls.formats:
            return cls.formats[message_format_id]
        else:
            new_format = None
            if message_format_id == '{':
                new_format = JsonMessageFormat()
                cls.formats[message_format_id] = new_format
            if message_format_id == 'z':
                new_format = JsonZipMessageFormat()
                cls.formats[message_format_id] = new_format

            return new_format

# -*- coding: utf-8 -*-

from .json_format import JsonMessageFormat

class ThingsboardMessageFormat(JsonMessageFormat):
    """Serialized messages data into a dictionary containing the needed telemetry information.

    """

    def __init__(self):
        super(ThingsboardMessageFormat, self).__init__()

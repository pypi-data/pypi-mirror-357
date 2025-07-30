# -*- coding: utf-8 -*-

class ModificationException(Exception):
    def __init__(self, message):
        super(ModificationException, self).__init__(message)

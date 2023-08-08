# -*- coding: utf-8 -*-

class WebServiceError(Exception):
    def __init__(self, arg):
        self.args = arg
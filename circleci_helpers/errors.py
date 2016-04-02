# -*- coding: utf-8 -*-


class Error(Exception):
    pass


class YAMLFileLoadError(Error):
    pass


class YAMLFileValidationError(Error):
    pass

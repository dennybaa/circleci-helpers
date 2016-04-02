# -*- coding: utf-8 -*-

import os.path
import sys
import pprint
import pykwalify.core

import yaml

from circleci_helpers.errors import YAMLFileLoadError, YAMLFileValidationError
from circleci_helpers.logger import Log
from circleci_helpers.matrix.cli import LOG_LEVEL


class Config(object):
    SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schema.yml')
    DEFAULT_CONFIG = 'circle-matrix.yml'

    log = Log.console_logger(LOG_LEVEL)

    def __init__(self, config_path=None, config_data=None):
        '''
        Args:
            config_path (str): path to the matrix config file.
            config_data (str): yaml matrix config data passed as string.
                If provided, it's preferred to config_path.
        '''
        self.config_path = config_path
        self._config_data = config_data
        self._config = None

    @property
    def config_data(self):
        '''Choses matrix YAML config source and reads it. If it's a file == '-' or
           default config doesn't exist. Data is read from STDIN.
        '''
        if self._config_data is not None:
            return self._config_data

        if self.config_path is None and not os.path.isfile(self.DEFAULT_CONFIG):
            self.config_path = '-'

        if self.config_path == '-':
            self._config_data = sys.stdin.read()
        else:
            with open(self.config_path, 'r') as inp:
                self._config_data = inp.read()

        return self._config_data

    @property
    def config(self):
        if self._config is not None:
            return self._config

        self._config = self.load_config()
        self.log.debug("***** DATA REPRESENTED *****\n%s", pprint.pformat(self._config, indent=2))
        self.validate_schema()
        return self._config

    def load_config(self):
        '''Parses matrix YAML config'''
        try:
            data = yaml.load(self.config_data)
            self.log.debug("***** YAML LOADED *****\n%s", self.config_data)
        except IOError as e:
            raise YAMLFileLoadError(e)
        except yaml.scanner.ScannerError as e:
            if self.config_path is not None:
                filename = 'STDIN' if self.config_path == '-' else self.config_path
            self.log.error("Couldn't parse YAML data from file: %s", filename)
            raise YAMLFileLoadError(e)

        return data

    def validate_schema(self, source_data=None, schema_file=None):
        '''Validates matrix dict to comply the schema'''
        source_data = source_data or self._config
        if source_data is None:
            raise RuntimeError('load the config file first or pass source_data argument')

        schema = pykwalify.core.Core(source_data=source_data,
                                     schema_files=[schema_file or Config.SCHEMA_FILE])
        try:
            schema.validate()
        except pykwalify.errors.SchemaError as e:
            self.log.error(e)
            raise YAMLFileValidationError(e)

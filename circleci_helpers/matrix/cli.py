# -*- coding: utf-8 -*-

import logging

from docopt import docopt

__docopt__ = """
Usage: circle-matrix [-c circle-matrix.yml] [-v ...]

Options:
  -c circle-matrix.yml --config-path circle-matrix.yml
                            matrix yaml file path. If not given or set to
                            "-" STDIN is used.
  -v --verbose              verbosity sets the log debug.
"""

CLI_ARGS = docopt(__docopt__)
LOG_LEVEL = logging.DEBUG if CLI_ARGS['--verbose'] > 0 else logging.INFO

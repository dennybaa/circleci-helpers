# -*- coding: utf-8 -*-

import sys

from termcolor import colored
from circleci_helpers.logger import Log
from circleci_helpers.matrix.cli import LOG_LEVEL, CLI_ARGS
from circleci_helpers.matrix.config import Config
from circleci_helpers.matrix.runner import BatchRunner
from circleci_helpers.shellhelpers import readenv


class BatchTerminated(Exception):
    def __init__(self, exitcode):
        super(BatchTerminated, self).__init__()
        self.exitcode = exitcode


class Matrix(object):
    log = Log.console_logger(LOG_LEVEL)
    SEQUENCE = ('before_script', 'script', 'after_success',
                'after_failure', 'after_script')

    def __init__(self, config_path=None, config_data=None):
        # Load matrix config
        config_path = config_path or CLI_ARGS['--config-path']
        self.config = Config(config_path=config_path,
                             config_data=config_data).config
        self.script_exitcode = 0
        self.batchenv = None
        self.step = None
        self.failed = False

    def get_matrixenv(self):
        '''Get matrix environment'''
        env = readenv(self.config['env'][self.step])
        envdebug = ['{}={}'.format(k, v) for k, v in env.items()]
        self.log.debug('***** STEP ENVIRONMENT *****\n%s', ' '.join(envdebug))

        return env

    def failure_allowed(self):
        hashlist = self.config.get('matrix', {}).get('allow_failures', [])

        # by default failures are not allowed
        if len(hashlist) == 0:
            return False

        # If batch environment variables value differs from the allowed
        # then failure is not allowed.
        for ahash in hashlist:
            failenv = readenv(ahash['env'])
            allset = True
            for k, v in failenv.items():
                if self.batchenv.get(k) != v:
                    allset = False
                    break

            if allset:
                return True

        return False

    def execute(self, step):
        '''Matrix step execution method'''
        # Check step value
        step = int(step)
        if step < 0 or step >= len(self.config['env']):
            self.log.error("matrix step `%s' can not be executed, "
                           "index out of range!", self.step)
            sys.exit(1)

        exitcode = self._execute(step)
        if not self.failure_allowed and exitcode > 0:
            sys.exit(exitcode)

    def _execute(self, step):
        # Brining matrix to initial state and set step number
        self.batchenv = None
        self.script_exitcode = 0
        self.step = step

        for seq in self.SEQUENCE:
            try:
                getattr(self, seq)()
            except BatchTerminated as e:
                self.failed = True
                return e.exitcode

        # Don't reset self.failed (it's already)
        self.failed = True if self.failed else self.script_exitcode > 0
        return self.script_exitcode

    def before_script(self):
        self.log.debug('Starting before_script execution')
        self.execute_batch('before_script')

    def script(self):
        self.script_exitcode = self.execute_batch('script',
                                                  batch_terminate=False)

    def after_success(self):
        if not self.script_exitcode:
            self.execute_batch('after_success')

    def after_failure(self):
        if self.script_exitcode:
            self.execute_batch('after_failure')

    def after_script(self):
        self.execute_batch('after_script')

    def execute_batch(self, batch_name, batch_terminate=True):
        '''Execute commands of a specific batch group'''
        commands = self.config.get(batch_name, None)
        if not commands:
            return

        # Execute batch runner with matrixenv and batchenv.
        # Matrix env stays immutable through all batch steps, while
        # batch env will be preserved even between batch runners.
        stepenv = self.get_matrixenv()
        runner = BatchRunner(stepenv=stepenv, env=self.batchenv)
        runner.execute(commands)
        self.batchenv = runner.batchenv

        # Terminate batch processing ignoring the rest batch groups
        if batch_terminate and runner.exitcode > 0:
            self.log.error(colored('%s execution failed', 'red'), batch_name)
            raise BatchTerminated(exitcode=runner.exitcode)

        return runner.exitcode

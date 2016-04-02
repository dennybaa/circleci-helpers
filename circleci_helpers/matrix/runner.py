# -*- coding: utf-8 -*-

import os
import tempfile

from termcolor import colored
from circleci_helpers.logger import Log
from circleci_helpers.matrix.cli import LOG_LEVEL
from circleci_helpers.shellhelpers import shell_out, readenv


def flatten(*seq):
    '''Flattens a list.
    Returns a generator.
    '''
    return (item for inseq in seq
            for item in (
                flatten(*inseq) if isinstance(inseq, (tuple, list)) else (inseq, )
            ))


class BatchRunner(object):
    log = Log.console_logger(LOG_LEVEL)

    def __init__(self, stepenv=None, env=None):
        self.stepenv = stepenv or {}
        self.env = env
        self.batchenv_tempfile = tempfile.NamedTemporaryFile(mode='w+')
        self.failed_command = None
        self.exitcode = 0

    @property
    def batchenv(self):
        '''Runner environment is preserved between batch steps.
           Retreives env from a temporary file.
        '''
        self.batchenv_tempfile.seek(0)
        env = readenv(self.batchenv_tempfile)
        # Setting initial environment, it's merged into os.environ
        if not env:
            env = os.environ.copy()
            env.update(self.env or {})

        # stepenv environment is restored for each batch step,
        # i.e. can not be changed from step to step.
        env.update(self.stepenv)
        return env

    def execute(self, *commands):
        for cmd in flatten(*commands):
            self.log.info(colored('$ ', 'green') + str(cmd))
            wrapped_cmd = self.spyenv_command(cmd)
            result = shell_out(wrapped_cmd, env=self.batchenv)

            # Fail early don't execute
            if result.failed:
                code = result.returncode
                self.log.info(colored('command failed (exitcode: {})'.format(code), 'red'))
                self.log.debug('***** COMMAND FAILED *****\n{} (PID: {}, exitcode: {})'
                               ''.format(cmd, result.pid, code))
                self.failed_command = cmd
                self.exitcode = code
                break

    def spyenv_command(self, cmd):
        '''Wrap shell command providing env dumping after execution'''
        spycmd = '''{cmd}
        _spyenv_retcode=$?
        env > {envtemp}
        exit $_spyenv_retcode
        '''
        return spycmd.format(cmd=cmd, envtemp=self.batchenv_tempfile.name)

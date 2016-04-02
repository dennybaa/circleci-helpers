# -*- coding: utf-8 -*-

import pytest

from circleci_helpers.matrix.runner import BatchRunner


def test_batch_execution(capsys):
    '''Several echo executions'''
    cmd = ('echo -n foo', 'echo -n bar')
    runner = BatchRunner()
    runner.execute(cmd)
    out, _ = capsys.readouterr()

    assert not runner.exitcode
    assert out == 'foobar'


def test_batch_early_fuilure(capsys):
    '''Batch should be stopped as it executes a script which fails'''
    runner = BatchRunner()
    runner.execute('echo -n foo', 'false', 'echo -n bar')
    out, _ = capsys.readouterr()

    assert runner.exitcode > 0
    assert runner.failed_command == 'false'
    assert out == 'foo'


def test_batch_env_persisted(capsys):
    '''Test if environment preserved between batch steps'''
    runner = BatchRunner(stepenv={'FOO': 'foo'})
    runner.execute('export BAR=bar', 'echo -n $FOO', 'echo -n $BAR')
    out, _ = capsys.readouterr()

    assert out == 'foobar'


def test_batch_stepenv_not_overwritten(capsys):
    '''Check if stepenv is not overwritten between batch steps'''
    runner = BatchRunner(stepenv={'FOO': 'foo'})
    runner.execute('export BAR=bar', 'export FOO=bar', 'echo -n $FOO', 'echo -n $BAR')
    out, _ = capsys.readouterr()

    assert out == 'foobar'


def test_batch_env_canbe_overwriten(capsys):
    '''Check if inital env can be overwritten'''
    runner = BatchRunner(env={'FOO': 'foo'})
    runner.execute('echo -n $FOO', 'FOO=bar', 'echo -n $FOO')

    out, _ = capsys.readouterr()

    assert out == 'foobar'

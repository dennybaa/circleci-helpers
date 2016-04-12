# -*- coding: utf-8 -*-

import os
import pytest
from circleci_helpers.matrix.matrix import Matrix, BatchTerminated

DATADIR = 'tests/matrix/configs/'


def test_matrix_batch_early_shutdown():
    '''Test matrix shutdown on early batch stages without
       proceeding to the later ones.
    '''
    m = Matrix(config_path=DATADIR + 'batch_early_shutdown.yml')
    exitcode = m._execute(step=0)
    assert exitcode == 2


def test_matrix_batch_environment(capsys):
    '''Check if matrix env is not overwritten between steps,
       but the batch environment is preserved between batches
    '''
    m = Matrix(config_path=DATADIR + 'batch_environment.yml')
    m.execute(step=0)
    out, _ = capsys.readouterr()

    assert out == 'foofoobar'


def _check_batch(capsys, config_path, success_or_failure, exitcode):
    m = Matrix(config_path=config_path)
    for i in range(0, len(m.config['env'])):
        _exitcode = m._execute(step=i)
        out, _ = capsys.readouterr()
        script, failure, after = out.split("\n")[0:3]

        assert script == 'Hello world{}'.format(i)
        assert failure == success_or_failure
        assert after == 'after_script'
        assert _exitcode == exitcode


def test_matrix_check_failure(capsys):
    _check_batch(capsys, DATADIR + 'batch_check_success.yml', 'success', 0)
    _check_batch(capsys, DATADIR + 'batch_check_failure.yml', 'failure', 1)


def test_matrix_allow_failures(capsys):
    m = Matrix(config_path=DATADIR + 'batch_allow_failures.yml')
    m.execute(step=0)
    m.execute(step=1)

    out, _ = capsys.readouterr()
    assert m.failed
    assert out == 'foo'

# -*- coding: utf-8 -*-

import pytest
from circleci_helpers.matrix.matrix import Matrix, BatchTerminated

DATADIR = 'tests/matrix/configs/'


def test_matrix_batch_early_shutdown():
    '''Test matrix shutdown on early batch stages without
       proceeding to the later ones.
    '''
    m = Matrix(config_path=DATADIR + 'batch_early_shutdown.yml')
    m.step = 0
    exitcode = m._execute()
    assert exitcode == 2


def test_matrix_batch_environment(capsys):
    '''Check if matrix env is not overwritten between steps,
       but the batch environment is preserved between batches
    '''
    m = Matrix(config_path=DATADIR + 'batch_environment.yml')
    m.execute(step=0)
    out, _ = capsys.readouterr()

    assert out == 'foofoobar'

# -*- coding: utf-8 -*-

import pytest
from circleci_helpers.shellhelpers import shell_out, readenv


def test_shell_out_stderr_capture(capsys):
    result = shell_out(">&2 echo -n error; false;")
    _, err = capsys.readouterr()

    assert err == 'error'
    assert result.failed


def test_shell_out_env_passthrough(capsys):
    result = shell_out('echo -n $FOO', env={'FOO': 'bar'})
    out, _ = capsys.readouterr()

    assert out == 'bar'
    assert result.success


def test_shellout_stdin_processing(tmpdir, capsys):
    # test wrong stdin is given
    with pytest.raises(TypeError):
        shell_out('cat', stdin=12)

    # test stdin given as string
    shell_out('bash -s', stdin='echo -n foo')
    out, _ = capsys.readouterr()
    assert out == 'foo'

    # test stdin from a file object
    f = tmpdir.join('input')
    f.write('foo')
    with open(f.strpath, 'r') as stream:
        shell_out('cat', stdin=stream)
        out, _ = capsys.readouterr()
        assert out == 'foo'


def test_readenv(tmpdir):
    # Test reading environment from a string
    env = readenv('FOO=foo foo BAR="bar bar" FOOBAR=foo = bar')
    assert env['FOO'] == 'foo foo'
    assert env['BAR'] == '"bar bar"'
    assert env['FOOBAR'] == 'foo = bar'

    # Test reading environment from an env file
    f = tmpdir.join('input')
    f.write('#HELLO=world')
    f.write('FOO=foo foo')
    with open(f.strpath, 'r') as stream:
        env = readenv(stream)
        assert env['FOO'] == 'foo foo'
        assert env.get('HELLO') is None

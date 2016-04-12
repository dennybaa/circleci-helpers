# -*- coding: utf-8 -*-

import pytest

from circleci_helpers.errors import YAMLFileLoadError, YAMLFileValidationError
from circleci_helpers.matrix.config import Config


def test_load_config_from_file(tmpdir):
    '''Test yaml config loading from a file'''
    f = tmpdir.join('wrong syntax')
    f.write('foo: - bar')
    c = Config(config_path=f.strpath)

    with pytest.raises(YAMLFileLoadError):
        c.load_config()
        assert True


def test_load_config_returns_dict():
    '''Test if yaml file loaded and parsed'''
    yaml_data = "env:\n  - VERSION=foo\n  - VERSION=bar\n"
    c = Config(config_data=yaml_data)
    data = c.load_config()

    assert data['env'][1] == 'VERSION=bar'


def test_validate_schema_noenv():
    '''Check validation failure, since no env provided'''
    yaml_data = "script:\n  - /bin/true\n"
    c = Config(config_data=yaml_data)
    with pytest.raises(YAMLFileValidationError):
        _ = c.config


def test_validate_schema_unknown_key():
    '''Check if mapping has an unknown key'''
    yaml_data = "env:\n  - VERSION=foo\n  - VERSION=bar\nscript:\n  - /bin/true\n" \
                "foo: bar"
    c = Config(config_data=yaml_data)
    with pytest.raises(YAMLFileValidationError):
        _ = c.config


def test_validate_schema_required():
    '''Check mapping if the required keys are provided.
    Required keys: env, script.
    '''
    yaml_data = "env:\n  - VERSION=foo\n  - VERSION=bar\n"
    c = Config(config_data=yaml_data)
    # Fails since script key is not provided
    with pytest.raises(YAMLFileValidationError):
        _ = c.config


def test_validate_schema_env_list():
    '''Test env variablie list pattern validation'''
    yaml_data = "env:\n  - VERSION=foo VERSION=bar\nscript:\n  - /bin/true\n"
    c = Config(config_data=yaml_data)
    assert True

    yaml_data = "env:\n  - FOO+foo\nscript:\n  - /bin/true\n"
    c = Config(config_data=yaml_data)
    with pytest.raises(YAMLFileValidationError):
        _ = c.config


def test_default_config_pickup(tmpdir):
    '''Test that defult config is loaded if it presents'''
    yaml_data = "env:\n  - VERSION=foo\n  - VERSION=bar\n"
    tmpdir.join('circle-matrix.yml').ensure().write(yaml_data)

    with tmpdir.as_cwd():
        c = Config()
        data = c.load_config()

    assert data['env'][1] == 'VERSION=bar'

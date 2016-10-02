'''
Created on 2 Oct 2016

@author: fressi
'''

import os
import tempfile

import yaml
import pytest
import six


@pytest.fixture
def create_temp_yaml():
    """It returns a factory function for creating temporary yaml files.

    """

    temp_files = []

    def _create_temp_yaml(obj):
        """It creates a temporary yaml file by dumping given object.

        """

        file_id, path = tempfile.mkstemp()
        os.write(file_id, six.b(yaml.dump(obj)))
        os.close(file_id)
        temp_files.append(os.path.abspath(path))
        return path

    yield _create_temp_yaml

    for path in temp_files:
        os.remove(path)

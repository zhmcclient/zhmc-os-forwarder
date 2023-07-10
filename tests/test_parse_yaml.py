#!/usr/bin/env python3

# Copyright 2023 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for the parse_yaml_file() function.
"""

import sys
import os
import stat
import time
import hashlib

import pytest

from zhmc_os_forwarder.utils import parse_yaml_file, ImproperExit


def test_parse_yaml_file_simple():
    """
    Tests if a simple forwarder config file is correctly parsed.
    """
    # Get a SHA256 of Unixtime to create a filename that does not exist
    filename = str(hashlib.sha256(str(time.time()).encode("utf-8")).
                   hexdigest())
    with open(filename, "w+", encoding='utf-8') as testfile:
        testfile.write("""
hmc:
  host: 10.11.12.13
  userid: "myuser"
  password: "mypassword"
  verify_cert: false

forwarding:
  - syslogs:
     - server: 10.11.12.14
    cpcs:
      - cpc: MYCPC
        partitions:
          - partition: ".*"
""")

    expected_result = {
        "hmc": {
            "host": "10.11.12.13",
            "userid": "myuser",
            "password": "mypassword",
            "verify_cert": False,
        },
        "forwarding": [
            {
                "syslogs": [
                    {
                        "server": "10.11.12.14",
                    },
                ],
                "cpcs": [
                    {
                        "cpc": "MYCPC",
                        "partitions": [
                            {
                                "partition": ".*",
                            },
                        ],
                    },
                ],
            },
        ],
    }
    result = parse_yaml_file(filename, 'test file')
    assert result == expected_result

    os.remove(filename)


def test_parse_yaml_file_permission():
    """
    Tests if permission denied is correctly handled.
    """

    if sys.platform == 'win32':
        pytest.skip("Test not supported on Windows")

    filename = str(hashlib.sha256(str(time.time()).encode("utf-8")).
                   hexdigest())
    with open(filename, "w+", encoding='utf-8'):
        pass
    # Make it unreadable (mode 000)
    os.chmod(filename, not stat.S_IRWXU)
    with pytest.raises(ImproperExit):
        parse_yaml_file(filename, 'test file')
    os.remove(filename)


def test_parse_yaml_file_notfound():
    """
    Tests if file not found is correctly handled.
    """
    filename = str(hashlib.sha256(str(time.time()).encode("utf-8")).
                   hexdigest())
    with pytest.raises(ImproperExit):
        parse_yaml_file(filename, 'test file')

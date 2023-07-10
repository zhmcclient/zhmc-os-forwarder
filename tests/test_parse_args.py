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
Unit tests for the parse_args() function.
"""

from zhmc_os_forwarder.zhmc_os_forwarder import parse_args
from zhmc_os_forwarder.utils import DEFAULT_CONFIG_FILE, \
    DEFAULT_SYSLOG_FACILITY


def test_parse_args_full():
    """
    Test with full set of options.
    """
    cmdline = [
        "-c", "foo.yml",
        "-v", "-v",
        "--log", "syslog",
        "--log-comp", "all=debug",
        "--syslog-facility", "local0",
    ]
    args = parse_args(cmdline)
    assert args.c == "foo.yml"
    assert args.log_dest == "syslog"
    assert "all=debug" in args.log_complevels
    assert args.syslog_facility == "local0"


def test_parse_args_min():
    """
    Test with minimal set of options.
    """
    args = parse_args([])
    assert args.c == DEFAULT_CONFIG_FILE
    assert args.log_dest is None
    assert args.log_complevels is None  # default set later
    assert args.syslog_facility == DEFAULT_SYSLOG_FACILITY

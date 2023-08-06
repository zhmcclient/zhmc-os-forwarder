#!/usr/bin/env python

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
IBM Z HMC OS Message Forwarder
"""

import argparse
import sys
import time
import logging
import logging.handlers

import urllib3
import zhmcclient

from ._version import __version__
from .forwarder_server import ForwarderServer
from . import utils  # for global variable VERBOSE_LEVEL
from .utils import DEFAULT_CONFIG_FILE, VALID_LOG_DESTINATIONS, \
    VALID_LOG_LEVELS, VALID_LOG_COMPONENTS, DEFAULT_LOG_LEVEL, \
    DEFAULT_LOG_COMP, DEFAULT_SYSLOG_FACILITY, VALID_SYSLOG_FACILITIES, \
    PRINT_ALWAYS, PRINT_V, RETRY_TIMEOUT_CONFIG, \
    ProperExit, ImproperExit, EarlyExit, \
    parse_yaml_file, logprint, setup_logging


def parse_args(args):
    """
    Parses the CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="IBM Z HMC OS Message Forwarder")
    parser.add_argument("-c", metavar="CONFIG_FILE",
                        default=DEFAULT_CONFIG_FILE,
                        help="path name of config file. "
                        "Use --help-config for details. "
                        "Default: {}".format(DEFAULT_CONFIG_FILE))
    parser.add_argument("--log", dest='log_dest', metavar="DEST", default=None,
                        help="enable logging and set a log destination "
                        "({dests}). Default: no logging".
                        format(dests=', '.join(VALID_LOG_DESTINATIONS)))
    parser.add_argument("--log-comp", dest='log_complevels', action='append',
                        metavar="COMP[=LEVEL]", default=None,
                        help="set a logging level ({levels}, default: "
                        "{def_level}) for a component ({comps}). May be "
                        "specified multiple times; options add to the default "
                        "of: {def_comp}".
                        format(levels=', '.join(VALID_LOG_LEVELS),
                               comps=', '.join(VALID_LOG_COMPONENTS),
                               def_level=DEFAULT_LOG_LEVEL,
                               def_comp=DEFAULT_LOG_COMP))
    parser.add_argument("--syslog-facility", metavar="TEXT",
                        default=DEFAULT_SYSLOG_FACILITY,
                        help="syslog facility ({slfs}) when logging to the "
                        "system log. Default: {def_slf}".
                        format(slfs=', '.join(VALID_SYSLOG_FACILITIES),
                               def_slf=DEFAULT_SYSLOG_FACILITY))
    parser.add_argument("--verbose", "-v", action='count', default=0,
                        help="increase the verbosity level (max: 2)")
    parser.add_argument("--version", action='store_true',
                        help="show versions of forwarder and zhmcclient "
                        "library and exit")
    parser.add_argument("--help-config", action='store_true',
                        help="show help for forwarder config file and exit")
    return parser.parse_args(args)


def print_version():
    """
    Print the version of this program and the zhmcclient library.
    """
    # pylint: disable=no-member
    print("zhmc_os_forwarder version: {}\n"
          "zhmcclient version: {}".
          format(__version__, zhmcclient.__version__))


def help_config():
    """
    Print help for the forwarder config file.
    """
    print("""
Help for forwarder config file

The forwarder config file is a YAML file that defines which HMC to talk to,
and the forwarding, i.e. which partition is forwarded to which syslog server.

The following example shows a complete forwarder config file. For more details,
see the documentation at https://zhmc-os-forwarder.readthedocs.io/.

---
hmc:
  hmc: 10.11.12.13
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


def main():
    """
    Main function for the script.
    """

    args = parse_args(sys.argv[1:])

    if args.version:
        print_version()
        sys.exit(0)

    if args.help_config:
        help_config()
        sys.exit(0)

    utils.VERBOSE_LEVEL = args.verbose

    urllib3.disable_warnings()

    forwarder_server = None

    try:
        setup_logging(args.log_dest, args.log_complevels, args.syslog_facility)

        logprint(logging.WARNING, None,
                 "---------------- "
                 "zhmc_os_forwarder started "
                 "----------------")

        logprint(logging.INFO, PRINT_ALWAYS,
                 "zhmc_os_forwarder version: {}".format(__version__))

        # pylint: disable=no-member
        logprint(logging.INFO, PRINT_ALWAYS,
                 "zhmcclient version: {}".format(zhmcclient.__version__))

        logprint(logging.INFO, PRINT_ALWAYS,
                 "Verbosity level: {}".format(utils.VERBOSE_LEVEL))

        config_filename = args.c
        logprint(logging.INFO, PRINT_V,
                 "Parsing forwarder config file: {}".format(config_filename))
        config_data = parse_yaml_file(
            config_filename, 'forwarder config file', 'config_schema.yaml')

        logprint(logging.INFO, PRINT_V,
                 "Timeout/retry configuration: "
                 "connect: {r.connect_timeout} sec / {r.connect_retries} "
                 "retries, read: {r.read_timeout} sec / {r.read_retries} "
                 "retries.".format(r=RETRY_TIMEOUT_CONFIG))

        forwarder_server = ForwarderServer(config_data, config_filename)
        try:
            forwarder_server.startup()
        except zhmcclient.Error as exc:
            new_exc = ImproperExit(
                "{}: {}".format(exc.__class__.__name__, exc))
            new_exc.__cause__ = None  # pylint: disable=invalid-name
            raise new_exc

        logprint(logging.INFO, PRINT_ALWAYS,
                 "Forwarder is up and running (Press Ctrl-C to shut down)")

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                raise ProperExit

    except KeyboardInterrupt:
        logprint(logging.WARNING, PRINT_ALWAYS,
                 "Forwarder interrupted before server start")
        exit_rc(1)
    except EarlyExit as exc:
        logprint(logging.ERROR, PRINT_ALWAYS,
                 "Error: {}".format(exc))
        exit_rc(1)
    except ImproperExit as exc:
        logprint(logging.ERROR, PRINT_ALWAYS,
                 "Error: {}".format(exc))
        if forwarder_server:
            forwarder_server.shutdown()
        exit_rc(1)
    except ProperExit:
        logprint(logging.WARNING, PRINT_ALWAYS,
                 "Forwarder shutdown requested")
        if forwarder_server:
            forwarder_server.shutdown()
        exit_rc(0)


def exit_rc(rc):
    """Exit the script"""
    logprint(logging.WARNING, None,
             "---------------- "
             "zhmc_os_forwarder terminated "
             "----------------")
    sys.exit(rc)


if __name__ == "__main__":
    main()

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
Utility functions
"""

import sys
import os
import types
import platform
import time
import logging
from contextlib import contextmanager

import yaml
import jsonschema
import zhmcclient

#
# GLobal variables that will be set after command line parsing and will
# then be used throughout the project.
#

# Verbosity level from the command line
VERBOSE_LEVEL = 0

# Indicates that logging was enabled on the command line
LOGGING_ENABLED = False


#
# Logging
#

LOGGER_NAME = 'zhmcosforwarder'

# Logger names by log component
LOGGER_NAMES = {
    'forwarder': LOGGER_NAME,
    'hmc': zhmcclient.HMC_LOGGER_NAME,
    'jms': zhmcclient.JMS_LOGGER_NAME,
}
VALID_LOG_COMPONENTS = list(LOGGER_NAMES.keys()) + ['all']

# Log levels by their CLI names
LOG_LEVELS = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'off': logging.NOTSET,
}
VALID_LOG_LEVELS = list(LOG_LEVELS.keys())

# Defaults for --log-comp option.
DEFAULT_LOG_LEVEL = 'warning'
DEFAULT_LOG_COMP = 'all=warning'

# Values for printing messages dependent on verbosity level in command line
PRINT_ALWAYS = 0
PRINT_V = 1
PRINT_VV = 2

VALID_LOG_DESTINATIONS = ['stderr', 'syslog', 'FILE']

# Syslog facilities
VALID_SYSLOG_FACILITIES = [
    'user', 'local0', 'local1', 'local2', 'local3', 'local4', 'local5',
    'local6', 'local7'
]
DEFAULT_SYSLOG_FACILITY = 'user'

# Values to use for the 'address' parameter when creating a SysLogHandler.
# Key: Operating system type, as returned by platform.system(). For CygWin,
# the returned value is 'CYGWIN_NT-6.1', which is special-cased to 'CYGWIN_NT'.
# Value: Value for the 'address' parameter.
SYSLOG_ADDRESS = {
    'Linux': '/dev/log',
    'Darwin': '/var/run/syslog',  # macOS / OS-X
    'Windows': ('localhost', 514),
    'CYGWIN_NT': '/dev/log',  # Requires syslog-ng pkg
    'other': ('localhost', 514),  # used if no key matches
}


#
# Defaults for other command line options
#

DEFAULT_CONFIG_FILE = '/etc/zhmc-os-forwarder/config.yaml'


#
# Retry
#

# Sleep time in seconds when retrying HMC connections
RETRY_SLEEP_TIME = 10

# Retry / timeout configuration for zhmcclient (used at the socket level)
RETRY_TIMEOUT_CONFIG = zhmcclient.RetryTimeoutConfig(
    connect_timeout=10,
    connect_retries=2,
    read_timeout=300,
    read_retries=2,
    max_redirects=zhmcclient.DEFAULT_MAX_REDIRECTS,
    operation_timeout=zhmcclient.DEFAULT_OPERATION_TIMEOUT,
    status_timeout=zhmcclient.DEFAULT_STATUS_TIMEOUT,
    name_uri_cache_timetolive=zhmcclient.DEFAULT_NAME_URI_CACHE_TIMETOLIVE,
)


#
# Exceptions
#

class ConfigFileError(Exception):
    """
    An error was found in the config file.
    """
    pass


class ConnectionError(Exception):
    # pylint: disable=redefined-builtin
    """
    Connection error with the HMC.
    """
    pass


class AuthError(Exception):
    """
    Authentication error with the HMC.
    """
    pass


class OtherError(Exception):
    """
    Other error with the HMC.
    """
    pass


class ProperExit(Exception):
    """
    Terminating while the server was running.
    """
    pass


class ImproperExit(Exception):
    """
    Terminating because something went wrong.
    """
    pass


class EarlyExit(Exception):
    """
    Terminating before the server was started.
    """
    pass


@contextmanager
def zhmc_exceptions(session, config_filename):
    # pylint: disable=invalid-name
    """
    Context manager that handles zhmcclient exceptions by raising the
    appropriate forwarder exceptions.

    Example::

        with zhmc_exceptions(session, config_filename):
            client = zhmcclient.Client(session)
            version_info = client.version_info()
    """
    try:
        yield
    except zhmcclient.ConnectionError as exc:
        new_exc = ConnectionError(
            "Connection error using IP address {} defined in forwarder config "
            "file {}: {}".format(session.host, config_filename, exc))
        new_exc.__cause__ = None
        raise new_exc  # ConnectionError
    except zhmcclient.ClientAuthError as exc:
        new_exc = AuthError(
            "Client authentication error for the HMC at {h} using "
            "userid '{u}' defined in forwarder config file {f}: {m}".
            format(h=session.host, u=session.userid, f=config_filename,
                   m=exc))
        new_exc.__cause__ = None
        raise new_exc  # AuthError
    except zhmcclient.ServerAuthError as exc:
        http_exc = exc.details  # zhmcclient.HTTPError
        new_exc = AuthError(
            "Authentication error returned from the HMC at {h} using "
            "userid '{u}' defined in forwarder config file {f}: {m} "
            "(HMC operation {hm} {hu}, HTTP status {hs}.{hr})".
            format(h=session.host, u=session.userid, f=config_filename,
                   m=exc, hm=http_exc.request_method, hu=http_exc.request_uri,
                   hs=http_exc.http_status, hr=http_exc.reason))
        new_exc.__cause__ = None
        raise new_exc  # AuthError
    except (IOError, OSError) as exc:
        new_exc = OtherError(str(exc))
        new_exc.__cause__ = None
        raise new_exc  # OtherError
    except zhmcclient.Error as exc:
        new_exc = OtherError(
            "Error returned from HMC at {}: {}".format(session.host, exc))
        new_exc.__cause__ = None
        raise new_exc  # OtherError


def validate_option(option_name, option_value, allowed_values):
    """
    Validate the option value against the allowed option values
    and return the value, if it passes. raises EarlyExit otherwise.

    Raises:
      EarlyExit: Invalid command line usage.
    """
    if option_value not in allowed_values:
        raise EarlyExit(
            "Invalid value {val} for {opt} option. Allowed are: {allowed}".
            format(opt=option_name, val=option_value,
                   allowed=', '.join(allowed_values)))
    return option_value


def parse_yaml_file(yamlfile, name, schemafilename=None):
    """
    Returns the parsed content of a YAML file as a Python object.
    Optionally validates against a specified JSON schema file in YAML format.

    Raises:
        ImproperExit
    """

    try:
        with open(yamlfile, "r", encoding='utf-8') as fp:
            yaml_obj = yaml.safe_load(fp)
    except FileNotFoundError as exc:
        new_exc = ImproperExit(
            "Cannot find {} {}: {}".
            format(name, yamlfile, exc))
        new_exc.__cause__ = None  # pylint: disable=invalid-name
        raise new_exc
    except PermissionError as exc:
        new_exc = ImproperExit(
            "Permission error reading {} {}: {}".
            format(name, yamlfile, exc))
        new_exc.__cause__ = None  # pylint: disable=invalid-name
        raise new_exc
    except yaml.YAMLError as exc:
        new_exc = ImproperExit(
            "YAML error reading {} {}: {}".
            format(name, yamlfile, exc))
        new_exc.__cause__ = None  # pylint: disable=invalid-name
        raise new_exc

    if schemafilename:

        schemafile = os.path.join(
            os.path.dirname(__file__), 'schemas', schemafilename)
        try:
            with open(schemafile, 'r', encoding='utf-8') as fp:
                schema = yaml.safe_load(fp)
        except FileNotFoundError as exc:
            new_exc = ImproperExit(
                "Internal error: Cannot find schema file {}: {}".
                format(schemafile, exc))
            new_exc.__cause__ = None  # pylint: disable=invalid-name
            raise new_exc
        except PermissionError as exc:
            new_exc = ImproperExit(
                "Internal error: Permission error reading schema file {}: {}".
                format(schemafile, exc))
            new_exc.__cause__ = None  # pylint: disable=invalid-name
            raise new_exc
        except yaml.YAMLError as exc:
            new_exc = ImproperExit(
                "Internal error: YAML error reading schema file {}: {}".
                format(schemafile, exc))
            new_exc.__cause__ = None  # pylint: disable=invalid-name
            raise new_exc

        try:
            jsonschema.validate(yaml_obj, schema)
        except jsonschema.exceptions.SchemaError as exc:
            new_exc = ImproperExit(
                "Internal error: Invalid JSON schema file {}: {}".
                format(schemafile, exc))
            new_exc.__cause__ = None
            raise new_exc
        except jsonschema.exceptions.ValidationError as exc:
            element_str = json_path_str(exc.absolute_path)
            new_exc = ImproperExit(
                "Validation of {} {} failed on {}: {}".
                format(name, yamlfile, element_str, exc.message))
            new_exc.__cause__ = None
            raise new_exc

    return yaml_obj


def json_path_str(path_list):
    """
    Return a string with the path list in JSON path notation, except that
    the root element is not '$' but verbally expressed.
    """
    if not path_list:
        return "root elements"

    path_str = ""
    for p in path_list:
        if isinstance(p, int):
            path_str += "[{}]".format(p)
        else:
            path_str += ".{}".format(p)
    if path_str.startswith('.'):
        path_str = path_str[1:]
    return "element '{}'".format(path_str)


def get_hmc_info(session):
    """
    Return the result of the 'Query API Version' operation. This includes
    the HMC version, HMC name and other data. For details, see the operation's
    result description in the HMC WS API book.

    Raises: zhmccclient exceptions
    """
    client = zhmcclient.Client(session)
    hmc_info = client.query_api_version()
    return hmc_info


def logprint(log_level, print_level, message):
    """
    Log a message at the specified log level, and print the message at
    the specified verbosity level

    Parameters:
        log_level (int): Python logging level at which the message should be
          logged (logging.DEBUG, etc.), or None for no logging.
        print_level (int): Verbosity level at which the message should be
          printed (1, 2), or None for no printing.
        message (string): The message.
    """
    if print_level is not None and VERBOSE_LEVEL >= print_level:
        print(message)
    if log_level is not None and LOGGING_ENABLED:
        logger = logging.getLogger(LOGGER_NAME)
        # Note: This method never raises an exception. Errors during logging
        # are handled by calling handler.handleError().
        logger.log(log_level, message)


def setup_logging(log_dest, log_complevels, syslog_facility):
    """
    Set up Python logging as specified in the command line.

    Raises:
        EarlyExit
    """
    global LOGGING_ENABLED  # pylint: disable=global-statement

    if log_dest is None:
        logprint(None, PRINT_V, "Logging is disabled")
        handler = None
        dest_str = None
    elif log_dest == 'stderr':
        dest_str = "the Standard Error stream"
        logprint(None, PRINT_V, "Logging to {}".format(dest_str))
        handler = logging.StreamHandler(stream=sys.stderr)
    elif log_dest == 'syslog':
        system = platform.system()
        if system.startswith('CYGWIN_NT'):
            # Value is 'CYGWIN_NT-6.1'; strip off trailing version:
            system = 'CYGWIN_NT'
        try:
            address = SYSLOG_ADDRESS[system]
        except KeyError:
            address = SYSLOG_ADDRESS['other']
        dest_str = ("the System Log at address {a!r} with syslog facility "
                    "{slf!r}".format(a=address, slf=syslog_facility))
        logprint(None, PRINT_V, "Logging to {}".format(dest_str))
        try:
            facility = logging.handlers.SysLogHandler.facility_names[
                syslog_facility]
        except KeyError:
            valid_slfs = ', '.join(
                logging.handlers.SysLogHandler.facility_names.keys())
            raise EarlyExit(
                "This system ({sys}) does not support syslog facility {slf}. "
                "Supported are: {slfs}.".
                format(sys=system, slf=syslog_facility, slfs=valid_slfs))
        # The following does not raise any exception if the syslog address
        # cannot be opened. In that case, the first attempt to log something
        # will fail.
        handler = logging.handlers.SysLogHandler(
            address=address, facility=facility)
    else:
        dest_str = "file {fn}".format(fn=log_dest)
        logprint(None, PRINT_V, "Logging to {}".format(dest_str))
        try:
            handler = logging.FileHandler(log_dest)
        except OSError as exc:
            raise EarlyExit(
                "Cannot log to file {fn}: {exc}: {msg}".
                format(fn=log_dest, exc=exc.__class__.__name__, msg=exc))

    if not handler and log_complevels:
        raise EarlyExit(
            "--log-comp option cannot be used when logging is disabled; "
            "use --log option to enable logging.")

    if handler:

        def handleError(self, record):
            """
            Replacement for built-in method on logging.Handler class.

            This is needed because the SysLogHandler class does not raise
            an exception when creating the handler object, but only when
            logging something to it.
            """
            _, exc, _ = sys.exc_info()
            f_record = self.format(record)
            print("Error: Logging to {d} failed with: {exc}: {msg}. Formatted "
                  "log record: {r!r}".
                  format(d=dest_str, exc=exc.__class__.__name__, msg=exc,
                         r=f_record),
                  file=sys.stderr)
            sys.exit(1)

        handler.handleError = types.MethodType(handleError, handler)

        logger_level_dict = {}  # key: logger_name, value: level
        if not log_complevels:
            log_complevels = [DEFAULT_LOG_COMP]
        for complevel in log_complevels:
            if '=' in complevel:
                comp, level = complevel.split('=', 2)
            else:
                comp = complevel
                level = DEFAULT_LOG_LEVEL
            if level not in LOG_LEVELS:
                raise EarlyExit(
                    "Invalid log level {level!r} in --log-comp option. "
                    "Allowed are: {allowed}".
                    format(level=level, allowed=', '.join(VALID_LOG_LEVELS)))
            if comp == 'all':
                for logger_name in LOGGER_NAMES.values():
                    logger_level_dict[logger_name] = level
            else:
                try:
                    logger_name = LOGGER_NAMES[comp]
                except KeyError:
                    raise EarlyExit(
                        "Invalid component {comp!r} in --log-comp option. "
                        "Allowed are: {allowed}".
                        format(comp=comp,
                               allowed=', '.join(VALID_LOG_COMPONENTS)))
                logger_level_dict[logger_name] = level

        complevels = ', '.join(
            ["{name}={level}".format(name=name, level=level)
             for name, level in logger_level_dict.items()])
        logprint(None, PRINT_V,
                 "Logging components: {complevels}".
                 format(complevels=complevels))

        if isinstance(handler, logging.handlers.SysLogHandler):
            # Most syslog implementations fail when the message is longer
            # than a limit. We use a hard coded limit for now:
            # * 2048 is the typical maximum length of a syslog message,
            #   including its headers
            # * 41 is the max length of the syslog message parts before MESSAGE
            # * 47 is the max length of the Python format string before message
            # Example syslog message:
            #   <34>1 2003-10-11T22:14:15.003Z localhost MESSAGE
            # where MESSAGE is the formatted Python log message.
            max_msg = '.{}'.format(2048 - 41 - 47)
        else:
            max_msg = ''
        fs = ('%(asctime)s %(levelname)s %(name)s: %(message){m}s'.
              format(m=max_msg))

        # Set the formatter to always log times in UTC. Since the %z
        # formatting string does not get adjusted for that, set the timezone
        # offset always to '+0000'.
        dfs = '%Y-%m-%d %H:%M:%S+0000'
        logging.Formatter.converter = time.gmtime  # log times in UTC

        handler.setFormatter(logging.Formatter(fmt=fs, datefmt=dfs))
        for logger_name in LOGGER_NAMES.values():
            logger = logging.getLogger(logger_name)
            if logger_name in logger_level_dict:
                level = logger_level_dict[logger_name]
                level_int = LOG_LEVELS[level]
                if level_int != logging.NOTSET:
                    logger.addHandler(handler)
                logger.setLevel(level_int)
            else:
                logger.setLevel(logging.NOTSET)

        LOGGING_ENABLED = True

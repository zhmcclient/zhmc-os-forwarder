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
A class for storing forwarded LPARs and their syslog servers
"""

from .forwarder_config import ForwarderConfig


# pylint: disable=too-few-public-methods
class ForwardedLparInfo:
    """
    Info for a single forwarded LPAR
    """

    def __init__(self, lpar, syslogs=None, topic=None):
        self.lpar = lpar
        if not syslogs:
            syslogs = []
        self.syslogs = syslogs
        self.topic = topic


class ForwardedLpars:
    """
    A data structure to maintain forwarded LPARs and their syslog servers,
    based on the forwarder config.
    """

    def __init__(self, session, config_data, config_filename):
        """
        Parameters:
          session (zhmcclient.Session): Session with the HMC.
          config_data (dict): Content of forwarder config file.
          config_filename (string): Path name of forwarder config file.
        """
        self.session = session
        self.config_data = config_data
        self.config_filename = config_filename

        # Forwarder config for fast lookup
        self.config = ForwarderConfig(config_data, config_filename)

        # Representation of forwarded LPARs
        # - key: LPAR URI
        # - value: ForwardedLparInfo
        self.forwarded_lpar_infos = {}

    def __str__(self):
        return ("{s.__class__.__name__}("
                "config_filename={s.config_filename!r}"
                ")".format(s=self))

    def __repr__(self):
        return ("{s.__class__.__name__}("
                "config_filename={s.config_filename!r}, "
                "config={s.config!r}, "
                "forwarded_lpar_infos={s.forwarded_lpar_infos!r}"
                ")".format(s=self))

    def add_if_matching(self, lpar):
        """
        Add an LPAR to be forwarded if it matches a forwarding definition
        in the forwarder config.

        If the LPAR is already being forwarded, its syslog servers are changed
        to the syslog servers from the forwarder definition.

        Parameters:
          lpar (zhmcclient.Partition/Lpar or string): The LPAR, as a zhmcclient
            resource object or as a URI string.

        Returns:
            bool: Indicates whether the LPAR was added.
        """
        syslogs = self.config.get_syslogs(lpar)
        if syslogs:
            if lpar.uri not in self.forwarded_lpar_infos:
                self.forwarded_lpar_infos[lpar.uri] = ForwardedLparInfo(lpar)
            self.forwarded_lpar_infos[lpar.uri].syslogs = syslogs
            return True
        return False

    def remove(self, lpar):
        """
        Remove an LPAR from being forwarded.

        If the LPAR is not currently being forwarded, Nothing is done.

        Parameters:
          lpar (zhmcclient.Partition/Lpar or string): The LPAR, as a zhmcclient
            resource object or as a URI string.
        """
        if lpar.uri in self.forwarded_lpar_infos:
            del self.forwarded_lpar_infos[lpar.uri]

    def is_forwarding(self, lpar):
        """
        Return whether the LPAR is currently being forwarded.

        Parameters:
          lpar (zhmcclient.Partition/Lpar or string): The LPAR, as a zhmcclient
            resource object or as a URI string.

        Returns:
          bool: Indicates whether the LPAR is currently being forwarded.
        """
        return lpar.uri in self.forwarded_lpar_infos

    def get_syslogs(self, lpar):
        """
        Get the syslogs from the forwarder config for a forwarded LPAR.

        If the LPAR is not currently forwarded, returns None.

        Parameters:
          lpar (zhmcclient.Partition/Lpar or string): The LPAR, as a zhmcclient
            resource object or as a URI string.

        Returns:
          list of ConfigSyslogInfo: The syslogs for the LPAR, or None.
        """
        try:
            lpar_info = self.forwarded_lpar_infos[lpar.uri]
        except KeyError:
            return None
        return lpar_info.syslogs

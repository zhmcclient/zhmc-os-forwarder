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

import re

from collections import namedtuple


# Info for a single CPC pattern in the forwarder config
ConfigCpcInfo = namedtuple(
    'ConfigCpcInfo',
    [
        'cpc_pattern',          # string: Compiled pattern for CPC name
        'lpar_infos',           # List of ConfigLparInfo items
    ]
)


# Info for a single LPAR pattern in the forwarder config
# In context of a CPC pattern.
ConfigLparInfo = namedtuple(
    'ConfigLparInfo',
    [
        'lpar_pattern',         # string: Compiled pattern for LPAR name
        'syslog_servers',       # List of strings: Syslog servers for the LPAR
    ]
)


class ForwarderConfig:
    """
    A data structure to keep the forwarder config in an optimized way.
    """

    def __init__(self, config_data, config_filename):
        """
        Parameters:
          config_data (dict): Content of forwarder config file.
          config_filename (string): Path name of forwarder config file.
        """
        self.config_data = config_data
        self.config_filename = config_filename

        # Data for storing the config

        # Representation of forwarder config for fast lookup
        # - items: namedtuple ConfigCpcInfo
        self.config_cpc_infos = []

        forwarding = self.config_data['forwarding']
        # forwarding data structure in config file:
        #   forwarding:
        #     - syslogs:
        #        - server: 10.11.12.14
        #       cpcs:
        #         - cpc: CPC.*
        #           partitions:
        #             - partition: "dal1-.*"

        for fwd_item in forwarding:
            syslog_servers = []
            for sls_item in fwd_item['syslogs']:
                syslog_servers.append(sls_item['server'])
            for cpc_item in fwd_item['cpcs']:
                cpc_pattern = re.compile('^{}$'.format(cpc_item['cpc']))
                cpc_info = ConfigCpcInfo(cpc_pattern, [])
                for lpar_item in cpc_item['partitions']:
                    lpar_pattern = re.compile(
                        '^{}$'.format(lpar_item['partition']))
                    lpar_info = ConfigLparInfo(lpar_pattern, syslog_servers)
                    cpc_info.lpar_infos.append(lpar_info)
                self.config_cpc_infos.append(cpc_info)

    def __str__(self):
        return ("{s.__class__.__name__}("
                "config_filename={s.config_filename!r}"
                ")".format(s=self))

    def __repr__(self):
        return ("{s.__class__.__name__}("
                "config_filename={s.config_filename!r}, "
                "config_cpc_infos={s.config_cpc_infos!r}"
                ")".format(s=self))

    def get_syslog_servers(self, lpar):
        """
        Get the syslog servers for an LPAR if it matches the forwarder config.

        If it does not match the forwarder config, None is returned.

        Parameters:
          lpar (zhmcclient.Partition/Lpar): The LPAR, as a zhmcclient
            resource object.

        Returns:
          list of string: List of syslog servers if matching, or None
          otherwise.
        """
        cpc = lpar.manager.parent
        for cpc_info in self.config_cpc_infos:
            if cpc_info.cpc_pattern.match(cpc.name):
                for lpar_info in cpc_info.lpar_infos:
                    if lpar_info.lpar_pattern.match(lpar.name):
                        return lpar_info.syslog_servers
        return None

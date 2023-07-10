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
A class for running the forwarder server
"""

import os
import logging
import time
from threading import Thread, Event

import zhmcclient

from .forwarded_lpars import ForwardedLpars
from .utils import logprint, PRINT_ALWAYS, RETRY_TIMEOUT_CONFIG, PRINT_V


class ForwarderServer:
    """
    A forwarder server.
    """

    def __init__(self, config_data, config_filename):
        """
        Parameters:
          config_data (dict): Content of forwarder config file.
          config_filename (string): Path name of forwarder config file.
        """
        self.config_data = config_data
        self.config_filename = config_filename

        self.thread = Thread(target=self.run)  # forwarder thread
        self.stop_event = Event()  # Set event to stop forwarder thread

        self.session = None  # zhmcclient.Session with the HMC

        self.all_cpcs = None  # List of all managed CPCs as zhmcclient.Cpc
        self.all_lpars = None  # List of all partitions/LPARs as zhmcclient obj

        self.forwarded_lpars = None  # ForwardedLpars object

    def startup(self):
        """
        Set up the forwarder server and start the forwarder thread.
        """

        hmc_data = self.config_data['hmc']
        # hmc data structure in config file:
        #   hmc:
        #     hmc: 10.11.12.13
        #     userid: "myuser"
        #     password: "mypassword"
        #     verify_cert: false

        verify_cert = hmc_data.get('verify_cert', True)
        if isinstance(verify_cert, str):
            if not os.path.isabs(verify_cert):
                verify_cert = os.path.join(
                    os.path.dirname(self.config_filename), verify_cert)

        logprint(logging.INFO, PRINT_ALWAYS,
                 "Opening session with HMC {h} "
                 "(user: {u}, certificate validation: {c})".
                 format(h=hmc_data['host'], u=hmc_data['userid'],
                        c=verify_cert))

        self.session = zhmcclient.Session(
            hmc_data['host'],
            hmc_data['userid'],
            hmc_data['password'],
            verify_cert=verify_cert,
            retry_timeout_config=RETRY_TIMEOUT_CONFIG)

        client = zhmcclient.Client(self.session)

        logprint(logging.INFO, PRINT_V,
                 "Gathering information about CPCs and LPARs to forward")
        self.all_cpcs = client.cpcs.list()
        self.all_lpars = []
        for cpc in self.all_cpcs:
            dpm = cpc.prop('dpm-enabled')
            if dpm:
                self.all_lpars.extend(cpc.partitions.list())
            else:
                self.all_lpars.extend(cpc.lpars.list())

        self.forwarded_lpars = ForwardedLpars(
            self.session, self.config_data, self.config_filename)

        self._start()

    def shutdown(self):
        """
        Stop the forwarder thread and clean up the forwarder server.
        """

        try:

            if self.thread:
                logprint(logging.INFO, PRINT_ALWAYS,
                         "Stopping forwarder thread")
                self._stop()

            # logprint(logging.INFO, PRINT_ALWAYS,
            #          "Cleaning up partition notifications on HMC")
            # for lpar_tuple in self.forwarded_lpars.values():
            #     lpar = lpar_tuple[0]
            #     try:
            #         lpar.disable_auto_update()
            #     except zhmcclient.HTTPError as exc:
            #         if exc.http_status == 403:
            #             # The session does not exist anymore
            #             pass

            if self.session:
                logprint(logging.INFO, PRINT_ALWAYS,
                         "Closing session with HMC")
                try:
                    self.session.logoff()
                except zhmcclient.HTTPError as exc:
                    if exc.http_status == 403:
                        # The session does not exist anymore
                        pass
                self.session = None

        except zhmcclient.Error as exc:
            logprint(logging.ERROR, PRINT_ALWAYS,
                     "Error when cleaning up: {}".format(exc))

    def _start(self):
        """
        Start the forwarder thread.
        """
        self.stop_event.clear()
        self.thread.start()

    def _stop(self):
        """
        Stop the forwarder thread.
        """
        self.stop_event.set()
        self.thread.join()

    def run(self):
        """
        The method running as the forwarder server thread.
        """
        logprint(logging.INFO, PRINT_ALWAYS,
                 "Entering forwarder thread")
        while True:

            # TODO: Implement the forwarding
            time.sleep(1)

            if self.stop_event.is_set():
                break

        logprint(logging.INFO, PRINT_ALWAYS,
                 "Leaving forwarder thread")

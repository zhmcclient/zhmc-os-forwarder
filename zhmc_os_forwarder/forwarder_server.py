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
import socket
from threading import Thread, Event

import zhmcclient

from .forwarded_lpars import ForwardedLpars
from .utils import logprint, PRINT_ALWAYS, PRINT_V, PRINT_VV, \
    RETRY_TIMEOUT_CONFIG


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

        self.receiver = None  # NotificationReceiver

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

        for lpar in self.all_lpars:
            cpc = lpar.manager.parent
            added = self.forwarded_lpars.add_if_matching(lpar)
            if added:
                logprint(logging.INFO, PRINT_V,
                         "LPAR {p!r} on CPC {c!r} will be forwarded".
                         format(p=lpar.name, c=cpc.name))

        self.receiver = zhmcclient.NotificationReceiver(
            [],  # self.session.object_topic to get notifications to ignore
            hmc_data['host'],
            hmc_data['userid'],
            hmc_data['password'])

        logger_id = 0  # ID number used in Python logger name
        for lpar_info in self.forwarded_lpars.forwarded_lpar_infos.values():
            lpar = lpar_info.lpar
            cpc = lpar.manager.parent

            logprint(logging.INFO, PRINT_VV,
                     "Opening OS message channel for LPAR {p!r} on CPC {c!r}".
                     format(p=lpar.name, c=cpc.name))
            try:
                os_topic = lpar.open_os_message_channel(
                    include_refresh_messages=True)
            except zhmcclient.HTTPError as exc:
                if exc.http_status == 409 and exc.reason == 331:
                    # OS message channel is already open for this session,
                    # reuse its notification topic.
                    topic_dicts = self.session.get_notification_topics()
                    os_topic = None
                    for topic_dict in topic_dicts:
                        if topic_dict['topic-type'] != \
                                'os-message-notification':
                            continue
                        obj_uri = topic_dict['object-uri']
                        if lpar.uri == obj_uri:
                            os_topic = topic_dict['topic-name']
                            logprint(logging.INFO, PRINT_VV,
                                     "Using existing OS message notification "
                                     "topic {t!r} for LPAR {p!r} on CPC {c!r}".
                                     format(t=os_topic, p=lpar.name,
                                            c=cpc.name))
                            break
                    if os_topic is None:
                        raise RuntimeError(
                            "An OS message notification topic for LPAR {p!r} "
                            "on CPC {c!r} supposedly exists, but cannot be "
                            "found in the existing topics for this session: "
                            "{t}".
                            format(p=lpar.name, c=cpc.name, t=topic_dicts))
                if exc.http_status == 409 and exc.reason == 332:
                    # The OS does not support OS messages.
                    logprint(logging.WARNING, PRINT_ALWAYS,
                             "Warning: The OS in LPAR {p!r} on CPC {c!r} does "
                             "not support OS messages - ignoring the LPAR".
                             format(p=lpar.name, c=cpc.name))
                else:
                    raise
            self.receiver.subscribe(os_topic)
            lpar_info.topic = os_topic

            # Prepare sending to syslogs by creating Python loggers
            for syslog in self.forwarded_lpars.get_syslogs(lpar):
                try:
                    logger = self._create_logger(syslog, logger_id)
                except ConnectionError as exc:
                    logprint(logging.WARNING, PRINT_ALWAYS,
                             "Warning: Skipping syslog server: {}".format(exc))
                    continue
                logger_id += 1
                syslog.logger = logger

        self._start()

    @staticmethod
    def _create_logger(syslog, logger_id):
        facility_code = logging.handlers.SysLogHandler.facility_names[
            syslog.facility]
        if syslog.port_type == 'tcp':
            # Newer syslog protocols, e.g. rsyslog
            socktype = socket.SOCK_STREAM
        else:
            assert syslog.port_type == 'udp'
            # Older syslog protocols, e.g. BSD
            socktype = socket.SOCK_DGRAM
        try:
            handler = logging.handlers.SysLogHandler(
                (syslog.host, syslog.port), facility_code,
                socktype=socktype)
        except Exception as exc:
            raise ConnectionError(
                "Cannot create log handler for syslog server at "
                "{host}, port {port}/{port_type}: {msg}".
                format(host=syslog.host, port=syslog.port,
                       port_type=syslog.port_type, msg=str(exc)))
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger_name = 'zhmcosfwd_syslog_{}'.format(logger_id)
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def shutdown(self):
        """
        Stop the forwarder thread and clean up the forwarder server.
        """

        try:

            for lpar_info in self.forwarded_lpars.forwarded_lpar_infos.values():
                lpar = lpar_info.lpar
                cpc = lpar.manager.parent

                logprint(logging.INFO, PRINT_VV,
                         "Unsubscribing OS message channel for LPAR {p!r} on "
                         "CPC {c!r}".
                         format(p=lpar.name, c=cpc.name))
                self.receiver.unsubscribe(lpar_info.topic)

            logprint(logging.INFO, PRINT_ALWAYS,
                     "Closing notification receiver")
            self.receiver.close()

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
        logprint(logging.INFO, PRINT_V,
                 "Entering forwarder thread")
        while True:

            if self.stop_event.is_set():
                break

            try:
                # pylint: disable=unused-variable
                for headers, message in self.receiver.notifications():
                    self.handle_notification(headers, message)

            except zhmcclient.NotificationJMSError as exc:
                logprint(logging.ERROR, PRINT_ALWAYS,
                         "Error receiving notifications {}: {}".
                         format(exc.__class__.__name__, exc))
                logprint(logging.ERROR, PRINT_ALWAYS,
                         "Receiving notifications again")

        logprint(logging.INFO, PRINT_V,
                 "Leaving forwarder thread")

    def handle_notification(self, headers, message):
        """
        Handle a received notification.
        """
        noti_type = headers['notification-type']
        if noti_type == 'os-message':
            for msg_info in message['os-messages']:
                lpar_uri = headers['object-uri']
                lpar_infos = self.forwarded_lpars.forwarded_lpar_infos
                lpar_info = lpar_infos[lpar_uri]
                lpar = lpar_info.lpar
                seq_no = msg_info['sequence-number']
                msg_txt = msg_info['message-text'].strip('\n')
                self.send_to_syslogs(lpar, seq_no, msg_txt)
        else:
            dest = headers['destination']
            sub_id = headers['subscription']
            obj_class = headers['class']
            obj_name = headers['name']
            logprint(logging.WARNING, PRINT_ALWAYS,
                     "Warning: Ignoring {nt!r} notification for {c} {n!r} "
                     "(subscription: {s}, destination: {d})".
                     format(nt=noti_type, c=obj_class, n=obj_name, s=sub_id,
                            d=dest))

    def send_to_syslogs(self, lpar, seq_no, msg_txt):
        """
        Send a single OS message to the configured syslogs for its LPAR.
        """
        cpc = lpar.manager.parent
        for syslog in self.forwarded_lpars.get_syslogs(lpar):
            if syslog.logger:
                syslog_txt = ('{c} {p} {s}: {m}'.
                              format(c=cpc.name, p=lpar.name, s=seq_no,
                                     m=msg_txt))
                try:
                    syslog.logger.info(syslog_txt)
                # pylint: disable=broad-exception-caught
                except Exception as exc:
                    logprint(logging.WARNING, PRINT_ALWAYS,
                             "Warning: Cannot send seq_no {s} from LPAR {p!r} "
                             "on CPC {c!r} to syslog host {h}: {m}".
                             format(s=seq_no, p=lpar.name, c=cpc.name,
                                    h=syslog.host, m=exc))
                    continue

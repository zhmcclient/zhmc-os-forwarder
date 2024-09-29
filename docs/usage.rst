.. Copyright 2023 IBM Corp. All Rights Reserved.
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

Usage
=====

This section describes how to use the forwarder beyond the quick introduction
in :ref:`Quickstart`.


Running on a system
-------------------

If you want to run the forwarder on some system (e.g. on your workstation for
trying it out), it is recommended to use a virtual Python environment.

With the virtual Python environment active, follow the steps in
:ref:`Quickstart` to install, establish the required files, and to run the
forwarder.


Running in a Docker container
-----------------------------

If you want to run the forwarder in a Docker container you can create the
container as follows, using the Dockerfile provided in the Git repository.

* Clone the Git repository of the forwarder and switch to the clone's root
  directory:

  .. code-block:: bash

      $ git clone https://github.com/zhmcclient/zhmc-os-forwarder
      $ cd zhmc-os-forwarder

* Build a local Docker image as follows:

  .. code-block:: bash

      $ make docker

  This builds a container image named ``zhmc_os_forwarder:latest`` in your local
  Docker environment.

  The image does not contain the forwarder config file, so that needs to be
  specified when starting the container.

* Run the local Docker image as follows:

  .. code-block:: bash

      $ docker run --rm -v $(pwd)/myconfig:/root/myconfig zhmc_os_forwarder -p 514:514 -c /root/myconfig/config.yaml -v

  In this command, the forwarder config file is provided on the local system
  as ``./myconfig/config.yaml``. The ``-v`` option of 'docker run' mounts the
  ``./myconfig`` directory to ``/root/myconfig`` in the container's file system.
  The ``-c`` option of the forwarder references the forwarder config file as it
  appears in the container's file system.

  The command above maps port 514 in the docker container to port 514 of the
  system running docker. That is the default port used by syslog. If your remote
  syslog servers use different ports, they need to be mapped using the ``-p`` option
  of the ``docker run`` command.


zhmc_os_forwarder command
-------------------------

The ``zhmc_os_forwarder`` command supports the following arguments:

.. When updating the command help, use a 100 char wide terminal
.. code-block:: text

    usage: zhmc_os_forwarder [-h] [-c CONFIG_FILE] [--log DEST] [--log-comp COMP[=LEVEL]]
                             [--syslog-facility TEXT] [--verbose] [--version] [--help-config]

    IBM Z HMC OS Message Forwarder

    optional arguments:

      -h, --help            show this help message and exit

      -c CONFIG_FILE        path name of config file. Use --help-config for details. Default:
                            /etc/zhmc-os-forwarder/config.yaml

      --log DEST            enable logging and set a log destination (stderr, syslog, FILE). Default:
                            no logging

      --log-comp COMP[=LEVEL]
                            set a logging level (error, warning, info, debug, off, default: warning)
                            for a component (forwarder, hmc, jms, all). May be specified multiple
                            times; options add to the default of: all=warning

      --syslog-facility TEXT
                            syslog facility (user, local0, local1, local2, local3, local4, local5,
                            local6, local7) when logging to the system log. Default: user

      --verbose, -v         increase the verbosity level (max: 2)

      --version             show versions of forwarder and zhmcclient library and exit

      --help-config         show help for forwarder config file and exit


Setting up the HMC
------------------

Usage of this package requires that the HMC in question is prepared
accordingly:

* The Web Services API must be enabled on the HMC.

  You can do that in the HMC GUI by selecting "HMC Management" in the left pane,
  then opening the "Configure API Settings" icon on the pain pane,
  then selecting the "Web Services" tab on the page that comes up, and
  finally enabling the Web Services API on that page.

  The above is on a z16 HMC, it may be different on older HMCs.

  If you cannot find this icon, then your userid does not have permission
  for the respective task on the HMC. In that case, there should be some
  other HMC admin you can go to to get the Web Services API enabled.


Setting up firewalls or proxies
-------------------------------

If you have to configure firewalls or proxies between the system where you
run the ``zhmc_os_forwarder`` command and the HMC, the following ports
need to be opened:

* 6794 (TCP) - for the HMC API HTTP server
* 61612 (TCP) - for the HMC API message broker via JMS over STOMP

For details, see sections "Connecting to the API HTTP server" and
"Connecting to the API message broker" in the :term:`HMC API` book.


HMC userid requirements
-----------------------

This section describes the requirements on the HMC userid that is used by
the ``zhmc_os_forwarder`` command.

The HMC userid must have the following permissions:

* Object access permission to the following
  objects:

  - LPARs for which OS messages should be forwarded
  - CPCs containing these LPARs

* Task permission for the following
  tasks:

  - "Operating System Messages" task (view-only mode is sufficient)


HMC certificate
---------------

By default, the HMC is configured with a self-signed certificate. That is the
X.509 certificate presented by the HMC as the server certificate during TLS
handshake at its Web Services API.

The 'zhmc_os_forwarder' command will reject self-signed certificates by default.

The HMC should be configured to use a CA-verifiable certificate. This can be
done in the HMC task "Certificate Management". See also the :term:`HMC Security`
book and Chapter 3 "Invoking API operations" in the :term:`HMC API` book.

The 'zhmc_os_forwarder' command provides control knobs for the verification of
the HMC certificate via the ``verify_cert`` attribute in the
:ref:`forwarder config file`, as follows:

* Not specified or specified as ``true`` (default): Verify the HMC certificate
  using the CA certificates from the first of these locations:

  - The certificate file or directory in the ``REQUESTS_CA_BUNDLE`` environment
    variable, if set
  - The certificate file or directory in the ``CURL_CA_BUNDLE`` environment
    variable, if set
  - The `Python 'certifi' package <https://pypi.org/project/certifi/>`_
    (which contains the
    `Mozilla Included CA Certificate List <https://wiki.mozilla.org/CA/Included_Certificates>`_).

* Specified with a string value: An absolute path or a path relative to the
  directory of the forwarder config file. Verify the HMC certificate using the CA
  certificates in the specified certificate file or directory.

* Specified as ``false``: Do not verify the HMC certificate.
  Not verifying the HMC certificate means that hostname mismatches, expired
  certificates, revoked certificates, or otherwise invalid certificates will not
  be detected. Since this mode makes the connection vulnerable to
  man-in-the-middle attacks, it is insecure and should not be used in production
  environments.

If a certificate file is specified (using any of the ways listed above), that
file must be in PEM format and must contain all CA certificates that are
supposed to be used. Usually they are in the order from leaf to root, but
that is not a hard requirement. The single certificates are concatenated
in the file.

If a certificate directory is specified (using any of the ways listed above),
it must contain PEM files with all CA certificates that are supposed to be used,
and copies of the PEM files or symbolic links to them in the hashed format
created by the OpenSSL command ``c_rehash``.

An X.509 certificate in PEM format is base64-encoded, begins with the line
``-----BEGIN CERTIFICATE-----``, and ends with the line
``-----END CERTIFICATE-----``.
More information about the PEM format is for example on this
`www.ssl.com page <https://www.ssl.com/guide/pem-der-crt-and-cer-x-509-encodings-and-conversions>`_
or in this `serverfault.com answer <https://serverfault.com/a/9717/330351>`_.

Note that setting the ``REQUESTS_CA_BUNDLE`` or ``CURL_CA_BUNDLE`` environment
variables influences other programs that use these variables, too.

For more information, see the
`Security <https://python-zhmcclient.readthedocs.io/en/latest/security.html>`_
section in the documentation of the 'zhmcclient' package.


Forwarder config file
---------------------

The *forwarder config file* tells the forwarder which HMC to use, and for which
CPCs and LPARs it should forward OS messages to which syslog servers.

The forwarder config file is in YAML format and has the following structure:

.. code-block:: yaml

    hmc:
      host: {hmc-ip-address}
      userid: {hmc-userid}
      password: {hmc-password}
      verify_cert: {verify-cert}

    forwarding:
      # list of forwarding definitions
      - syslogs:
         # list of remote syslog servers
         - host: {syslog-ip-address}
           port: {syslog-port}
           port_type: {syslog-port-type}
           facility: {syslog-facility}
        cpcs:
          # list of CPCs
          - cpc: {cpc-pattern}
            partitions:
              # list of LPARs
              - partition: {partition-pattern}

Where:

* ``{hmc-ip-address}`` is the IP address of the HMC.

* ``{hmc-userid}`` is the userid on the HMC to be used for logging on.

* ``{hmc-password}`` is the password of that userid.

* ``{verify-cert}`` controls whether and how the HMC server certificate is
  verified. For details, see :ref:`HMC certificate`.

* ``{cpc-pattern}`` is a :term:`regular expression` for the CPC name, to
  select CPCs from the set of CPCs managed by the targeted HMC.

* ``{partition-pattern}`` is a :term:`regular expression` for the LPAR name, to
  select LPARs from the CPC (or set of CPCs) specified in ``{cpc-pattern}``.

Each item in the ``forwarding`` list is a forwarding definition that specifies
a list of remote syslog servers and a list of LPARs (along with their CPCs)
The OS messages of the specified LPARs will be forwarded to the remote
syslog servers. In other words, the forwarding definitions are organized
by the targeted syslog servers.


Example forwarder config file
-----------------------------

The following is an example forwarder config file.

The file can be downloaded from the Git repo as
`examples/config_example.yaml <https://github.com/zhmcclient/zhmc-os-forwarder/blob/master/examples/config_example.yaml>`_.

.. literalinclude:: ../examples/config_example.yaml
  :language: yaml


Logging
-------

The forwarder supports logging its own activities and the interactions with the
HMC. Note that this kind of logging has nothing to do with the forwarding of
OS messages to remote syslog servers.

By default, logging is disabled.

Logging is enabled by using the ``--log DEST`` option that controls the
logging destination as follows:

* ``--log stderr`` - log to the Standard Error stream
* ``--log syslog`` - log to the System Log (see :ref:`Logging to the System Log`)
* ``--log FILE`` - log to the log file with path name ``FILE``.

There are multiple components that can log. By default, all of them log at the
warning level. This can be fine tuned by using the ``--log-comp COMP[=LEVEL]``
option. This option can be specified multiple times, and the specified options
add in sequence to the default of ``all=warning``.

The components that can be specified in ``COMP`` are:

* ``forwarder`` - activities of the forwarder.
  Logger name: ``zhmcforwarder``.
* ``hmc`` - HTTP interactions with the HMC performed by the zhmcclient library.
  Logger name: ``zhmcclient.hmc``.
* ``jms`` - JMS notifications from the HMC received by the zhmcclient library.
  Logger name: ``zhmcclient.jms``.
* ``all`` - all of these components.

The log levels that can be specified in ``LEVEL`` are:

* ``error`` - Show only errors for the component. Errors are serious conditions
  that need to be fixed by the user. Some errors may need to be reported as
  issues. The forwarder retries with the HMC in case of certain errors, but some
  errors cause the forwarder to terminate.
* ``warning`` - Show errors and warnings for the component. Warnings never cause
  the forwarder to terminate, but should be analyzed and may need to be fixed.
* ``info`` - Show informations, warnings and errors for the component.
  Informations are useful to understand what is going on.
* ``debug`` - Show debug info, informations, warnings and errors for the
  component. Debug info provides a very detailed amount of information that may
  be useful foo analyzing problems.
* ``off`` - Show no log messages for the component.

The ``LEVEL`` part can be omitted in the ``--log-comp`` option, and its
default is ``warning``. This is for compatibility with older versions of the
forwarder.

The default log level for each component is ``warning``, and specifying
other log levels changes that level only for the specified components but
keeps the default for those components that are not specified.

Examples:

.. code-block:: bash

    # log to Standard Error with all=warning
    $ zhmc_os_forwarder --log stderr ...

    # log to file mylog.log with all=warning
    $ zhmc_os_forwarder --log mylog.log ...

    # log to file mylog.log with forwarder=info, hmc=warning (by default), jms=warning (by default)
    $ zhmc_os_forwarder --log mylog.log --log-comp forwarder=info

    # log to file mylog.log with forwarder=info, hmc=warning (by default), jms=debug
    $ zhmc_os_forwarder --log mylog.log --log-comp forwarder=info --log-comp jms=debug

    # log to file mylog.log with forwarder=debug, hmc=debug, jms=debug
    $ zhmc_os_forwarder --log mylog.log --log-comp all=debug

    # log to file mylog.log with forwarder=info, hmc=off, jms=off
    $ zhmc_os_forwarder --log mylog.log --log-comp all=off --log-comp forwarder=info


Logging to the System Log
^^^^^^^^^^^^^^^^^^^^^^^^^

When logging its own activities and the interactions with the HMC to the
System Log, the syslog address used by the forwarder depends on the operating
system the forwarder runs on, as follows:

* Linux: ``/dev/log``
* macOS: ``/var/run/syslog``
* Windows: UDP port 514 on localhost (requires a syslog demon to run)
* CygWin: ``/dev/log`` (requires the syslog-ng package to be installed)

For other operating systems, UDP port 514 on localhost is used.

Messages logged to the system log will only show up there if the syslog
configuration has enabled the syslog facility and the syslog severity levels
that are used by the forwarder.
The configuration of the syslog depends on the operating system or syslog demon
that is used and is therefore not described here.

The syslog facility that will be used by the forwarder can be specified with the
``--syslog-facility`` option and defaults to ``user``.

The syslog severity levels (not to be confused with syslog priorities) that will
be used by the forwarder are derived from the Python log levels using the default
mapping defined by Python logging, which is:

================  =================
Python log level  Syslog severity
================  =================
``ERROR``         3 (Error)
``WARNING``       4 (Warning)
``INFO``          6 (Informational)
``DEBUG``         7 (Debug)
================  =================

On some systems, the syslog rejects messages that exceed a certain limit.
For this reason, the forwarder truncates the message text to somewhat below
2048 Bytes, when logging to the system log. Messages are not truncated when
logging to the Standard Error stream or to a file.

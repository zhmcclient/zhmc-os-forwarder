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

Introduction
============

.. image:: https://img.shields.io/pypi/v/zhmc-os-forwarder.svg
    :target: https://pypi.python.org/pypi/zhmc-os-forwarder/
    :alt: Version on Pypi

.. image:: https://github.com/zhmcclient/zhmc-os-forwarder/workflows/test/badge.svg?branch=master
    :target: https://github.com/zhmcclient/zhmc-os-forwarder/actions?query=branch%3Amaster
    :alt: Test status (master)

.. image:: https://readthedocs.org/projects/zhmc-os-forwarder/badge/?version=latest
    :target: https://readthedocs.org/projects/zhmc-os-forwarder/builds/
    :alt: Docs status (master)

.. image:: https://coveralls.io/repos/github/zhmcclient/zhmc-os-forwarder/badge.svg?branch=master
    :target: https://coveralls.io/github/zhmcclient/zhmc-os-forwarder?branch=master
    :alt: Test coverage (master)

The **IBM Z HMC OS Message Forwarder** connects to the console of operating
systems running in LPARs on Z systems and forwards the messages written by the
operating systems in the LPARs to remote syslog serverss.

The Z systems can be in classic or DPM operational mode.

The forwarder attempts to stay up as much as possible, for example it performs
automatic session renewals with the HMC if the logon session expires, and it
survives HMC reboots and automatically resumes forwarding again once
the HMC come back up, without loosing or duplicating any messages.

Supported environments
----------------------

* Operating systems: Linux, macOS, Windows
* Python versions: 3.5 and higher
* HMC versions: 2.11.1 and higher

Quickstart
----------

* Install the forwarder and all of its Python dependencies as follows:

  .. code-block:: bash

      $ pip install zhmc-os-forwarder

* Provide a *config file* for use by the forwarder.

  The config file tells the forwarder which HMC to use, and for which CPCs
  and LPARs it should forward to which syslog servers.

  Download the :ref:`Example forwarder config file` and edit that copy according
  to your needs.

  For details, see :ref:`Forwarder config file`.

* Run the forwarder as follows:

  .. code-block:: bash

      $ zhmc_os_forwarder -c config.yaml
      zhmc_os_forwarder version: 0.2.0
      zhmcclient version: 1.10.0
      Verbosity level: 0
      Opening session with HMC 10.11.12.13 (user: johndoe@us.ibm.com, certificate validation: False)
      Forwarder is up and running (Press Ctrl-C to shut down)

* Look at the syslogs you have configured in the config file and verify that
  OS messages show up there.

Limitations
-----------

At this point, the forwarder has several limitations. All of them are intended
to be resolved in future releases.

* The forwarder does not recover from HMC restart or connection loss
* Restarting the forwarder will send again all OS messages the HMC has buffered
* New and deleted LPARs in DPM mode are not automatically detected.

Reporting issues
----------------

If you encounter a problem, please report it as an `issue on GitHub`_.

.. _issue on GitHub: https://github.com/zhmcclient/zhmc-os-forwarder/issues

License
-------

This package is licensed under the `Apache 2.0 License`_.

.. _Apache 2.0 License: http://apache.org/licenses/LICENSE-2.0

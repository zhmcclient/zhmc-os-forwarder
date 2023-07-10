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

IBM Z HMC OS Message Forwarder
==============================

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
systems and forwards the OS messages on the console to a remote syslog server.

The forwarder attempts to stay up as much as possible, for example it performs
automatic session renewals with the HMC if the logon session expires, and it
survives HMC reboots and automatically picks up message forwarding at the
right message sequence number once the HMC come back up.

.. _IBM Z: https://www.ibm.com/it-infrastructure/z

Documentation
-------------

* `Documentation`_
* `Change log`_

.. _Documentation: https://zhmc-os-forwarder.readthedocs.io/en/stable/
.. _Change log: https://zhmc-os-forwarder.readthedocs.io/en/stable/changes.html

Quickstart
----------

* Install the forwarder and all of its Python dependencies as follows:

  .. code-block:: bash

      $ pip install zhmc-os-forwarder

* Provide a config file for use by the forwarder.

  The config file tells the forwarder which HMC to use, and for which CPCs
  and partitions it should forward to which syslog servers.

  Download the `example config file`_ as ``config.yaml`` and edit that copy
  according to your environment.

  For details, see `forwarder config file`_.

.. _forwarder config file: https://zhmc-os-forwarder.readthedocs.io/en/stable/usage.html#hmc-credentials-file
.. _example config file: examples/config_example.yaml

* Run the forwarder as follows:

  .. code-block:: bash

      $ zhmc_os_forwarder -c config.yaml

Reporting issues
----------------

If you encounter a problem, please report it as an `issue on GitHub`_.

.. _issue on GitHub: https://github.com/zhmcclient/zhmc-os-forwarder/issues

License
-------

This package is licensed under the `Apache 2.0 License`_.

.. _Apache 2.0 License: http://apache.org/licenses/LICENSE-2.0

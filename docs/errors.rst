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

Troubleshooting
===============

This section describes some issues and how to resolve them. If you encounter
an issue that is not covered here, please report it (see :ref:`Reporting issues`).

Permission denied on forwarder config file
------------------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Error: Permission error reading forwarder config file foo.yaml: [Errno 13] Permission denied: 'foo.yaml'

You don't have permission to read from the forwarder config file. Change the permissions with
``chmod``, check ``man chmod`` if you are unfamiliar with it.

Forwarder config file not found
-------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Error: Cannot find forwarder config file foo.yaml: [Errno 2] No such file or directory: 'foo.yaml'

Specify the right path name. Relative path names are relative to the current
directory.

Forwarder config file has YAML syntax issues
--------------------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Error: YAML error reading forwarder config file foo.yaml: <... error details ...>

There is a YAML syntax error in the forwarder config file. The error details
provide the actual information on what is wrong.

You can also check the `YAML specification`_.

.. _YAML specification: http://yaml.org/spec/1.2/spec.html

Forwarder config file does not validate
---------------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Error: Validation of forwarder config file foo.yaml failed <... error details ...>

The YAML syntax of the forwarder config file is correct, but there is an issue
with its content (i.e. schema). The error details provide the actual information
on what is wrong.

You can also check :ref:`Forwarder config file`.

Timeout accessing HMC
---------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Opening session with HMC 99.99.99.99 (user: johndoe@us.ibm.com, certificate validation: False)
  zhmcclient._exceptions.ConnectTimeout: HTTPSConnectionPool(host='99.99.99.99', port=6794): Max retries exceeded
    with url: /api/sessions (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x10489fa00>,
    'Connection to 99.99.99.99 timed out. (connect timeout=10)')), reason: (<urllib3.connection.HTTPSConnection object
    at 0x10489fa00>, 'Connection to 99.99.99.99 timed out. (connect timeout=10)')

The HMC cannot be reached. Make sure the IP address is correct, and the VPN,
firewall logon, or proxy logon you may need to access the HMC are in place.

Authentication error accessing HMC
----------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder -c foo.yaml
  Opening session with HMC 10.11.12.13 (user: johndoe@us.ibm.com, certificate validation: False)
  zhmcclient._exceptions.ServerAuthError: HTTP authentication failed with 403,0: Login failed.
    Try the operation again.  If the problem persists, contact your security administrator.

The HMC could be reached but rejects the login at the WS API. Reasons may be wrong
user/password, or Web Services API in the HMC not enabled. For the latter, see
:ref:`Setting up the HMC`.

Warning: LPAR does not support OS messages
------------------------------------------

Example:

.. code-block:: bash

  $ zhmc_os_forwarder
  . . .
  Warning: The OS in LPAR 'foo' on CPC 'CPCA' does not support OS messages - ignoring the LPAR

This indicates that the operating system in the LPAR does not support writing
its console via the console API. The LPAR is being ignored, but the forwarder
otherwise keeps on running.

zhmcclient troubleshooting
--------------------------

The `zhmcclient Troubleshooting <https://python-zhmcclient.readthedocs.io/en/latest/appendix.html#troubleshooting>`_
section also applies to the forwarder.

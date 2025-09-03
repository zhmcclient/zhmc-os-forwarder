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

Appendix
========


Glossary
--------

.. glossary::

    forwarder
        The **IBM Z HMC OS Message Forwarder** described in this document.

    forwarder config file
        A YAML file with the configuration for the :term:`forwarder`.
        For details, see :term:`Forwarder config file`.

    LPAR
    logical partition
    partition
        Logical partitions are, in practice, equivalent to separate Z systems.
        Each logical partition runs its own operating system.

        See also `Mainframe hardware: Logical partitions (LPARs) <https://www.ibm.com/docs/en/zos-basic-skills?topic=design-mainframe-hardware-logical-partitions-lpars>`_.

        The HMC Web Services API (see :term:`HMC API`) has two distinct resource
        types: "partition" when the Z system is in the DPM operational mode, and
        "logical-partition" when the Z system is in the classic operational
        mode, but it is the same concept.

        Even though the :term:`forwarder` supports Z systems in both operational
        modes, this document uses the single term "LPAR" for simplicity.

    regular expression
        Regular expressions in the :term:`forwarder config files <forwarder config file>`
        are standard `Python regular expressions <https://docs.python.org/3/library/re.html>`_.

    Z system
    CPC
        A Z system is a server with s390x CPU architecture. The size of a Z
        system can range from a set of 19-inch drawers up to multiple racks.
        The boundaries of a Z system are defined by its CPU, memory and IO
        boundaries, and not by its rack boundaries.
        The :term:`HMC API` book uses the resource type "cpc" and term "CPC"
        for a Z system.


Bibliography
------------

.. glossary::

   HMC API
       `IBM SC27-2646-00, IBM Z Hardware Management Console Web Services API (Version 2.17.0) <https://www.ibm.com/docs/ko/module_1721331501652/pdf/SC27-2646-00.pdf>`_

   HMC Security
       `IBM SC28-7061-00, IBM Z Hardware Management Console Security (Version 2.17.0) <https://www.ibm.com/docs/ko/module_1721331501652/pdf/SC28-7061-00.pdf>`_

   HMC Help
       `IBM Z Hardware Management Console Help (Version 2.17.0) <https://www.ibm.com/docs/en/help-ibm-hmc-z17>`

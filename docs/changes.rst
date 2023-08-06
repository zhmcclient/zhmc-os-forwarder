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


Change log
----------


Version 0.2.0
^^^^^^^^^^^^^

Released: 2023-08-06

**Bug fixes:**

* Improved the cleanup when exiting the forwarder to tolerate errors in
  closing down with the HMC. The errors are logged and displayed, but the
  cleanup continues.

* Improved error handling when encountering HMC errors, by producing a proper
  error message instead of a Python traceback.

* Improved cleanup by not attempting to unsubscribe from LPARs that were
  ignored. (issue #25)

**Enhancements:**

* Added documentation (issue #9)

* Optimized the subscription for OS message notifications, by not
  subscribing for OS message notifications for LPARs when opening the
  OS message channel returns that the OS does not support it.


Version 0.1.0
^^^^^^^^^^^^^

Released: 2023-07-14

Initial PyPI release

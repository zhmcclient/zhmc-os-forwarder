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


Version 0.3.0.dev1
^^^^^^^^^^^^^^^^^^

Released: not yet

**Incompatible changes:**

* Dropped support for Python 3.5, 3.6, and 3.7. (issues #40, #74)

**Deprecations:**

**Bug fixes:**

* Addressed safety issues up to 2024-06-16.

* Test: Circumvented a pip-check-reqs issue by excluding its version 2.5.0.s

* Docs: Increased minimum Sphinx versions to 7.1.0 on Python 3.8 and to 7.2.0 on
  Python >=3.9 and adjusted dependent package versions in order to fix a version
  incompatibility between sphinxcontrib-applehelp and Sphinx.
  Disabled Sphinx runs on Python <=3.7 in order to no longer having to deal
  with older Sphinx versions. (issue #57)

* In the Github Actions test workflow for Python 3.6 and 3.7, changed
  macos-latest back to macos-12 because macos-latest got upgraded from macOS 12
  to macOS 14 which no longer supports these Python versions.

**Enhancements:**

* Added support for Python 3.12. Had to increase the minimum versions of
  setuptools to 66.1.0 and pip to 23.1.2 in order to address removal of the
  long deprecated pkgutils.ImpImporter in Python 3.12, as well as several
  packages used only for development. (issue #388)

* Test: Moved check_reqs and safety in test workflow to the end, in order to
  still run the other test steps when these two fail.

* Test: Added Python 3.8 with latest package levels to normal tests because
  that is now the minimum version to run Sphinx. (related to issue #57)

* Test: Added the option 'ignore-unpinned-requirements: False' to both
  safety policy files because for safety 3.0, the default is to ignore
  unpinned requirements (in requirements.txt).
  Increased safety minimum version to 3.0 because the new option is not
  tolerated by safety 2.x. Safety now runs only on Python >=3.7 because
  that is what safetx 3.0 requires.

* Test: Split safety runs into one against all requirements that may fail and
  one against the install requirements that must succeed. (issue #54)

* Changed safety run for install dependencies to use the exact minimum versions
  of the dependent packages, by moving them into a separate
  minimum-constraints-install.txt file that is included by the existing
  minimum-constraints.txt file. (issue #64)

* The safety run for all dependencies now must succeed when the test workflow
  is run for a release (i.e. branch name 'release_...').

**Cleanup:**

* Increased versions of GitHub Actions plugins to increase node.js runtime
  to version 20.

**Known issues:**

* See `list of open issues`_.

.. _`list of open issues`: https://github.com/zhmcclient/zhmc-os-forwarder/issues


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

* Fixed safety issues from 2023-08-27.

* Test: Circumvented a pip-check-reqs issue by excluding its version 2.5.0.

**Enhancements:**

* Added documentation (issue #9)

* Optimized the subscription for OS message notifications, by not
  subscribing for OS message notifications for LPARs when opening the
  OS message channel returns that the OS does not support it.


Version 0.1.0
^^^^^^^^^^^^^

Released: 2023-07-14

Initial PyPI release

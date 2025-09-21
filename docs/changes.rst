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

.. ============================================================================
..
.. Do not add change records here directly, but create fragment files instead!
..
.. ============================================================================

.. only:: dev

   .. include:: tmp_changes.rst

.. towncrier start
Version 1.1.0
^^^^^^^^^^^^^

Released: 2025-06-04

**Bug fixes:**

* Fixed missing package dependencies for development.

* Addressed safety issues up to 2025-06-04.

* Dev: Fixed towncrier change log check in release_branch make target.

* Dev: Added handling of HTTP error 422 when creating a new stable branch in
  the GitHub Actions publish workflow.

* Docs: Fixed supported Python versions in readme file. (`#123 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/123>`_)

**Enhancements:**

* Added check for incorrectly named towncrier change fragment files.

* Dev: Started using the trusted publisher concept of Pypi in order to avoid
  dealing with Pypi access tokens. (`#146 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/146>`_)

**Cleanup:**

* Accommodated rollout of Ubuntu 24.04 on GitHub Actions by using ubuntu-22.04
  as the OS image for Python 3.8 based test runs.


Version 1.0.0
^^^^^^^^^^^^^

Released: 2024-10-10

**Incompatible changes:**

* Changed mage name of Docker container image from 'zhmcosforwarder' to
  'zhmc_os_forwarder' to match the command name. (`#100 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/100>`_)

**Bug fixes:**

* Dev: Fixed checks and missing removal of temp file in make targets for releasing
  and starting a version.

* Dev: In the make commands to create/update AUTHORS.md, added a reftag to the
  'git shortlog' command to fix the issue that without a terminal (e.g. in GitHub
  Actions), the command did not display any authors.

* Fixed incorrect check for start branch in 'make start_tag'. (`#114 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/114>`_)

**Enhancements:**

* Dev: Automatically update AUTHORS.md when building the distribution archives.

* Migrated to pyproject.toml. (`#80 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/80>`_)

* Migrated to using towncrier for managing change logs. (`#81 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/81>`_)

* Added support for running the 'ruff' checker via "make ruff" and added that
  to the test workflow. (`#82 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/82>`_)

* Added support for running the 'bandit' checker with a new make target
  'bandit', and added that to the GitHub Actions test workflow.
  Adjusted the code in order to pass the bandit check. (`#83 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/83>`_)

* Support for and test of Python 3.13.0-rc.1. Needed to increase the minimum
  versions of PyYAML to 6.0.2 and pyrsistent to 0.20.0. (`#84 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/84>`_)

* Test: Added tests for Python 3.13 (final version). (`#85 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/85>`_)

* Dev: Encapsulated the releasing of a version to PyPI into new 'release_branch'
  and 'release_publish' make targets. See the development documentation for
  details. (`#97 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/97>`_)

* Dev: Encapsulated the starting of a new version into new 'start_branch' and
  'start_tag' make targets. See the development documentation for details. (`#97 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/97>`_)

* Improved building of the Docker container to reduce its size. (`#100 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/100>`_)

* Increased zhmcclient to 1.18.0 to pick up fixes. (`#111 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/111>`_)

**Cleanup:**

* Dev: Dropped the 'make upload' target, because the release to PyPI has
  been migrated to using a publish workflow. (`#97 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/97>`_)

* Resolved most warnings in test and publish workflows. (`#102 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/102>`_)


Version 0.3.0
^^^^^^^^^^^^^

Released: 2024-09-29

**Incompatible changes:**

* Dropped support for Python 3.5, 3.6, and 3.7. (issues #40, #74)

* Dev: Changed 'make install' to install in non-editable mode.

**Bug fixes:**

* Addressed safety issues up to 2024-08-18.

* Test: Circumvented a pip-check-reqs issue by excluding its version 2.5.0.s

* Docs: Increased minimum Sphinx versions to 7.1.0 on Python 3.8 and to 7.2.0 on
  Python >=3.9 and adjusted dependent package versions in order to fix a version
  incompatibility between sphinxcontrib-applehelp and Sphinx.
  Disabled Sphinx runs on Python <=3.7 in order to no longer having to deal
  with older Sphinx versions. (issue #57)

* In the Github Actions test workflow for Python 3.6 and 3.7, changed
  macos-latest back to macos-12 because macos-latest got upgraded from macOS 12
  to macOS 14 which no longer supports these Python versions.

* Docs: Fixed incorrect statement about port mapping in Docker container.
  (issue #30)

* Docs: Fixed incorrect link to change log.
  (issue #30)

* Test: Fixed the issue that coveralls was not found in the test workflow on MacOS
  with Python 3.9-3.11, by running it without login shell. Added Python 3.11 on
  MacOS to the normal tests.

**Enhancements:**

* Changed development status of this package to "Beta".

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
  is run for a release (i.e. branch name 'release\_...').

* Added support for a new make target 'authors' that generates an AUTHORS.md
  file from the git commit history. (issue #55)

* Increased minimum version of zhmcclient package to 1.16.1 to pick up
  fixes and enhancements.

**Cleanup:**

* Increased versions of GitHub Actions plugins to increase node.js runtime
  to version 20.

* Converted README from from RST to MarkDown to fix badge formatting.
  (issue #72)

* Dev: Relaxed the conditions when safety issues are tolerated:
  Issues in development dependencies are now tolerated in normal and scheduled
  test workflow runs (but not in local make runs and release test workflow runs).
  Issues in installation dependencies are now tolerated in normal test workflow
  runs (but not in local make runs and scheduled/release test workflow runs).

* Dev: Added to the release instructions a step to run the safety tool, and
  to roll back any fixes for safety issues into any maintained stable branches.

* Dev: Added to the release instructions to check and fix dependabot issues,
  and to roll back any fixes into any maintained stable branches.


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

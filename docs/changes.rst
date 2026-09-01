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
Version 1.2.0
^^^^^^^^^^^^^

Released: 2026-09-01

**Incompatible changes:**

* Removed support for Python 3.8, because (1) Python 3.8 is out of service since
  2024-10-07, and (2) the license definition according to PEP 639 requires
  setuptools >= 77.0.3 which requires Python >= 3.9, and pyproject.toml does
  not support environment markers. (`#219 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/219>`_)

**Bug fixes:**

* Changed from the unmaintained GitHub action gsactions/commit-message-checker
  to its new fork ddev/commit-message-checker.

* Development: Fixed that pip-missing-reqs raised TypeError by pinning pip
  to <26.2.

* Fixed safety issues up to 2026-07-10.

* Dev: Fixed issue where the package version used for distribution archive file
  names were generated inconsistently between setuptools_scm (used in Makefile)
  and the 'build' module, by using no build isolation ('--no-isolation' option
  of the 'build' module) and increasing the minimum version of 'setuptools-scm'
  to 9.2.0, which fixes a number of version related issues.

* Upgrade nltk to 3.9.1 to fix the wordnet error, see https://github.com/nltk/nltk/issues/3416

* Dev: Circumvented safety issue with import of typer module by pinning typer
  to <0.17.0.

* Development: Fixed that squash merges of the release/start PRs did not work in
  the release/start process.

* Docs: Fixed broken links in the documentation. Fixed the description of
  commit message checking in the development section of the documentation to
  remove the mentioning of the GitCop service which is no longer used.

* Removed the pinning of typer version to <0.17.0 with the new release of safety 3.6.1 and
  also upgraded minimum version of safety to be 3.6.1 to fix the issue with typer>=0.17.0, see  https://github.com/pyupio/safety/issues/778

* Dev: Added dependencies for Sphinx.

* Relaxed the commit message length check in the test workflow so
  that it no longer requires an empty line after the title and that it
  ignores the PR ID created by squash commits when checking the length.

* Docs: Updates in Bibliography section: Collapsed the HMC WS-API books to a
  single version (2.17), Added link to HMC Help, Updated HMC Security book to
  2.17, Removed the HMC Operations Guide which no longer exists.

* Docs: Removed the badges from the introduction page of the documentation
  on readthedocs.org. The badges are still in the README file on the GitHub repo.

* Test: Fixed new issues raised by pylint 4.0.0.

* Dev: Fixed the dependencies in the Makefile: Because the package is no longer
  installed in edit mode, the Python source files now needed to be added to
  the dependency list of the 'install' target. Also, 'install' is no longer
  a dependency of 'develop', because none of the targets that need 'develop'
  need the package to be installed. Added Makefile as a dependent on rules
  that produce files. (`#165 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/165>`_)

* Dev: Made order of names in AUTHORS.md reliable. (`#167 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/167>`_)

**Enhancements:**

* Test: Added check for missing and extra dependencies in minimum constraints
  files based on installed packages. The result is displayed as a warning in
  the summary of the GitHub Actions run of the "test" workflow.

* Development: Added a GitHub Actions workflow named 'backport' that creates a
  backport PR to the latest stable branch stable_M.N when a PR labeled with the
  'backport' label is merged.

* Docs: The change log of the documentation on ReadTheDocs now shows the changes
  of the next functional release in the version for the 'master' branch.

* Dev: Added checking by Mend Renovate.

* Docs: Changed the version setup on ReadTheDocs to only show released versions
  and no longer branches such as 'latest' or 'stable'. Adjusted the verification
  steps in the release instructions accordingly.

* Docs: Added sections that describe how to handle GitHub Dependabot alerts
  and how to use the assisted backporting of PRs.

* Test: Enabled tests on Python 3.14.

* Dev: Added doclinkcheck to GitHub Actions test workflow, ignoring errors. (`#161 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/161>`_)

* Dev: Added commit message checker to test workflow. (`#162 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/162>`_)

* Test: Improved some settings for coverage measurement, and enabled branch
  coverage reporting. This lowered the overall coverage percentage somewhat.
  Increased the minimum version of the "coverage" package to support the
  newer properties in the coverage config. Along with that, increased the
  minimum version of the "coveralls" package. (`#225 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/225>`_)

**Cleanup:**

* Test: Added retries for sending coverage data to the coveralls.io site to
  address issues with the site.

* Dev: Changed default shell on Windows to use bash from WSL. Removed make macros
  that encapsulated differences between Windows and Linux/macOS. Removed 'bash -c'
  from commands in the Makefile.

* Test: Reduced the GitHub Actions test environments to save resources.

* Removed unused packages from minimum constraints files.

* Removed Travis control file (was used in IBM internal fork).

* Simplified pip dependency file requirements-develop.txt by removing any indirect
  package dependencies and leaving that to the requirements of the packages
  we use directly. Reorganized the minimum-constraints-develop.txt file
  accordingly.

* Resolved several issues reported by new ruff version 4.

* Used new license format defined in PEP 639 to accommodate upcoming removal
  of support for old format. (`#216 <https://github.com/zhmcclient/zhmc-os-forwarder/issues/216>`_)


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

# Makefile for zhmc-os-forwarder project
#
# Use this to get information on the targets:
#   make  - or -  make help
#
# It is recommended to run this Makefile in a virtual Python environment,
# because Python packages will be installed automatically.
#
# Supported OS platforms:
#     Windows (native)
#     Linux (any)
#     macOS/OS-X
#
# OS-level commands used by this Makefile (to be provided manually):
#   On native Windows:
#     cmd (providing: del, copy, rmdir, set)
#     where
#   On Linux and macOS:
#     rm, find, cp, env, sort, which, uname
#
# Environment variables:
#   PYTHON_CMD: Python command to use (OS-X needs to distinguish Python 2/3)
#   PIP_CMD: Pip command to use (OS-X needs to distinguish Python 2/3)
#   PACKAGE_LEVEL: minimum/latest - Level of Python dependent packages to use

# No built-in rules needed:
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

# Python / Pip commands
ifndef PYTHON_CMD
  PYTHON_CMD := python
endif
ifndef PIP_CMD
  PIP_CMD := pip
endif

# Package level
ifndef PACKAGE_LEVEL
  PACKAGE_LEVEL := latest
endif

# Run type (normal, scheduled, release, local)
ifndef RUN_TYPE
  RUN_TYPE := local
endif

# Determine OS platform make runs on.
ifeq ($(OS),Windows_NT)
  ifdef PWD
    PLATFORM := Windows_UNIX
  else
    PLATFORM := Windows_native
    ifndef COMSPEC
      # Make variables are case sensitive and some native Windows environments have
      # ComSpec set instead of COMSPEC.
      ifdef ComSpec
        COMSPEC = $(ComSpec)
      endif
    endif
    ifdef COMSPEC
      SHELL := $(subst \,/,$(COMSPEC))
    else
      SHELL := cmd.exe
    endif
    .SHELLFLAGS := /c
  endif
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

ifeq ($(PLATFORM),Windows_native)
  # Note: The substituted backslashes must be doubled.
  # Remove files (blank-separated list of wildcard path specs)
  RM_FUNC = del /f /q $(subst /,\\,$(1))
  # Remove files recursively (single wildcard path spec)
  RM_R_FUNC = del /f /q /s $(subst /,\\,$(1))
  # Remove directories (blank-separated list of wildcard path specs)
  RMDIR_FUNC = rmdir /q /s $(subst /,\\,$(1))
  # Remove directories recursively (single wildcard path spec)
  RMDIR_R_FUNC = rmdir /q /s $(subst /,\\,$(1))
  # Copy a file, preserving the modified date
  CP_FUNC = copy /y $(subst /,\\,$(1)) $(subst /,\\,$(2))
  ENV = set
  WHICH = where
else
  RM_FUNC = rm -f $(1)
  RM_R_FUNC = find . -type f -name '$(1)' -delete
  RMDIR_FUNC = rm -rf $(1)
  RMDIR_R_FUNC = find . -type d -name '$(1)' | xargs -n 1 rm -rf
  CP_FUNC = cp -r $(1) $(2)
  ENV = env | sort
  WHICH = which -a
endif

package_name := zhmc_os_forwarder

# Package version (e.g. "1.0.0a1.dev10+gd013028e" during development, or "1.0.0"
# when releasing).
# Note: The package version is automatically calculated by setuptools_scm based
# on the most recent tag in the commit history, increasing the least significant
# version indicator by 1.
package_version := $(shell $(PYTHON_CMD) -m setuptools_scm)

docker_registry := zhmcosforwarder

python_mn_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('{}.{}'.format(sys.version_info[0], sys.version_info[1]))")
pymn := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('py{}{}'.format(sys.version_info[0], sys.version_info[1]))")

package_dir := $(package_name)

# The version file is recreated by setuptools-scm on every build, so it is
# excluded from git, and also from some dependency lists.
version_file := $(package_dir)/_version_scm.py

# Source files in the package
package_py_files := \
    $(wildcard $(package_dir)/*.py) \
    $(wildcard $(package_dir)/*/*.py) \

test_dir := tests
test_py_files := \
    $(wildcard $(test_dir)/*.py) \
    $(wildcard $(test_dir)/*/*.py) \

dist_dir := dist
bdist_file := $(dist_dir)/$(package_name)-$(package_version)-py2.py3-none-any.whl
sdist_file := $(dist_dir)/$(package_name)-$(package_version).tar.gz

# Dependencies of the distribution archives. Since the $(version_file) is
# created when building the distribution archives, this must not contain
# the $(version_file).
dist_dependent_files := \
    pyproject.toml \
    LICENSE \
    README.md \
    requirements.txt \
    $(package_py_files) \

doc_dir := docs
doc_build_dir := build_docs
doc_build_file := $(doc_build_dir)/index.html
doc_dependent_files := \
    $(wildcard $(doc_dir)/*.*) \
		$(wildcard $(doc_dir)/*/*.*) \
		examples/config_example.yaml \
    $(package_py_files) \

# Source files for checks (with PyLint and Flake8, etc.)
check_py_files := \
    $(filter-out $(version_file), $(package_py_files)) \
    $(test_py_files) \
    $(doc_dir)/conf.py \

# Directory for .done files
done_dir := done

# Packages whose dependencies are checked using pip-missing-reqs
check_reqs_packages := pip_check_reqs pipdeptree build pytest coverage coveralls flake8 ruff pylint twine safety bandit sphinx towncrier

# Safety policy file
safety_install_policy_file := .safety-policy-install.yml
safety_develop_policy_file := .safety-policy-develop.yml

# Bandit config file
bandit_rc_file := .bandit.toml

# Flake8 config file
flake8_rc_file := .flake8

# Ruff config file
ruff_rc_file := .ruff.toml

# PyLint config file
pylint_rc_file := .pylintrc

pytest_cov_opts := --cov $(package_name) --cov-config .coveragerc --cov-report=html:htmlcov

ifeq ($(PACKAGE_LEVEL),minimum)
  pip_level_opts := -c minimum-constraints-develop.txt -c minimum-constraints-install.txt
else
  ifeq ($(PACKAGE_LEVEL),latest)
    pip_level_opts := --upgrade --upgrade-strategy eager
  else
    $(error Invalid value for PACKAGE_LEVEL variable: $(PACKAGE_LEVEL))
  endif
endif

.PHONY: help
help:
	@echo "Makefile for project $(package_name)"
	@echo "Package version: $(package_version)"
	@echo "Python version: $(python_mn_version)"
	@echo "Targets:"
	@echo "  install    - Install package and its prerequisites (non-editable)"
	@echo "  develop    - Install prerequisites for development"
	@echo "  check_reqs - Perform missing dependency checks"
	@echo "  check      - Perform flake8 checks"
	@echo "  ruff       - Perform ruff checks (an alternate lint tool)"
	@echo "  pylint     - Perform pylint checks"
	@echo "  safety     - Run safety checker"
	@echo "  bandit     - Run bandit checker"
	@echo "  test       - Perform unit tests including coverage checker"
	@echo "  build      - Build the distribution files in $(dist_dir)"
	@echo "  builddoc   - Build the documentation in $(doc_build_dir)"
	@echo "  all        - Do all of the above"
	@echo "  docker     - Build local Docker image in registry $(docker_registry)"
	@echo "  authors    - Generate AUTHORS.md file from git log"
	@echo "  upload     - Upload the package to Pypi"
	@echo "  clean      - Remove any temporary files"
	@echo "  clobber    - Remove any build products"
	@echo "  platform   - Display the information about the platform as seen by make"
	@echo "  env        - Display the environment as seen by make"
	@echo 'Environment variables:'
	@echo "  PACKAGE_LEVEL - Package level to be used for installing dependent Python"
	@echo "      packages in 'install' and 'develop' targets:"
	@echo "        latest - Latest package versions available on Pypi"
	@echo "        minimum - A minimum version as defined in minimum-constraints-develop.txt"
	@echo "      Optional, defaults to 'latest'."
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'

.PHONY: platform
platform:
	@echo "Makefile: Platform information as seen by make:"
	@echo "Platform: $(PLATFORM)"
	@echo "Shell used for commands: $(SHELL)"
	@echo "Shell flags: $(.SHELLFLAGS)"
	@echo "Make version: $(MAKE_VERSION)"
	@echo "Python command name: $(PYTHON_CMD)"
	@echo "Python command location: $(shell $(WHICH) $(PYTHON_CMD))"
	@echo "Python version: $(python_mn_version)"
	@echo "Pip command name: $(PIP_CMD)"
	@echo "Pip command location: $(shell $(WHICH) $(PIP_CMD))"
	@echo "Pip version: $(shell $(PIP_CMD) --version)"
	@echo "$(package_name) package version: $(package_version)"

.PHONY: env
env:
	@echo "Makefile: Environment variables as seen by make:"
	$(ENV)

.PHONY: _check_version
_check_version:
ifeq (,$(package_version))
	$(error Package version could not be determined)
endif

.PHONY: install
install: $(done_dir)/install_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: develop
develop: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: check
check: $(done_dir)/flake8_$(pymn)_$(PACKAGE_LEVEL).done
	@echo '$@ done.'

.PHONY: ruff
ruff: $(done_dir)/ruff_$(pymn)_$(PACKAGE_LEVEL).done
	@echo '$@ done.'

.PHONY: pylint
pylint: $(done_dir)/pylint_$(pymn)_$(PACKAGE_LEVEL).done
	@echo '$@ done.'

.PHONY: safety
safety: $(done_dir)/safety_develop_$(pymn)_$(PACKAGE_LEVEL).done $(done_dir)/safety_install_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: bandit
bandit: $(done_dir)/bandit_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: check_reqs
check_reqs: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done minimum-constraints-develop.txt minimum-constraints-install.txt requirements.txt
	@echo "Makefile: Checking missing dependencies of this package"
	pip-missing-reqs $(package_name) --requirements-file=requirements.txt
	pip-missing-reqs $(package_name) --requirements-file=minimum-constraints-install.txt
	@echo "Makefile: Done checking missing dependencies of this package"
ifeq ($(PLATFORM),Windows_native)
# Reason for skipping on Windows is https://github.com/r1chardj0n3s/pip-check-reqs/issues/67
	@echo "Makefile: Warning: Skipping the checking of missing dependencies of site-packages directory on native Windows" >&2
else
	@echo "Makefile: Checking missing dependencies of some development packages in our minimum versions"
	bash -c "cat minimum-constraints-develop.txt minimum-constraints-install.txt >tmp_minimum-constraints-all.txt"
	@rc=0; for pkg in $(check_reqs_packages); do dir=$$($(PYTHON_CMD) -c "import $${pkg} as m,os; dm=os.path.dirname(m.__file__); d=dm if not dm.endswith('site-packages') else m.__file__; print(d)"); cmd="pip-missing-reqs $${dir} --requirements-file=tmp_minimum-constraints-all.txt"; echo $${cmd}; $${cmd}; rc=$$(expr $${rc} + $${?}); done; exit $${rc}
	-$(call RM_FUNC,tmp_minimum-constraints-all.txt)
	@echo "Makefile: Done checking missing dependencies of some development packages in our minimum versions"
endif
	@echo "Makefile: $@ done."

.PHONY: test
test: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: Performing unit tests and coverage with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	pytest $(pytest_cov_opts) -s $(test_dir)
	@echo "Makefile: Done performing unit tests and coverage"
	@echo "Makefile: $@ done."

.PHONY: build
build: _check_version $(bdist_file) $(sdist_file)
	@echo "Makefile: $@ done."

.PHONY: builddoc
builddoc: _check_version $(doc_build_file)
	@echo "Makefile: $@ done."

.PHONY: all
all: install develop check_reqs check pylint test build builddoc check_reqs
	@echo "Makefile: $@ done."

.PHONY: docker
docker: _check_version $(done_dir)/docker_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: authors
authors: _check_version
	echo "# Authors of this project" >AUTHORS.md
	echo "" >>AUTHORS.md
	echo "Sorted list of authors derived from git commit history:" >>AUTHORS.md
	echo '```' >>AUTHORS.md
	git shortlog --summary --email | cut -f 2 | sort >>AUTHORS.md
	echo '```' >>AUTHORS.md
	@echo '$@ done.'

.PHONY: upload
upload: _check_version $(bdist_file) $(sdist_file)
ifeq (,$(findstring .dev,$(package_version)))
	@echo "==> This will upload $(package_name) version $(package_version) to PyPI!"
	@echo -n "==> Continue? [yN] "
	@bash -c 'read answer; if [ "$$answer" != "y" ]; then echo "Aborted."; false; fi'
	twine upload $(bdist_file) $(sdist_file)
	@echo "Makefile: Done: Uploaded $(package_name) version to PyPI: $(package_version)"
else
	@echo "Error: A development version $(package_version) of $(package_name) cannot be uploaded to PyPI!"
	@false
endif

.PHONY: clean
clean:
	-$(call RM_R_FUNC,*.pyc)
	-$(call RM_R_FUNC,*.tmp)
	-$(call RM_R_FUNC,tmp_*)
	-$(call RM_FUNC,.coverage MANIFEST MANIFEST.in AUTHORS ChangeLog)
	-$(call RMDIR_R_FUNC,__pycache__)
	-$(call RMDIR_FUNC,build $(package_name).egg-info .pytest_cache)
	@echo "Makefile: $@ done."

.PHONY: clobber
clobber: clean
	-$(call RMDIR_FUNC,$(doc_build_dir) htmlcov)
	-$(call RM_R_FUNC,*.done)
	@echo "Makefile: $@ done."

$(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done: minimum-constraints-develop.txt minimum-constraints-install.txt requirements-base.txt
	@echo "Makefile: Installing base packages with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	-$(call RM_FUNC,$@)
	$(PYTHON_CMD) -m pip install $(pip_level_opts) -r requirements-base.txt
	@echo "Makefile: Done installing base packages"
	echo "done" >$@

$(done_dir)/install_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done requirements.txt minimum-constraints-develop.txt minimum-constraints-install.txt pyproject.toml
	@echo "Makefile: Installing package (non-editable) and its prerequisites with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	-$(call RM_FUNC,$@)
	$(PYTHON_CMD) -m pip install $(pip_level_opts) .
	@echo "Makefile: Done installing package and its prerequisites"
	echo "done" >$@

$(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/install_$(pymn)_$(PACKAGE_LEVEL).done requirements-develop.txt minimum-constraints-develop.txt minimum-constraints-install.txt
	@echo "Makefile: Installing prerequisites for development with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	-$(call RM_FUNC,$@)
	$(PYTHON_CMD) -m pip install $(pip_level_opts) -r requirements-develop.txt
	@echo "Makefile: Done installing prerequisites for development"
	echo "done" >$@

$(doc_build_file): $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(doc_dependent_files)
	@echo "Makefile: Generating HTML documentation with main file: $@"
	sphinx-build -b html -v $(doc_dir) $(doc_build_dir)
	@echo "Makefile: Done generating HTML documentation"

$(sdist_file): $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done Makefile $(dist_dependent_files)
	@echo "Makefile: Building the source distribution archive: $(sdist_file)"
	$(PYTHON_CMD) -m build --sdist --outdir $(dist_dir) .
	@echo "Makefile: Done building the source distribution archive: $(sdist_file)"

$(bdist_file) $(version_file): $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done Makefile $(dist_dependent_files)
	@echo "Makefile: Building the wheel distribution archive: $(bdist_file)"
	$(PYTHON_CMD) -m build --wheel --outdir $(dist_dir) -C--universal .
	@echo "Makefile: Done building the wheel distribution archive: $(bdist_file)"

$(done_dir)/flake8_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(flake8_rc_file) $(check_py_files)
	@echo "Makefile: Performing flake8 checks with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	flake8 --config $(flake8_rc_file) $(check_py_files)
	echo "done" >$@
	@echo "Makefile: Done performing flake8 checks"

$(done_dir)/ruff_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(ruff_rc_file) $(check_py_files)
	@echo "Makefile: Performing ruff checks with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	-$(call RM_FUNC,$@)
	ruff check --unsafe-fixes --config $(ruff_rc_file) $(check_py_files)
	echo "done" >$@
	@echo "Makefile: Done performing ruff checks"

$(done_dir)/pylint_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(pylint_rc_file) $(check_py_files)
	@echo "Makefile: Performing pylint checks with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	pylint --rcfile=$(pylint_rc_file) --disable=fixme $(check_py_files)
	echo "done" >$@
	@echo "Makefile: Done performing pylint checks"

$(done_dir)/safety_develop_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done Makefile $(safety_develop_policy_file) minimum-constraints-develop.txt
	@echo "Makefile: Running Safety for development packages (and tolerate safety issues when RUN_TYPE is normal or scheduled)"
	-$(call RM_FUNC,$@)
	bash -c "safety check --policy-file $(safety_develop_policy_file) -r minimum-constraints-develop.txt --full-report || test '$(RUN_TYPE)' == 'normal' || test '$(RUN_TYPE)' == 'scheduled' || exit 1"
	echo "done" >$@
	@echo "Makefile: Done running Safety for development packages"

$(done_dir)/safety_install_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done Makefile $(safety_install_policy_file) minimum-constraints-install.txt
	@echo "Makefile: Running Safety for install packages (and tolerate safety issues when RUN_TYPE is normal)"
	-$(call RM_FUNC,$@)
	bash -c "safety check --policy-file $(safety_install_policy_file) -r minimum-constraints-install.txt --full-report || test '$(RUN_TYPE)' == 'normal' || exit 1"
	echo "done" >$@
	@echo "Makefile: Done running Safety for install packages"

$(done_dir)/bandit_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(bandit_rc_file) $(check_py_files)
	@echo "Makefile: Running Bandit"
	-$(call RM_FUNC,$@)
	bandit -c $(bandit_rc_file) -l $(check_py_files)
	echo "done" >$@
	@echo "Makefile: Done running Bandit"

$(done_dir)/docker_$(pymn)_$(PACKAGE_LEVEL).done: $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done Dockerfile .dockerignore Makefile $(dist_dependent_files)
	@echo "Makefile: Building Docker image $(docker_registry):latest"
	-$(call RM_FUNC,$@)
	docker build -t $(docker_registry):latest .
	@echo "Makefile: Done building Docker image"
	echo "done" >$@

# IBM Z HMC OS Message Forwarder

[![Version on Pypi](https://img.shields.io/pypi/v/zhmc-os-forwarder.svg)](https://pypi.python.org/pypi/zhmc-os-forwarder/)
[![Test status (master)](https://github.com/zhmcclient/zhmc-os-forwarder/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-os-forwarder/actions/workflows/test.yml?query=branch%3Amaster)
[![Docs status (master)](https://readthedocs.org/projects/zhmc-os-forwarder/badge/?version=latest)](https://readthedocs.org/projects/zhmc-os-forwarder/builds/)
[![Test coverage (master)](https://coveralls.io/repos/github/zhmcclient/zhmc-os-forwarder/badge.svg?branch=master)](https://coveralls.io/github/zhmcclient/zhmc-os-forwarder?branch=master)

The **IBM Z HMC OS Message Forwarder** connects to the console of
operating systems running in LPARs on Z systems and forwards the
messages written by the operating systems in the LPARs to remote syslog
servers.

The Z systems can be in classic or DPM operational mode.

The forwarder attempts to stay up as much as possible, for example it
performs automatic session renewals with the HMC if the logon session
expires, and it survives HMC reboots and automatically resumes
forwarding again once the HMC come back up, without loosing or
duplicating any messages.

# Documentation

- [Documentation](https://zhmc-os-forwarder.readthedocs.io/en/stable/)
- [Change log](https://zhmc-os-forwarder.readthedocs.io/en/stable/changes.html)

# Supported environments

- Operating systems: Linux, macOS, Windows
- Python versions: 3.9 and higher
- HMC versions: 2.11.1 and higher

# Quickstart

- If not yet available, install the "pipx" command as described in
  https://pipx.pypa.io/stable/installation/.

- Without having any virtual Python environment active, install the log
  forwarder as follows:

  ``` bash
  $ pipx install zhmc-os-forwarder
  ```

  That makes the `zhmc_os_forwarder` command available in the PATH, without
  having to activate any virtual Python environment.

- Provide a *config file* for use by the forwarder.

  The config file tells the forwarder which HMC to use, and for which
  CPCs and LPARs it should forward to which syslog servers.

  Download the
  [Example forwarder config file](examples/config_example.yaml) and edit that
  copy according to your needs.

  For details, see
  [Forwarder config file](https://zhmc-os-forwarder.readthedocs.io/en/stable/usage.html#forwarder-config-file).

- Run the forwarder as follows:

  ``` bash
  $ zhmc_os_forwarder -c config.yaml
  zhmc_os_forwarder version: 0.2.0
  zhmcclient version: 1.10.0
  Verbosity level: 0
  Opening session with HMC 10.11.12.13 (user: johndoe@us.ibm.com, certificate validation: False)
  Forwarder is up and running (Press Ctrl-C to shut down)
  ```

# Limitations

At this point, the forwarder has several limitations. All of them are
intended to be resolved in future releases.

- The forwarder does not recover from HMC restart or connection loss
- Restarting the forwarder will send again all OS messages the HMC has
  buffered
- New and deleted LPARs in DPM mode are not automatically detected.

# Reporting issues

If you encounter a problem, please report it as an
[issue on GitHub](https://github.com/zhmcclient/zhmc-os-forwarder/issues).

# License

This package is licensed under the
[Apache 2.0 License](http://apache.org/licenses/LICENSE-2.0).

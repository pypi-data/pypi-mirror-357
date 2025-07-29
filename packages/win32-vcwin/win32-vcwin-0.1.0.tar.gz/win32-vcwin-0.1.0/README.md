# win32-vcwin — CLI tool for managing VC++ Tools, Windows SDK, WDK, and DirectX SDK

[![PyPI version](https://badge.fury.io/py/win32-vcwin.svg)](https://pypi.org/project/win32-vcwin/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**win32-vcwin** is a command-line tool for Windows developers to inspect, install, uninstall, and manage components such as Visual C++ Tools, Windows SDK, WDK, and DirectX SDK.

## Features

- 🔍 Search for installed and available packages
- 📦 Install and uninstall WDK, Windows SDK, DXSDK
- 📋 Get detailed information about installed components
- 🧾 Output in either YAML or JSON format
- ⚙️ Automate setup for development environments

## Installation

Install `win32-vcwin` via pip:

```bash
pip install win32-vcwin
```
⚠ Requires Windows and Python 3.6+


## Available commands

| Command                                                         | Description                               |
| --------------------------------------------------------------- | ----------------------------------------- |
| `state`                                                         | Show installed SDKs and tools             |
| `install <package> <version>`                                   | Install a package (`sdk`, `wdk`, `dxsdk`) |
| `uninstall/remove <package> <version> [--full] [--show-string]` | Uninstall a package                       |
| `search [name] [version]`                                       | Search for available packages             |
| `list <package>`                                                | List installed versions of WDK or SDK     |
| `get <name>`                                                    | Get detailed info about `sdk` or `wdk`    |


## Output Format

By default, output is in YAML. For JSON output, use:

```bash
vcwin state --format json
```

## Example Usage

```bash
vcwin state
```

Shows installed versions of:
- Visual C++ Tools
- Windows SDK
- DirectX SDK

Search for all available packages (dxsdk, windows sdk, wdk):
```bash
vcwin search
```

Search for available SDK versions (you can search for 'sdk', 'wdk', 'dxsdk'):
```bash
vcwin search sdk
```

Downloads and installs the specified version of Windows Driver Kit:
```bash
vcwin install wdk 10.1.22621.2428
```

Fully uninstalls WDK and all its components:
```bash
vcwin uninstall wdk 10.1.22621.2428 --full
```
The --full flag ensures that all WDK uninstall components are removed.
For WDK, it also removes any WDK-related files or configuration from the associated Windows SDK of the same version.
The --full flag only matters when deleting wdk

You can also use the --show-string flag to just see what registry uninstall command would be used to remove a wdk package (not sdk related), but without actually removing the package. (wdk only, do not combine this flag with --full or sdk related packages will be removed):
```bash
vcwin uninstall wdk 10.1.22621.2428 --show-string
```

List all installed windows sdk:
```bash
vcwin list sdk
```

Install dxsdk:
```bash
vcwin install dxsdk 9.29.1962.0
```

Uninstall dxsdk:
```bash
vcwin uninstall dxsdk 9.29.1962.0
```

You can export the current state of all packages in JSON format using the following command:
```bash
vcwin state --format json > state.json
```

This will save the package state information to the state.json file for further analysis or use in other tools.

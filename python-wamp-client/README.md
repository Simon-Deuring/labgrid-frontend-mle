# WAMP Server written in Python for the Labgrid project

## Usage

To start the python backend router run following command in this directory.

```sh
> python run.py [-h] [--url URL] [--realm REALM]
```

The port of the crossbar router is `8083` and can be changed in the [config](./labby/router/.crossbar/config.json).

To establish a connection to the labgrid coordinator it might be required to use ssh-port-forwarding (`ssh -L`).

The currently implemented RPC endpoints can be found in the [API-Definition](./doc/wamp_api.md). The returned resources and places are identical to those defined in the [labgrid-doc](https://labgrid.readthedocs.io/en/latest/configuration.html#resources).

We advice the use of a virtual python environment, like conda, virtualenv or pipenv to handle the Python Interpreter and requirements.

## Requirements

* Python >= 3.7
  * Modules: Autobahn, Crossbar

### Windows

* Additionally Crossbar requires [Pywin32](https://crossbar.io/docs/Installation-on-Windows/#installing-the-dependencies) on Windows

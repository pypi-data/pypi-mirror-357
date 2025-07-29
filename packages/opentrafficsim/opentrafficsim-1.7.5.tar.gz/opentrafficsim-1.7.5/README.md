# opentrafficsim

This package provides opentrafficsim (OTS) so that it can be integrated into python porjects.

## Installation

Install from PyPi:
```
$ pip install opentrafficsim
```

> Note: You cannot use this package as a git dependency, because OTS must be built before packaging and poetry is currently not able to do this.

## Usage

The following code, will make OTS available to your python program:

```python3
import opentrafficsim
```

This will populate the `OTS_HOME` and `OTS_VERSION` environment variables accordingly. `OTS_HOME` follows the layout of the opentrafficsim repo. So you will find the distribution JAR under `$OTS_HOME/ots-distribution/target/ots-distribution-$OTS_VERSION.jar`.

## Update

1. Update the git submodule to the new version
2. Install dev dependencies: `poetry install --with dev`
3. Bump to new version `poetry run bump-my-version <patch|minior|major` (choose the appropriate version upgrade)
4. push to repo and publish through pipeline

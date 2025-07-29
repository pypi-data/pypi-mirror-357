import os
from pathlib import Path

OTS_VERSION = "1.7.5"

if "OTS_HOME" not in os.environ:
    ots_home_path = Path(__file__).parent
    os.environ["OTS_HOME"] = str(ots_home_path.absolute())
    os.environ["OTS_VERSION"] = OTS_VERSION

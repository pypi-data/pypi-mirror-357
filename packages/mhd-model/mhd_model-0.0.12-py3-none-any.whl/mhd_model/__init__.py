import pathlib
import sys

__version__ = "v0.0.12"

application_root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(application_root_path))

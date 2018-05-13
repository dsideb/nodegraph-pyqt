import sys as _sys
import os as _os

# Add third party as top level modules
_sys.path.append(_os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.realpath(__file__))),
    "thirdparty"))

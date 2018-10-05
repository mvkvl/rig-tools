
# include libraries
import os,sys
sys.path.insert(0, "{}/../lib/".format(os.path.dirname(__file__)))
sys.path.insert(0, "{}/../lib/crypto".format(os.path.dirname(__file__)))
sys.path.insert(0, "{}/../lib/poolapi".format(os.path.dirname(__file__)))
sys.path.insert(0, "{}/../lib/minerapi".format(os.path.dirname(__file__)))

# enable JSON serialization for own classes
from json import JSONEncoder
def _default(self, obj):
    return getattr(obj.__class__, "toJSON", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default

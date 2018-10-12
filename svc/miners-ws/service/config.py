import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,"{}//lib".format(currentdir))

class Config(object):
    ENV      = os.environ.get('FLASK_ENV')       or "development"
    DATA_DIR = os.environ.get('MINERS_DATA_DIR') or "/Users/kami/work/dev/mine.2/miners-ws/var-run" # "/var/run/miner"
    PORT     = os.environ.get('MINERS_WS_PORT')  or "5000"
    LOGGING  = os.environ.get('LOG_LEVEL')       or "DEBUG"

from flask import Flask
from config import Config
import logger
import signal
import os

app = Flask(__name__)
app.config.from_object(Config)

from flask.logging import default_handler
app.logger.removeHandler(default_handler)

from app import routes

logger   = logger.instance(__name__, os.environ.get('LOG_APP_MAIN', app.config['LOGGING']))

def cleanup(signum, frame):
    logger.info("stop web service")
    exit(0)

def startup():
    logger.info("start web service")


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

startup()

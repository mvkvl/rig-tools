from app import app
from flask import request
from flask import jsonify
import os, json
import logger

logger = logger.instance(__name__, os.environ.get('LOG_LEVEL', app.config['LOGGING']))

def get_active_miners():
    miners = []
    for f in os.listdir(app.config['DATA_DIR']):
        with open(os.path.join(app.config['DATA_DIR'], f)) as miner_config:
            mc = json.load(miner_config)
            miners.append(mc)
    return miners

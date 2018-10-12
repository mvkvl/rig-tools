from app import app
from flask import request
from flask import jsonify
import os
import logger, tools

logger  = logger.instance(__name__, os.environ.get('LOG_APP_ROUTES', app.config['LOGGING']))

# =========================================================
#  R O U T E   H A N D L E R S
#
# ---------------------------------------------------------
#  index page
@app.route('/')
@app.route('/index')
def index():
    return jsonify(tools.get_active_miners())
# ---------------------------------------------------------

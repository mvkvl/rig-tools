import logging

levelMap = {
    'DEBUG'    : logging.DEBUG,
    'INFO'     : logging.INFO,
    'WARNING'  : logging.DEBUG,
    'WARN'     : logging.WARNING,
    'ERROR'    : logging.ERROR,
    'ERR'      : logging.ERROR,
    'CRITICAL' : logging.CRITICAL,
    'CRIT'     : logging.CRITICAL
}

def instance(name, levelName):
    level = levelMap.get(levelName, 'DEBUG')
    mylogger = logging.getLogger(name.upper().replace("_", ""))
    mylogger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('[%(name)s - %(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    mylogger.addHandler(ch)
    return mylogger

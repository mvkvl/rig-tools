import logging

def instance(name, levelName):
    level = logging.getLevelName(levelName)
    logging.basicConfig(format='%(asctime)19s %(name)-11s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger(name)
    log.setLevel(level)
    return log

    # level = logging.getLevelName(levelName) # levelMap.get(levelName, 'DEBUG')
    # mylogger = logging.getLogger(name.lower().replace("_", ""))
    # mylogger.setLevel(level)
    # ch = logging.StreamHandler()
    # ch.setLevel(level)
    # formatter = logging.Formatter('%(asctime)19s %(name)-10s %(levelname)s %(message)s',
    #                               "%Y-%m-%d %H:%M:%S")
    # ch.setFormatter(formatter)
    # mylogger.addHandler(ch)
    # return mylogger

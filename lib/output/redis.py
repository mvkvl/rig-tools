# import redis
import json, time
import logger

# def __connect_influx(conf):
#     return InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    # pass

def __write_data(conf, data, module="", loglevel="ERROR"):
    # client = __connect_influx(conf)
    # client.switch_database(conf["database"])
    #
    # log = logger.instance(module, loglevel)
    #
    # for i in range (MAX_WRITE_ATTEMPTS):
    #     try:
    #         if client.write_points(data):
    #             log.info("InfluxDB write OK")
    #             break
    #         else:
    #             log.warning("Can't write to InfluxDB")
    #         time.sleep(i+1)
    #     except Exception as ex:
    #         s = str(ex).replace("b'","").replace("\\n'","") #.replace("'","\"")
    #         err = json.loads(s).get("error")
    #         log.error("InfluxDB write error - {}".format(err))
    # client.close()
    pass

def prepare_wallet_balance_data(data, conf, metric=None):
    result = []
    for c in data:
        for k in data.get(c):
            result.append({"{}.{}.{}".format(metric, c, k): data.get(c).get(k)})
    return result
def prepare_pool_balance_data(data, conf, metric=None):
    result = []
    for p in data:
        for c in data.get(p):
            for k in data.get(p).get(c):
                result.append({"{}.{}.{}.{}".format(metric, p, c, k): data.get(p).get(c).get(k)})
    return result
def prepare_pool_stats_data(data, conf, metric=None):
    result = []
    for p in data:
        for c in data.get(p):
            for w in data.get(p).get(c).get("workers"):
                result.append({"{}.{}.{}.{}.hashrate".format(metric, p, c, w): data.get(p).get(c).get("workers").get(w).hashrate()})
                result.append({"{}.{}.{}.{}.average".format(metric, p, c, w): data.get(p).get(c).get("workers").get(w).average()})
    return result
def prepare_worker_stats_data(data, conf, metric=None):
    # result = []
    # for p in data:
    #     for c in data.get(p):
    #         for w in data.get(p).get(c).get("workers"):
    #             result.append({"{}.{}.{}.{}.hashrate".format(metric, p, c, w): data.get(p).get(c).get("workers").get(w).hashrate()})
    #             result.append({"{}.{}.{}.{}.average".format(metric, p, c, w): data.get(p).get(c).get("workers").get(w).average()})
    # return result
    return data

def save_wallet_balance(data, conf, loglevel="ERROR", module="", metric=None):
    # print (json.dumps(prepare_wallet_balance_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_wallet_balance_data(data, conf, metric), module=module, loglevel=loglevel)
def save_pool_balance(data, conf, loglevel="ERROR", module="", metric=None):
    # print (json.dumps(prepare_pool_balance_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_pool_balance_data(data, conf, metric), module=module, loglevel=loglevel)
def save_pool_stats(data, conf, loglevel="ERROR", module="", metric=None):
    # print (json.dumps(prepare_pool_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_pool_stats_data(data, conf, metric), module=module, loglevel=loglevel)
def save_worker_stats(data, conf, loglevel="ERROR", module="", metric=None):
    print (json.dumps(prepare_worker_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    # __write_data(conf, prepare_worker_stats_dataprepare_worker_stats_data(data, conf, metric), module=module, loglevel=loglevel)

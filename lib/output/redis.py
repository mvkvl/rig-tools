import redis
import json, time
import logger

# def __connect_influx(conf):
#     return InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    # pass

def __write_data(conf, data, module="", loglevel="ERROR"):
    # print (json.dumps(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': '))
    r = redis.Redis(host=conf["host"], port=conf["port"])
    for i in data:
        for k in i:
            r.set(k, i.get(k))
            print ("{} -> {}".format(k, i.get(k)))

    r.close()

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
    result = []
    for r in data:
        for w in data.get(r):
            result.append({"{}.{}.power:{}".format(metric, w, r): float(data.get(r).get(w).get("power"))})
            result.append({"{}.{}.hashrate:{}".format(metric, w, r): data.get(r).get(w).get("hashrate")})
            result.append({"{}.{}.efficiency:{}".format(metric, w, r): data.get(r).get(w).get("efficiency")})
    return result
def prepare_gpu_stats_data(data, conf, metric=None):
    result = []
    for r in data:
        rig_total_power = 0.0
        for w in data[r]:
            for g in data[r][w]['gpu']:
                rig_total_power = float(g.get("power"))
                result.append({"{}.{}.power:{}".format(metric, g["id"], r): float(g.get("power"))})
                result.append({"{}.{}.hashrate:{}".format(metric, g["id"], r): float(g.get("hashrate"))})
                result.append({"{}.{}.efficiency:{}".format(metric, g["id"], r): float(g.get("efficiency"))})
                result.append({"{}.{}.temperature:{}".format(metric, g["id"], r): float(g.get("temperature"))})
        if rig_total_power > 0:
            result.append({"{}.{}.power:{}".format(metric, "total", r): float(rig_total_power)})
    return result
def prepare_pool_worker_stats_data(data, conf, metric=None):
    result = []
    for r in data:
        for w in data.get(r):
            c = data.get(r).get(w).get("crypto")
            p = data.get(r).get(w).get("pool").get("name")
            h = float(data.get(r).get(w).get("pool").get("hashrate"))
            a = float(data.get(r).get(w).get("pool").get("average"))
            result.append({"{}.{}.{}.{}.hashrate".format(metric, p, c, w): h})
            result.append({"{}.{}.{}.{}.average".format(metric, p, c, w) : a})
    return result

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
    # print (json.dumps(prepare_worker_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_worker_stats_data(data, conf, metric), module=module, loglevel=loglevel)
def save_gpu_stats(data, conf, loglevel="ERROR", module="", metric=None):
    print (json.dumps(prepare_gpu_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    # __write_data(conf, prepare_gpu_stats_data(data, conf, metric), module=module, loglevel=loglevel)
def save_pool_worker_stats(data, conf, loglevel="ERROR", module="", metric=None):
    # print (json.dumps(prepare_pool_worker_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_pool_worker_stats_data(data, conf, metric), module=module, loglevel=loglevel)


def prepare_traffic_stats_data(data, conf, metric=None):
    result = []
    for h in data:
        for i in data[h]:
            m = "{}.{}.{}".format(metric, h, i)
            result.append({"{}.in".format(m): float(data[h][i]['rx'])})
            result.append({"{}.out".format(m): float(data[h][i]['tx'])})
    return result

def save_traffic_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_traffic_stats_data(data, conf, metric), module=module, loglevel=loglevel)

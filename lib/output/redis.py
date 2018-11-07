import redis
import json, time
import logger

def writeData(conf, data):
    r = redis.Redis(host=conf["host"], port=conf["port"])
    for d in data:
        r.set(d['key'], d['value'])


def __write_data(conf, data, module="", loglevel="ERROR"):
    # print (json.dumps(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': '))
    r = redis.Redis(host=conf["host"], port=conf["port"])
    for i in data:
        for k in i:
            r.set(k, i.get(k))
            # print ("{} -> {}".format(k, i.get(k)))

def prepare_wallet_balance_data(data, conf, metric=None):
    result = []
    for c in data:
        for k in data.get(c):
            result.append({"{}.{}:{}".format(metric, k, c): data.get(c).get(k)})
    return result
def prepare_pool_balance_data(data, conf, metric=None):
    result = []
    for p in data:
        for c in data.get(p):
            for k in data.get(p).get(c):
                result.append({"{}.{}:{}.{}".format(metric, k, p, c): data.get(p).get(c).get(k)})
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
            result.append({"{}.power:{}.{}".format(metric, r, w): float(data.get(r).get(w).get("power"))})
            result.append({"{}.hashrate:{}.{}".format(metric, r, w): data.get(r).get(w).get("hashrate")})
            result.append({"{}.efficiency:{}.{}".format(metric, r, w): data.get(r).get(w).get("efficiency")})
    return result
def prepare_gpu_stats_data(data, conf, metric=None):
    result = []
    for r in data:
        rig_total_power = 0.0
        for w in data[r]:
            for g in data[r][w]['gpu']:
                rig_total_power += float(g.get("power"))
                result.append({"{}.power:{}.{}".format(metric, r, g["id"]): float(g.get("power"))})
                result.append({"{}.hashrate:{}.{}".format(metric, r, g["id"]): float(g.get("hashrate"))})
                result.append({"{}.efficiency:{}.{}".format(metric, r, g["id"]): float(g.get("efficiency"))})
                result.append({"{}.temperature:{}.{}".format(metric, r, g["id"]): float(g.get("temperature"))})
        if rig_total_power > 0:
            result.append({"{}.power:{}.{}".format(metric, r, "total"): float(rig_total_power)})
    return result
def prepare_pool_worker_stats_data(data, conf, metric=None):
    result = []
    for r in data:
        for w in data.get(r):
            c = data.get(r).get(w).get("crypto")
            p = data.get(r).get(w).get("pool").get("name")
            h = float(data.get(r).get(w).get("pool").get("hashrate"))
            a = float(data.get(r).get(w).get("pool").get("average"))
            result.append({"{}.hashrate:{}.{}.{}".format(metric, p, c, w): h})
            # result.append({"{}.average:{}.{}.{}".format(metric, p, c, w) : a})
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
    # print (json.dumps(prepare_gpu_stats_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_gpu_stats_data(data, conf, metric), module=module, loglevel=loglevel)
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

def save_crypto_price(data, conf, metric=None, module=None, loglevel="ERROR"):
    pass
def save_blockchain_info(data, conf, metric=None, module=None, loglevel="ERROR"):
    pass
def save_power_value(data, conf, metric=None, module=None, loglevel="ERROR"):
    pass

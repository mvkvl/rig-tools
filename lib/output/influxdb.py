from influxdb import InfluxDBClient
import json

# creates data array to save to influxdb
def prepare_wallet_balance_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, crypto):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "crypto": crypto,
                },
                "fields": {
                }
               }
        return res
    result = []
    m = metric or conf.get("metric")
    for c in data:
        point = make_data_point(m, c)
        for w in data.get(c):
            point["fields"][w] = data.get(c).get(w)
        result.append(point)
    return result

# creates data array to save to influxdb
def prepare_pool_balance_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, pool, crypto):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "crypto": crypto,
                    "pool": pool,
                },
                "fields": {
                }
               }
        return res
    result = []
    m = metric or conf.get("metric")
    for p in data:
        for c in data.get(p):
            point = make_data_point(m, p, c)
            for w in data.get(p).get(c):
                point["fields"][w] = data.get(p).get(c).get(w)
            result.append(point)
    return result

# creates data array to save to influxdb
def prepare_worker_stats_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, rig, worker):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "host": rig,
                    "worker": worker,
                },
                "fields": {
                }
               }
        return res
    result = []
    for r in data:
        for w in data[r]:
            m = metric or conf.get("metric")
            pt = make_data_point(m, r, w)
            pt["fields"]["power"] = data.get(r).get(w).get("power")
            pt["fields"]["hashrate"] = data.get(r).get(w).get("hashrate")
            pt["fields"]["efficiency"] = data.get(r).get(w).get("efficiency")
            result.append(pt)
    return result

# creates data array to save to influxdb
def prepare_gpu_stats_data(data, conf, metric=None):
    # creates single data point for influxdb
 def make_data_point(metric, rig, gpu):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "host": rig,
                    "gpu": gpu,
                },
                "fields": {
                }
               }
        return res
    result = []
    for r in data:
        for w in data[r]:
            for g in data[r][w]['gpu']:
                m = metric or conf.get("metric")
                pt = make_data_point(m, r, g["id"])
                pt["fields"]["power"]       = g.get("power")
                pt["fields"]["hashrate"]    = g.get("hashrate")
                pt["fields"]["efficiency"]  = g.get("efficiency")
                pt["fields"]["temperature"] = g.get("temperature")
                result.append(pt)
    return result

# save wallets' balances to influxdb
def save_wallet_balance(data, conf, metric=None):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_wallet_balance_data(data, conf, metric)):
        raise Exception("could not write data to InfluxDB")
    client.close()

# save pools' balances to influxdb
def save_pool_balance(data, conf, metric=None):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_pool_balance_data(data, conf, metric)):
        raise Exception("could not write data to InfluxDB")
    client.close()

# save worker stats to influxdb
def save_worker_stats(data, conf, metric=None):
   client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
   client.switch_database(conf["database"])
   if not client.write_points(prepare_worker_stats_data(data, conf, metric)):
       raise Exception("could not write data to InfluxDB")
   client.close()

# save GPU stats to influxdb
def save_gpu_stats(data, conf, metric=None):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_gpu_stats_data(data, conf, metric)):
        raise Exception("could not write data to InfluxDB")
    client.close()



















# print(json.dumps(conf, sort_keys=False,  indent=2,  separators=(',', ': ')))
# print(json.dumps(prepare_wallet_balance_data(data, conf), sort_keys=False,  indent=2,  separators=(',', ': ')))

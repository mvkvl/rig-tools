from influxdb import InfluxDBClient
import json

# creates single data point for influxdb
def make_wallet_balance_data_point(metric, crypto):
    res =  {"measurement": "{}".format(metric),
            "tags": {
                "crypto": crypto,
            },
            "fields": {
            }
           }
    return res
# creates data array to save to influxdb
def prepare_wallet_balance_data(data, conf, metric=None):
    result = []
    m = metric or conf.get("metric")
    for c in data:
        point = make_wallet_balance_data_point(m, c)
        for w in data.get(c):
            point["fields"][w] = data.get(c).get(w)
        result.append(point)
    return result

# creates single data point for influxdb
def make_pool_balance_data_point(metric, pool, crypto):
    res =  {"measurement": "{}".format(metric),
            "tags": {
                "crypto": crypto,
                "pool": pool,
            },
            "fields": {
            }
           }
    return res
# creates data array to save to influxdb
def prepare_pool_balance_data(data, conf, metric=None):
    result = []
    m = metric or conf.get("metric")
    for p in data:
        for c in data.get(p):
            point = make_pool_balance_data_point(m, p, c)
            for w in data.get(p).get(c):
                point["fields"][w] = data.get(p).get(c).get(w)
            result.append(point)
    return result

# save wallets' balances to influxdb
def save_wallet_balance(data, conf, metric=None):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_wallet_balance_data(data, conf, metric)):
        raise Exception("could not write data to InfluxDB")
    client.close()
    # print(json.dumps(conf, sort_keys=False,  indent=2,  separators=(',', ': ')))
    # print(json.dumps(prepare_wallet_balance_data(data, conf), sort_keys=False,  indent=2,  separators=(',', ': ')))

# save pools' balances to influxdb
def save_pool_balance(data, conf, metric=None):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_pool_balance_data(data, conf, metric)):
        raise Exception("could not write data to InfluxDB")
    client.close()

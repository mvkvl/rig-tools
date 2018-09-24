from influxdb import InfluxDBClient
import json

# creates single data point for influxdb
def make_balance_data_point(metric, crypto):
    res =  {"measurement": "{}".format(metric),
            "tags": {
                "crypto": crypto,
            },
            "fields": {
            }
           }
    return res

# creates data array to save to influxdb
def prepare_influx_balance_data(data, conf):
    result = []
    for c in data:
        point = make_balance_data_point(conf.get("metric"), c)
        for w in data.get(c):
            point["fields"][w] = data.get(c).get(w)
        result.append(point)
    return result

# save wallet balances to influxdb
def save_wallet_balance(data, conf):
    client = InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)
    client.switch_database(conf["database"])
    if not client.write_points(prepare_influx_balance_data(data, conf)):
        raise Exception("could not write data to InfluxDB")
    client.close()
    # print(json.dumps(conf, sort_keys=False,  indent=2,  separators=(',', ': ')))
    # print(json.dumps(prepare_influx_balance_data(data, conf), sort_keys=False,  indent=2,  separators=(',', ': ')))

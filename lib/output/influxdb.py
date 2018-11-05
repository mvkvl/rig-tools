from influxdb import InfluxDBClient
import json, time
import logger
import itertools

MAX_WRITE_ATTEMPTS = 5

# connect to influxdb
def __connect_influx(conf):
    return InfluxDBClient(host=conf["server"], port=conf["port"]) # , username=conf["login"], password=conf["password"] ssl=True, verify_ssl=True)

def __write_data(conf, data, module="", loglevel="ERROR"):
    client = __connect_influx(conf)
    client.switch_database(conf["database"])

    log = logger.instance(module, loglevel)

    for i in range (MAX_WRITE_ATTEMPTS):
        try:
            if client.write_points(data):
                log.info("InfluxDB write OK")
                break
            else:
                log.warning("Can't write to InfluxDB")
            time.sleep(i+1)
        except Exception as ex:
            s = str(ex).replace("b'","").replace("\\n'","") #.replace("'","\"")
            err = json.loads(s).get("error")
            log.error("InfluxDB write error - {}".format(err))
    client.close()

def __get_tag_values(metric, tag, cfg):
    # query = "show tag values from \"monitor\".\"autogen\".\"{}\" with key = {}"
    query = "show tag values from \"{}\".\"{}\" with key = {}"
    q = query.format(cfg["database"], metric, tag)
    v = read_tags(cfg, q, "value")
    return v

def __get_averaged_value(conf, period, field, metric, params):
    queryParams = "";
    for p in params:
        queryParams += " AND \"{}\" = '{}'".format(p, params.get(p))
    query = "SELECT mean(\"{}\") AS \"avgfld\" \
             FROM \"monitor\".\"autogen\".\"{}\" \
             WHERE time > now() - {} \
             {} \
             GROUP BY time({})";
    q = query.format(field, metric, period, queryParams, period);
    v = read_data(conf, q, "avgfld")
    return v

def __get_averaged_values(conf, query, period):
    result = []
    for av in query:
        for item in query.get(av):
            valuesToCheck = []
            for m in item:
                listOfLists = []
                for tag in item.get(m):
                    tagValues = __get_tag_values(m, tag, conf)
                    listOfLists.append([(tag, x) for x in tagValues])
                for li in list(itertools.product(*listOfLists)):
                    key = "{}.{}_average_{}:{}".format(m, av, period, ".".join([y for x, y in li]))
                    val = __get_averaged_value(conf, period, av, m, dict((x, y) for x, y in li))
                    if val:
                        result.append({'key': key, 'value': val})
    return result

def aggregate_data(conf, periods, data):
    result = []
    for period in periods:
        avs = __get_averaged_values(conf, data, period)
        for av in avs:
            result.append(av)
    return result

def read_data(conf, query, field):
    client = __connect_influx(conf)
    client.switch_database(conf["database"])
    rs = client.query(query)
    v  = list(rs.get_points())
    client.close()
    return float(v[0].get(field)) if v and v[0] and v[0].get(field) else None
def read_tags(conf, query, field):
    client = __connect_influx(conf)
    client.switch_database(conf["database"])
    rs = client.query(query)
    v  = list(rs.get_points())
    client.close()
    res = []
    for i in v:
        res.append(i.get('value'))
    return res

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
            point["fields"][w] = float(data.get(c).get(w))
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
                point["fields"][w] = float(data.get(p).get(c).get(w))
            result.append(point)
    return result

# creates data array to save to influxdb
def prepare_pool_stats_data(data, conf, metric=None):
    def make_data_point(metric, pool, crypto, worker, hr, avg):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "worker": worker,
                    "crypto": crypto,
                    "pool"  : pool,
                },
                "fields": {
                    "hashrate": hr,
                    "average" : avg
                }
               }
        return res
    result = []
    m = metric or conf.get("metric")
    for p in data:
        for c in data.get(p):
            for w in data.get(p).get(c).get('workers'):
                h = float(data[p][c]['workers'][w].hashrate())
                a = float(data[p][c]['workers'][w].average())
                point = make_data_point(m, p, c, w, h, a)
            result.append(point)
    return result

# creates data array to save to influxdb
def prepare_pool_worker_stats_data(data, conf, metric=None):
    def make_data_point(metric, pool, crypto, worker, hr, avg):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "worker": worker,
                    "crypto": crypto,
                    "pool"  : pool,
                },
                "fields": {
                    "hashrate": hr,
                    "average" : avg
                }
               }
        return res
    result = []
    m = metric or conf.get("metric")
    for rig in data:
        for worker in data.get(rig):
            h = float(data[rig][worker]['pool']['hashrate'])
            a = float(data[rig][worker]['pool']['average'])
            p = data[rig][worker]['pool']['name']
            c = data[rig][worker]['crypto']
            # print("{}.{}.{}: {}/{}".format(p, worker, c, h, a))
            point = make_data_point(m, p, c, worker, h, a)
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
            pt["fields"]["power"] = float(data.get(r).get(w).get("power"))
            pt["fields"]["hashrate"] = float(data.get(r).get(w).get("hashrate"))
            pt["fields"]["efficiency"] = float(data.get(r).get(w).get("efficiency"))
            result.append(pt)
    return result

# creates data array to save to influxdb
def prepare_gpu_stats_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, rig, gpu):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "host": rig,
                    "gpu" : gpu
                },
                "fields": {
                }
               }
        return res
    result = []
    for r in data:
        rig_total_power = 0
        for w in data[r]:
            for g in data[r][w]['gpu']:
                m = metric or conf.get("metric")
                pt = make_data_point(m, r, g["id"])
                pt["fields"]["power"]       = float(g.get("power"))
                pt["fields"]["hashrate"]    = float(g.get("hashrate"))
                pt["fields"]["efficiency"]  = float(g.get("efficiency"))
                pt["fields"]["temperature"] = float(g.get("temperature"))
                rig_total_power += g['power']
                result.append(pt)
        if rig_total_power > 0:
            m = metric or conf.get("metric")
            pt = make_data_point(m, r, "total")
            pt["fields"]["power"] = float(rig_total_power)
            # print(json.dumps(pt, sort_keys=True,  indent=2,  separators=(',', ': ')))
            result.append(pt)
    # print("-" * 100)
    # print(json.dumps(result, sort_keys=True,  indent=2,  separators=(',', ': ')))
    return result

# creates data array to save to influxdb
def prepare_traffic_stats_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, host, interface):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "host"     : host,
                    "interface": interface,
                },
                "fields": {
                }
               }
        return res
    result = []
    for h in data:
        for i in data[h]:
            m = metric or conf.get("metric")
            pt = make_data_point(m, h, i)
            pt["fields"]["in"]  = float(data[h][i]['rx']) # float(g.get(""))
            pt["fields"]["out"] = float(data[h][i]['tx']) # float(g.get("hashrate"))
            result.append(pt)
    return result

# creates data array to save to influxdb
def prepare_blockchain_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, crypto):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "crypto" : crypto,
                },
                "fields": {
                }
               }
        return res
    result = []
    for c in data:
        m = metric or conf.get("metric")
        pt = make_data_point(m, c)
        pt["fields"]["diff"]    = data[c]['diff']
        pt["fields"]["nethash"] = data[c]['nethash']
        result.append(pt)
    return result

def prepare_price_data(data, conf, metric=None):
    # creates single data point for influxdb
    def make_data_point(metric, crypto):
        res =  {"measurement": "{}".format(metric),
                "tags": {
                    "crypto" : crypto,
                },
                "fields": {
                }
               }
        return res
    result = []
    for crypto in data:
        m = metric or conf.get("metric")
        pt = make_data_point(m, crypto)
        for cur in data[crypto]:
            pt['fields'][cur.lower()] = float(data[crypto][cur])
        result.append(pt)
    return result

def prepare_aggregated_power_data(data, conf, metric=None):
    result = {"measurement": "{}".format(metric),
            "tags": {
                "outlet" : data["outlet"],
            },
            "fields": {
                "meter": float(data["value"])
            }
           }
    return [result]

def prepare_power_data(data, conf, metric=None):
    result = {"measurement": "{}".format(metric),
            "tags": {
                "outlet" : data["outlet"],
            },
            "fields": {
                "value": float(data["value"])
            }
           }
    return [result]


# save wallets' balances to influxdb
def save_wallet_balance(data, conf, loglevel="ERROR", module="", metric=None):
    __write_data(conf, prepare_wallet_balance_data(data, conf, metric), module=module, loglevel=loglevel)

# save pools' balances to influxdb
def save_pool_balance(data, conf, loglevel="ERROR", module="", metric=None):
    __write_data(conf, prepare_pool_balance_data(data, conf, metric), module=module, loglevel=loglevel)

# save pool stats to influxdb
def save_pool_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_pool_stats_data(data, conf, metric), module=module, loglevel=loglevel)

# save pool worker stats to influxdb
def save_pool_worker_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_pool_worker_stats_data(data, conf, metric), module=module, loglevel=loglevel)

# save worker stats to influxdb
def save_worker_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_worker_stats_data(data, conf, metric), module=module, loglevel=loglevel)

# save GPU stats to influxdb
def save_gpu_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_gpu_stats_data(data, conf, metric), module=module, loglevel=loglevel)

# save traffic stats to influxdb
def save_traffic_stats(data, conf, metric=None, module=None, loglevel="ERROR"):
    __write_data(conf, prepare_traffic_stats_data(data, conf, metric), module=module, loglevel=loglevel)

# save blockchain stats to influxdb
def save_blockchain_info(data, conf, metric=None, module=None, loglevel="ERROR"):
    # print(json.dumps(prepare_blockchain_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_blockchain_data(data, conf, metric), module=module, loglevel=loglevel)

# save crypto price to influxdb
def save_crypto_price(data, conf, metric=None, module=None, loglevel="ERROR"):
    # print(json.dumps(prepare_price_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_price_data(data, conf, metric), module=module, loglevel=loglevel)

# save aggregated power to influxdb
def save_aggregated_power(data, conf, metric=None, module=None, loglevel="ERROR"):
    # print(json.dumps(prepare_aggregated_power_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_aggregated_power_data(data, conf, metric), module=module, loglevel=loglevel)

def save_power_value(data, conf, metric=None, module=None, loglevel="ERROR"):
    # print(json.dumps(prepare_power_data(data, conf, metric), sort_keys=False,  indent=2,  separators=(',', ': ')))
    __write_data(conf, prepare_power_data(data, conf, metric), module=module, loglevel=loglevel)

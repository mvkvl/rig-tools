import yaml
import json
import tools
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from explorer import Explorer
from poolapi  import poolapi
from minerapi import minerapi
import jsonwebapi as ja

from pprint import pprint

THREAD_POOL_SIZE = 8

class WalletBalance(object):

    # performs up to THREAD_POOL_SIZE web requests in parallel
    def __balance_query(self, conf, func):
        pool = ThreadPool(THREAD_POOL_SIZE)
        result = pool.map(func, list(conf.items()))
        pool.close()
        pool.join()
        return dict(zip(conf.keys(), result))

    # calls network explorer API for given crypto / wallet
    def __get_wallet_balance(self, query):
        return Explorer(query[0].split(".")[0], query[1]).balance()

    # converts input configuration dictionary to
    # dictionary suitable for 'balance_query' call
    def __to_query(self, crypto_conf):
        query = {}
        for c in crypto_conf:
            for k in crypto_conf.get(c):
                query["{}.{}".format(c,k)] = crypto_conf.get(c).get(k)
        return query

    # converts result of 'balance_query' call to
    # initial configuration dictionary structure
    def __to_conf(self, query_res):
        conf = {}
        for k in query_res:
            a,b = k.split(".")
            if not conf.get(a):
                conf[a] = {}
            conf[a][b] = float(query_res.get(k))
        return conf

    def __init__(self, conf):
        self.conf = conf

    def query(self):
        return self.__to_conf(self.__balance_query(self.__to_query(self.conf), self.__get_wallet_balance))

class PoolBalance(object):

    # performs up to THREAD_POOL_SIZE web requests in parallel
    def __balance_query(self, conf, func):
        pool = ThreadPool(THREAD_POOL_SIZE)
        result = pool.map(func, list(conf.items()))
        pool.close()
        pool.join()
        return dict(zip(conf.keys(), result))

    # requests pool api web service
    def __get_pool_balance(self, query):
        c = query[0].split(".")[0]
        p = query[0].split(".")[1]
        k = query[1]
        api = poolapi.instance(p, c, k)
        return {"confirmed":    tools.to_float(api.balance()),
                "unconfirmed":  tools.to_float(api.unconfirmed()),
                "total":        tools.to_float(api.balance()) + tools.to_float(api.unconfirmed())}

    # converts input configuration dictionary to
    # dictionary suitable for 'balance_query' call
    def __to_query(self, crypto_conf):
        query = {}
        for c in crypto_conf:
            for k in crypto_conf.get(c):
                query["{}.{}".format(c,k)] = crypto_conf.get(c).get(k)
        return query

    # converts result of 'balance_query' call to
    # initial configuration dictionary structure
    def __to_conf(self, query_res):
        conf = {}
        for k in query_res:
            a,b = k.split(".")
            if not conf.get(b):
                conf[b] = {}
            conf[b][a] = query_res.get(k)
        return conf

    def __init__(self, conf):
        self.conf = conf

    def query(self):
        return self.__to_conf(self.__balance_query(self.__to_query(self.conf), self.__get_pool_balance))

class PoolStats(object):

    # performs up to THREAD_POOL_SIZE web requests in parallel
    def __stats_query(self, conf, func):
        pool = ThreadPool(THREAD_POOL_SIZE)
        result = pool.map(func, list(conf.items()))
        pool.close()
        pool.join()
        return dict(zip(conf.keys(), result))

    # requests pool api web service
    def __get_pool_stats(self, query):
        c = query[0].split(".")[0]
        p = query[0].split(".")[1]
        k = query[1]
        api = poolapi.instance(p, c, k)
        stats = api.status()
        if stats[0].get("hashrate")     \
           and stats[0]["hashrate"] == 0 \
           and stats[0]["unconfirmed"]  == 0 :
            return {"general": None, "workers": None}
        else:
            return {"general": stats[0], "workers": stats[1]}

    # converts input configuration dictionary to
    # dictionary suitable for 'balance_query' call
    def __to_query(self, crypto_conf):
        query = {}
        for c in crypto_conf:
            for p in crypto_conf.get(c):
                query["{}.{}".format(c,p)] = crypto_conf.get(c).get(p)
        return query

    # converts result of 'balance_query' call to
    # initial configuration dictionary structure
    def __to_conf(self, query_res):
        conf = {}
        for k in query_res:
            a,b = k.split(".")
            if not conf.get(b):
                conf[b] = {}
            conf[b][a] = query_res.get(k)
        return conf

    def __init__(self, conf):
        self.conf = conf

    def query(self):
        status = self.__to_conf(self.__stats_query(self.__to_query(self.conf), self.__get_pool_stats))
        # print(json.dumps(status, sort_keys=False,  indent=2,  separators=(',', ': ')))
        result = {}
        for p in status:
            for c in status.get(p):
                d = status.get(p).get(c)
                if d.get("general").get("hashrate") and d.get("general").get("unconfirmed"):
                    if d.get("general")["hashrate"] == 0 and d.get("general")["unconfirmed"] == 0:
                        pass
                    else:
                        if not result.get(p):
                            result[p] = {}
                        result[p][c] = d
        return result

class WorkerStats(object):

    def __init__(self, conf):
        self.conf = conf
        pass

    def query(self):
        result = {}
        for cfile in self.conf:
            with open(cfile) as f:
                d = json.load(f)
                if not result.get(d["rig"]):
                    result[d["rig"]] = {}
                result[d["rig"]][d["worker"]] = \
                              minerapi.instance(d["miner"], "{}:{}"
                                      .format(d["host"], d["apiport"])).status()
        return result

class WorkerStatsCombo(object):

    def __init__(self, rigs, pools=None):
        self.conf = {}
        self.conf['rigs']  = rigs
        self.conf['pools'] = pools

    def __get_active_miners(self):
        miners = []
        rigs   = self.conf['rigs']
        for r in rigs:
            ip = rigs[r]['url'].replace("http://","").split(":")[0]
            for w in ja.request(rigs[r]['url']):
                miners.append({
                    'worker'  : w.get('worker'),
                    'host'    : ip,
                    'apiport' : w.get('apiport'),
                    'crypto'  : w.get('crypto'),
                    'pool'    : w.get('pool'),
                    'miner'   : w.get('miner'),
                    'rig'     : r
                })
        return miners

    def __get_pool_conf(self, miners):
        result = {}
        pools  = self.conf['pools']
        for miner in miners:
            try:
                key = pools.get(miner['crypto']).get(miner['pool'])
            except:
                key = None
            if not result.get(miner['crypto']):
                result[miner['crypto']] = {}
            result[miner['crypto']][miner['pool']] = key
        return result

    def __get_miners_data(self, miners):
        result = {}
        for miner in miners:
            if not result.get(miner["rig"]):
                result[miner["rig"]] = {}
            result[miner["rig"]][miner["worker"]] = \
                          minerapi.instance(miner["miner"], "{}:{}"
                                  .format(miner["host"], miner["apiport"])).status()
            result[miner["rig"]][miner["worker"]]['crypto'] = miner["crypto"]
            result[miner["rig"]][miner["worker"]]['pool'] = miner["pool"]
        return result

    def __get_pools_data(self, pools):
        return PoolStats(pools).query()

    def __combine(self, m_data, p_data):
        for rig in m_data:
            for w in m_data[rig]:
                dt = p_data[m_data[rig][w]['pool']][m_data[rig][w]['crypto']]['workers'][w]
                pd = {}
                pd['name']     = m_data[rig][w]['pool']
                pd['hashrate'] = dt.hashrate()
                pd['average']  = dt.average()
                m_data[rig][w]['pool'] = pd
        return m_data

    def query(self):
        miners = self.__get_active_miners()
        pools  = self.__get_pool_conf(miners)
        m_data = self.__get_miners_data(miners)

        if self.conf["pools"]:
            p_data = self.__get_pools_data(pools)
            result = self.__combine(m_data, p_data)
        else:
            result = m_data

        # print(json.dumps(result, sort_keys=False,  indent=2,  separators=(',', ': ')))
        return result

class BlockchainInfo(object):

    def __init__(self, conf):
        self.conf = conf
        pass

    def query(self):
        result = {}
        for crypto in self.conf:
            result[crypto] = Explorer(crypto).network()
        return result

class CryptoPrice(object):

    def __init__(self, conf):
        self.conf = conf
        pass

    def query(self):
        result = {}
        for crypto in self.conf:
            result[crypto] = Explorer(crypto).price(self.conf[crypto])
        return result

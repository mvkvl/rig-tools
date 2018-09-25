import json, time, tools
import jsonwebapi as ja

TIMEOUT=60

class CoinblockersWorker:
    data = None
    def __init__(self, wdata, hdata):
        self.data = wdata
        self.avg = tools.get_coinblockers_averages(hdata)

    def toJSON(self):
        return {'name'      : self.name(),
                'hashrate'  : self.hashrate(),
                'average'   : self.average()
                # 'lastshare' : self.last()
               }

    def name(self):
        return self.data.get('name').split(".")[1]
    def hashrate(self):
        return float(self.data.get('hashrate')) / 1000000.0
    def average(self):
        return self.avg / 1000000.0
    def paid(self):
        return float(self.data.get('paid'))
    def last(self):
        return None

class CoinblockersAPI:
    key       = None
    data      = None
    crypto    = None
    timestamp = None
    def __init__(self, crypto, wallet):
        self.key    = wallet
        self.crypto = crypto

    def pool_data(self):
        if not self.data or time.time() - self.timestamp > TIMEOUT:
            self.data = None
            self.data = ja.request("https://{}.coinblockers.com/api/worker_stats?{}".format(self.crypto, self.key))
            self.timestamp = time.time()
        return self.data
    def balance(self):
        try:
            return self.pool_data().get('balance')
        except Exception as ex:
            return None
    def unconfirmed(self):
        try:
            return self.pool_data().get('immature')
        except Exception as ex:
            return None
    def paid(self):
        try:
            return self.pool_data().get('paid')
        except Exception as ex:
            return None
    def hashrate(self):
        try:
            return float(self.pool_data().get('totalHash')) / 1000000.0
        except Exception as ex:
            return None
    def average(self):
        return None
    def workers(self):
        try:
            result = {}
            if self.pool_data().get('workers'):
                for wn in self.pool_data().get('workers'):
                    wname = self.pool_data().get('workers').get(wn).get('name').split(".")[1]
                    w = self.pool_data().get('workers').get(wn)
                    h = self.pool_data().get('history').get(wn)
                    result[wname] = CoinblockersWorker(w, h)
            return result
        except Exception as ex:
            return {}
    def worker(self, name):
        try:
            if self.pool_data().get('workers'):
                for wn in self.pool_data().get('workers'):
                    wname = self.pool_data().get('workers').get(wn).get('name').split(".")[1]
                    if wname == name:
                        w = self.pool_data().get('workers').get(wn)
                        h = self.pool_data().get('history').get(wn)
                        return CoinblockersWorker(w, h)
            return None
        except Exception as ex:
            return None
    def status(self, worker=None):
        g_data = {}
        w_data = {}
        g_data['chashrate'] = self.hashrate()
        g_data['ahashrate'] = self.average()
        g_data['cbalance'] = self.balance()
        g_data['ubalance'] = self.unconfirmed()
        w = self.worker(worker)
        if w:
            w_data['name']      = w.name()
            w_data['chashrate'] = w.hashrate()
            w_data['ahashrate'] = w.average()
        return g_data, w_data


if __name__ == '__main__':
    snapi = CoinblockersAPI("rvn", "<<< rvn_mining_wallet >>>")
    print(json.dumps(snapi.pool_data(), indent=2, separators=(',', ': ')))

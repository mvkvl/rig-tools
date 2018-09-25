# "api" : "https://api.nanopool.org/v1/zec/user/%WALLET%"

import json, time
import jsonwebapi as ja

TIMEOUT=60

class NanopoolWorker:
    data = None
    def __init__(self, data):
        self.data = data
    def toJSON(self):
        return {'name'      : self.name(),
                'hashrate'  : self.hashrate(),
                'average'   : self.average(),
                'h1'        : self.average('h1'),
                'h3'        : self.average('h3'),
                'h6'        : self.average('h6'),
                'h12'       : self.average('h12'),
                'h24'       : self.average('h24'),
                'lastshare' : self.last()
               }
    def name(self):
        return self.data.get('id')
    def hashrate(self):
        return float(self.data.get('hashrate'))
    def average(self, h="h6"):
        return float(self.data.get(h))
    def last(self):
        return float(self.data.get(h))
        int(self.data.get("lastSeen"))

class NanopoolAPI:

    crypto    = None
    data      = None
    timestamp = None

    def __init__(self, crypto, wallet):
        self.wallet = wallet
        self.crypto = crypto
    def pool_data(self):
        try:
            if not self.data or time.time() - self.timestamp > TIMEOUT:
                self.data = ja.request("https://api.nanopool.org/v1/{}/user/{}".format(self.crypto, self.wallet)).get('data')
                self.timestamp = time.time()
        except Exception as ex:
            self.data = {}
        return self.data
    def balance(self):
        try:
            return float(self.pool_data().get('balance'))
        except Exception as ex:
            return None
    def unconfirmed(self):
        try:
            return float(self.pool_data().get('unconfirmed_balance'))
        except Exception as ex:
            return None
    def hashrate(self):
        try:
            return float(self.pool_data().get('hashrate'))
        except Exception as ex:
            return None
    def average(self,h):
        try:
            return float(self.pool_data().get('avgHashrate').get(h))
        except Exception as ex:
            return None
    def workers(self):
        result = {}
        try:
            for w in self.pool_data().get('workers'):
                result[w.get('id')] = NanopoolWorker(w)
        except Exception as ex:
            pass
        return result
    def worker(self, name):
        try:
            for w in self.pool_data().get('workers'):
                if w.get('id') == name:
                    return NanopoolWorker(w)
        except Exception as ex:
            return None
    def status(self, worker=None):
        g_data = {}
        w_data = {}
        g_data['chashrate'] = self.hashrate()
        g_data['ahashrate'] = self.average("h12")
        g_data['cbalance'] = self.balance()
        g_data['ubalance'] = self.unconfirmed()
        w = self.worker(worker)
        if w:
            w_data['name']      = w.name()
            w_data['chashrate'] = w.hashrate()
            w_data['ahashrate'] = w.average("h6")
            w_data['h1']        = w.average("h1")
            w_data['h3']        = w.average("h3")
            w_data['h6']        = w.average("h6")
            w_data['h12']       = w.average("h12")
            w_data['h24']       = w.average("h24")
        return g_data, w_data


if __name__ == '__main__':
    snapi = NanopoolAPI("zec", "<<< zec_mining_wallet >>>")
    print(json.dumps(snapi.pool_data(), indent=2, separators=(',', ': ')))

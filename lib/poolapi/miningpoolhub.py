import json, time
import jsonwebapi as ja
import tools

TIMEOUT=60

class MiningPoolHubWorker:
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
                'h24'       : self.average('h24')
               }
    def name(self):
        return self.data.get('name')
    def hashrate(self):
        return float(self.data.get('hashrate')) * 1000.0
    def average(self, h="h6"):
        return float(self.data.get(h))

API = "https://{crypto}.miningpoolhub.com/index.php?page=api&action={method}&api_key={apikey}&id={id}"

class MiningPoolHubAPI:

    id         = None
    key        = None
    crypto     = None
    data       = None
    timestamp  = None
    average_hr = None
    wrks       = None

    def __init__(self, crypto, apikey):
        self.key    = apikey.split("_")[0]
        self.id     = apikey.split("_")[1]
        self.crypto = tools.convert_crypto(crypto)

    def api_call(self, method):
        try:
            return ja.request(API.format(crypto=self.crypto, method=method, apikey=self.key, id=self.id)).get(method).get("data")
        except Exception as ex:
            print(ex)
            return None

    def pool_data(self):
        if not self.data or time.time() - self.timestamp > TIMEOUT:
            self.average_hr = None;
            self.data = {}
            self.data['status']    = self.api_call("getuserstatus")
            self.data['balance']   = self.api_call("getuserbalance")
            self.data['workers']   = self.api_call("getuserworkers")
            self.data['hourly_hr'] = self.api_call("gethourlyhashrates")
            self.timestamp = time.time()
        return self.data

    def balance(self):
        try:
            return float(self.pool_data().get('balance').get('confirmed'))
        except Exception as ex:
            return None
    def unconfirmed(self):
        try:
            return float(self.pool_data().get('balance').get('unconfirmed'))
        except Exception as ex:
            return None
    def hashrate(self):
        try:
            return float(self.pool_data().get('status').get('hashrate')) * 1000.0
        except Exception as ex:
            return None
    def average(self, h="h6"):
        try:
            self.average_hr = tools.get_mph_averages(self.pool_data())
            return self.average_hr.get(h)
        except Exception as ex:
            return None
    def workers(self):
        if not self.wrks:
            self.wrks = []
            for w in self.pool_data().get('workers'):
                w['name'] = w.get('username').replace("{}.".format(self.pool_data().get('status').get('username')), "")
                avg = tools.get_mph_averages(self.pool_data(), w['name'])
                for k in avg: w[k] = avg[k]
                self.wrks.append(MiningPoolHubWorker(w))
        return self.wrks
    def worker(self, name):
        for w in self.workers():
            if w.name() == name:
                return w

    def status(self, worker=None):
        g_data = {}
        w_data = {}
        if self.hashrate():    g_data['chashrate'] = self.hashrate()
        if self.average():     g_data['ahashrate'] = self.average()
        if self.balance():     g_data['cbalance']  = self.balance()
        if self.unconfirmed(): g_data['ubalance']  = self.unconfirmed()
        w = self.worker(worker)
        if w:
            w_data['name']      = w.name()
            w_data['chashrate'] = w.hashrate()
            w_data['ahashrate'] = w.average()
            w_data['h1']        = w.average('h1')
            w_data['h3']        = w.average('h3')
            w_data['h6']        = w.average('h6')
            w_data['h12']       = w.average('h12')
            w_data['h24']       = w.average('h24')
        return g_data, w_data

if __name__ == '__main__':
    snapi = MiningPoolHubAPI("zec", "<<< mph_api_key >>>")
    print(json.dumps(snapi.pool_data(), indent=2, separators=(',', ': ')))

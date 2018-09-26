import json, time
import jsonwebapi as ja
import time
import random
import tools

TIMEOUT=60

class SuprnovaWorker:
    data = None
    def __init__(self, data):
        self.data = data
    def toJSON(self):
        return {'name'      : self.name(),
                'hashrate'  : self.hashrate(),
                'average'   : self.average()
                # 'lastshare' : self.last()
               }
    def name(self):
        return self.data.get('username').split(".")[1]
    def hashrate(self):
        return float(self.data.get('hashrate')) / 1000.0
    def average(self):
        return 0
    def last(self):
        return None

class SuprnovaAPI:
    key       = None
    data      = None
    crypto    = None
    timestamp = None
    def __init__(self, crypto, key):
        self.key    = key
        self.crypto = crypto

    def pool_data(self):
        if not self.data or time.time() - self.timestamp > TIMEOUT:
            self.data = {}
            time.sleep(random.randrange(0, 4, 1))
            d = ja.request("https://{}.suprnova.cc/index.php?page=api&action=getuserstatus&api_key={}".format(self.crypto,  self.key))
            if d:
                self.data['status']  = d.get('getuserstatus').get('data')
            else:
                self.data['status']  = None
            time.sleep(random.randrange(0, 4, 1))
            d = ja.request("https://{}.suprnova.cc/index.php?page=api&action=getuserbalance&api_key={}".format(self.crypto, self.key))
            if d:
                self.data['balance'] = d.get('getuserbalance').get('data')
            else:
                self.data['balance']  = None
            time.sleep(random.randrange(0, 4, 1))
            d = ja.request("https://{}.suprnova.cc/index.php?page=api&action=getuserworkers&api_key={}".format(self.crypto, self.key))
            if d:
                self.data['workers'] = d.get('getuserworkers').get('data')
            else:
                self.data['workers'] = None
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
            return float(self.pool_data().get('status').get('hashrate')) / 1000.0
        except Exception as ex:
            return None
    def average(self):
        return 0
    def workers(self):
        try:
            result = {}
            if self.pool_data().get('workers'):
                for w in self.pool_data().get('workers'):
                    wname = w.get('username').split(".")[1]
                    result[wname] = SuprnovaWorker(w)
            return result
        except Exception as ex:
            return {}
    def worker(self, name):
        try:
            if self.pool_data().get('workers'):
                for w in self.pool_data().get('workers'):
                    wname = w.get('username').split(".")[1]
                    if wname == name:
                        return SuprnovaWorker(w)
            return None
        except Exception as ex:
            return {}
    def status(self, worker=None):
        g_data = {}
        w_data = {}
        g_data['hashrate']    = self.hashrate()
        # g_data['average']     = self.average()
        g_data['confirmed']   = self.balance()
        g_data['unconfirmed'] = self.unconfirmed()
        if worker:
            w = self.worker(worker)
            if w:
                w_data['name']     = w.name()
                w_data['hashrate'] = w.hashrate()
                # w_data['average']  = w.average()
        else:
            w_data = self.workers()
        return g_data, w_data


if __name__ == '__main__':
    snapi = SuprnovaAPI("zec", "<<< suprnova_api_key >>>")
    print(json.dumps(snapi.pool_data(), indent=2, separators=(',', ': ')))

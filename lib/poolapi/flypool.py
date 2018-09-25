import json, time
import jsonwebapi as ja

TIMEOUT=60

class FlypoolWorker:
    data = None
    def __init__(self, data):
        self.data = data
    def toJSON(self):
        return {"name"      : self.name(),
                "hashrate"  : self.hashrate(),
                "average"   : self.average(),
                "lastshare" : self.last()
               }
    def name(self):
        return self.data.get("worker")
    def hashrate(self):
        return float(self.data.get("currentHashrate"))
    def average(self):
        return float(self.data.get("averageHashrate"))
    def last(self):
        return int(self.data.get("lastSeen"))

class FlypoolAPI:
    crypto    = None
    data      = None
    timestamp = None
    def __init__(self, crypto, wallet):
        self.wallet = wallet
        self.crypto = crypto

    def balance_value(self, b):
        if not b:
            return 0.0
        else:
            return float(b) / 100000000.0

    def pool_data(self):
        if not self.data or time.time() - self.timestamp > TIMEOUT:
            self.data = {}
            d = ja.request("https://api-zcash.flypool.org/miner/{}/currentStats".format(self.wallet))
            if d: self.data["stats"]   = d.get("data")
            d = ja.request("https://api-zcash.flypool.org/miner/{}/workers".format(self.wallet))
            if d: self.data["workers"] = d.get("data")
            self.timestamp = time.time()
        return self.data
    def balance(self):
        try:
            return self.balance_value(self.pool_data().get("stats").get("unpaid"))
        except Exception as ex:
            return None
    def unconfirmed(self):
        try:
            return self.balance_value(self.pool_data().get("stats").get("unconfirmed"))
        except Exception as ex:
            return None
    def hashrate(self):
        try:
            return float(self.pool_data().get("stats").get("currentHashrate"))
        except Exception as ex:
            return None
    def average(self):
        try:
            return float(self.pool_data().get("stats").get("averageHashrate"))
        except Exception as ex:
            return None
    def workers(self):
        result = {}
        for w in self.pool_data().get("workers"):
            result[w.get("worker")] = FlypoolWorker(w)
        return result
    def worker(self, name):
        for w in self.pool_data().get("workers"):
            if w.get("worker") == name:
                return FlypoolWorker(w)
        return None
    def status(self, worker=None):
        g_data = {}
        w_data = {}
        g_data["chashrate"] = self.hashrate()
        g_data["ahashrate"] = self.average()
        g_data["cbalance"] = self.balance()
        g_data["ubalance"] = self.unconfirmed()
        w = self.worker(worker)
        if w:
            w_data["name"]      = w.name()
            w_data["chashrate"] = w.hashrate()
            w_data["ahashrate"] = w.average()
        return g_data, w_data


if __name__ == '__main__':
    fpapi = FlypoolAPI("zec", "<<< zec_mining_wallet >>>")
    print(json.dumps(fpapi.pool_data(), indent=2, separators=(',', ': ')))

import urllib.request
import jsonwebapi as ja
import json

# https://insight.is
# https://www.blockcypher.com/dev/dash/#address-balance-endpoint
# https://multiexplorer.com/api/address_balance/paranoid3?address=t1b6FNqZ39ep1F6L3cq4sYC6roEZ9ZAdqVa&currency=zec

class Explorer(object):

    balance_api = {
        "btc":  None, # TODO
        "zec": "https://api.zcha.in/v2/mainnet/accounts/%WALLET%",
        "zcl":  None, # TODO
        "zen": "https://explorer.zensystem.io/insight-api-zen/addr/%WALLET%?noTxList=1",
        "rvn": "https://ravencoin.network/api/addr/%WALLET%?noTxList=1",
        "xmr":  None  # TODO
     }

    network_api = {
        "rvn": {
            "url"    : "https://ravencoin.network/api/status?q=getMiningInfo",
            "field"  : "miningInfo",   # field of response to read
            "diff"   : "difficulty",   # response item for network difficulty
            "nethash": "networkhashps" # response item for network hashrate
         },
        "btc": None, # TODO
        "zec": None, # TODO
        "zcl": None, # TODO
        "zen": None, # TODO
        "xmr": None  # TODO
     }

    def __init__(self, crypto, wallet=None):
        self.crypto = crypto
        self.wallet = wallet

    def get_balance_api(self):
        result = self.balance_api.get(self.crypto)
        if not result:
            raise ValueError("Unsupported currency requested: {}".format(self.crypto))
        return result.replace("%WALLET%", self.wallet);
    def get_network_api(self):
        result = self.network_api.get(self.crypto)
        if not result:
            raise ValueError("Unsupported blockchain requested: {}".format(self.crypto))
        return result

    def balance(self):
        return ja.request(self.get_balance_api()).get("balance") or 0
    def network(self):
        net   = self.get_network_api()
        data  = ja.request(net["url"]).get(net["field"])
        return {'diff': data.get(net.get('diff')), 'nethash': data.get(net.get('nethash'))}
    def price(self, currency):
        url = "https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}".format(self.crypto.upper(), currency.upper())
        return ja.request(url)


# testing
if __name__ == '__main__':
    print(Explorer("rvn", "RD7yadeCvSDs4fCbEPuHstU3GHbiS7ao9q").balance())
    print(Explorer("rvn").price("USD,EUR"))
    print(Explorer("rvn").network())

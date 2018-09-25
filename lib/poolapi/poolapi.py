from nanopool      import NanopoolAPI
from suprnova      import SuprnovaAPI
from flypool       import FlypoolAPI
from miningpoolhub import MiningPoolHubAPI
from coinblockers  import CoinblockersAPI

class poolapi:
    @staticmethod
    def instance(pool, crypto, key):
        pools = {
            "nanopool"     : NanopoolAPI,
            'suprnova'     : SuprnovaAPI,
            'flypool'      : FlypoolAPI,
            'miningpoolhub': MiningPoolHubAPI,
            'coinblockers' : CoinblockersAPI
        }
        if pool in pools:
            return pools[pool](crypto, key)
        raise ValueError("Unsupported pool '{}'".format(pool))

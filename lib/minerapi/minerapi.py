from bminerapi import bminer
from ewbfapi   import ewbf
from zenemyapi import zenemy
from trexapi   import trex

class minerapi:
    @staticmethod
    def instance(miner, api_url):
        miners = {
            "bminer" : bminer,
            'ewbf'   : ewbf,
            "zenemy" : zenemy,
            "trex"   : trex
            # 'ccminer': ccminerapi,
            # 'dstm': dstmapi,
        }
        if miner in miners:
            return miners[miner](api_url)
        raise ValueError("Unsupported miner '{}'".format(miner))

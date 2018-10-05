
# import os,sys
# sys.path.insert(0, "{}/../".format(os.path.dirname(__file__)))

import json,time, datetime
import jsonwebapi as ja
from gpu import gpu

class trex:

    TIMEOUT = 30

    api       = None
    data      = None
    raw_data  = None
    timestamp = None

    def __init__(self, api_url):
        if api_url.startswith("http://") or api_url.startswith("https://"):
            self.api = "{}/summary".format(api_url)
        else:
            self.api = "http://{}/summary".format(api_url)

    def process_data(self, raw_data):
        # print(json.dumps(raw_data, indent=2, separators=(',', ': ')))
        total_hr = 0
        total_pw = 0
        gpus = []
        for gpu in raw_data['gpus']:
            gpuid = gpu['gpu_id']
            gpuhr = gpu['hashrate'] / 1000000.0
            gputm = gpu['temperature']
            gpupw = gpu['power']
            if (gpupw > 0):
                gpuef = gpuhr / gpupw
            else:
                gpuef = 0
            total_hr += gpuhr
            total_pw += gpupw
            gpus.append({"id":gpuid,"hashrate":gpuhr,"temperature":gputm,"power":gpupw,"efficiency":gpuef})
        total_ef = total_hr / total_pw
        summary               = {}
        summary['name']       = 't-rex'
 #       summary['start']      = datetime.datetime.fromtimestamp(int(raw_data['start_time'])).strftime('%Y-%m-%d %H:%M:%S')
        summary['accepted']   = raw_data['accepted_count']
        summary['rejected']   = raw_data['rejected_count']
        summary['hashrate']   = total_hr
        summary['power']      = total_pw
        summary['efficiency'] = total_ef
        summary['gpu']        = gpus
        return summary

    def miner_data(self):
        if not self.data or time.time() - self.timestamp > self.TIMEOUT:
            self.raw_data = ja.request(self.api)
            self.data = self.process_data(self.raw_data)
            self.timestamp = time.time()
        return self.data

    def name(self):
        return self.miner_data().get('name')
    def hashrate(self):
        return self.miner_data().get('hashrate')
    def power(self):
        return self.miner_data().get('power')
    def efficiency(self):
        return self.miner_data().get('efficiency')
    def accepted(self):
        return self.miner_data().get('accepted')
    def rejected(self):
        return self.miner_data().get('rejected')
    def started(self):
        return self.miner_data().get('start')
    def disconnects(self):
        return None
    def ping(self):
        return None
    def solved(self):
        return None
    def wait(self):
        return None
    def gpu(self, id):
        for g in self.miner_data().get('gpu'):
            if g['id'] == id:
                return gpu(g)
        return None
    def gpus(self):
        return self.miner_data().get('gpu')
    def disconnects(self):
        return 0
    def ping(self):
        return 0
    def solved(self):
        return 0
    def wait(self):
        return 0
    def toJSON(self):
        return {
                'name'        : self.name(),
                'hashrate'    : self.hashrate(),
                'power'       : self.power(),
                'efficiency'  : self.efficiency(),
                'accepted'    : self.accepted(),
                'rejected'    : self.rejected(),
                'start'       : self.started(),
                'disconnects' : self.disconnects(),
                'ping'        : self.ping(),
                'solved'      : self.solved(),
                'wait'        : self.wait(),
                'gpu'         : self.gpus()
               }
    def status(self):
        return self.toJSON()

if __name__ == '__main__':
    t = trex("127.0.0.1:10082")
    print(t.miner_data())

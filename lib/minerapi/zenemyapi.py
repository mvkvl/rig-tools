import socket, json, time, datetime, string
import jsonwebapi as ja
from gpu import gpu

# https://github.com/tpruvot/ccminer/tree/windows/api
# https://github.com/ocminer/suprminer/tree/master/api
# https://github.com/ocminer/suprminer/blob/master/api/index.php

class zenemy:

    TIMEOUT = 30

    api_host  = None
    api_port  = None
    data      = None
    raw_data  = None
    timestamp = None

    def api_call(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.api_host, self.api_port))
        sock.send(command.encode())
        resp = ''
        while 1:
            buf = sock.recv(10083)
            if buf:
                resp += buf.decode()
            else:
                break
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return resp

    def __init__(self, api_url):
        self.api_host = api_url.split(":")[0]
        self.api_port = int(api_url.split(":")[1])

    def str_to_dict(self, str):
        res = {}
        for item in str.split(";"):
            k = item.split("=")[0]
            v = item.split("=")[1]
            try: res[k] = int(v)
            except Exception as ex:
                try: res[k] = float(v)
                except Exception as ex: res[k] = v
        # print(res)
        return res

    def parse_gpus(self, data):
        gpus = []
        for gpu_str in data.split("|"):
            gpu_fstr = "".join(filter(lambda x: x in string.printable, gpu_str))
            if gpu_fstr and len(gpu_fstr) > 0:
                gpus.append(self.str_to_dict(gpu_fstr))
        return gpus

    def parse_summary(self, data):
        item_fstr = "".join(filter(lambda x: x in string.printable, data.split("|")[0]))
        if item_fstr and len(item_fstr) > 0:
            return self.str_to_dict(item_fstr)
        return None

    def parse_pool(self, data):
        item_fstr = "".join(filter(lambda x: x in string.printable, data.split("|")[0]))
        if item_fstr and len(item_fstr) > 0:
            return self.str_to_dict(item_fstr)
        return None

    def process_data(self, raw_data):
        total_hr = 0
        total_pw = 0
        gpus     = []
        for gpu in self.parse_gpus(raw_data['threads']):
            gpuid = gpu['GPU']
            gpuhr = gpu['KHS'] / 1000.0
            gputm = gpu['TEMP']
            gpupw = gpu['POWER'] / 1000.0
            if (gpupw > 0): gpuef = gpuhr / gpupw
            else:           gpuef = 0
            gpus.append({"id":gpuid,"hashrate":gpuhr,"temperature":gputm,"power":gpupw,"efficiency":gpuef})
            total_hr += gpuhr
            total_pw += gpupw

        summ = self.parse_summary(raw_data['summary'])
        pool = self.parse_pool(raw_data['pool'])
        summary                = {}
        summary['name']        = 'zenemy'
        # summary['start']      = datetime.datetime.fromtimestamp(int(raw_data['start_time'])).strftime('%Y-%m-%d %H:%M:%S')
        summary['accepted']    = summ['ACC']
        summary['rejected']    = summ['REJ']
        summary['hashrate']    = summ['KHS'] / 1000.0
        summary['power']       = total_pw
        summary['disconnects'] = pool['DISCO']
        summary['ping']        = pool['PING']
        summary['solved']      = pool['SOLV']
        summary['wait']        = pool['WAIT']
        try:                    summary['efficiency'] = summary['hashrate'] / summary['power']
        except Exception as ex: summary['efficiency'] = 0
        summary['gpu']        = gpus
        return summary

    def miner_data(self):
        if not self.data or time.time() - self.timestamp > self.TIMEOUT:
            self.raw_data = {}
            self.raw_data['summary'] = self.api_call("summary")
            self.raw_data['threads'] = self.api_call("threads")
            self.raw_data['pool']    = self.api_call("pool")
            self.timestamp = time.time()
            self.data = self.process_data(self.raw_data)
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
    def disconnects(self):
        return self.miner_data().get('disconnects')
    def ping(self):
        return self.miner_data().get('ping')
    def solved(self):
        return self.miner_data().get('solved')
    def wait(self):
        return self.miner_data().get('wait')
    def started(self):
        # return self.miner_data().get('start')
        return 0
    def gpu(self, id):
        for g in self.miner_data().get('gpu'):
            if g['id'] == id:
                return gpu(g)
        return None
    def gpus(self):
        return self.miner_data().get('gpu')
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

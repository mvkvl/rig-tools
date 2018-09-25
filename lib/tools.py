import json, datetime

def dump(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

def convert_crypto(crypto):
    c = {
        "zen" : "zencash"
       ,"zec" : "zcash"
       ,"xmr" : "monero"
    }
    return c[crypto]
def get_mph_averages(data, worker_name=""):
    arr = []
    avg = {}
    if data.get('hourly_hr'):
        for hhr in data.get('hourly_hr').get('mine'):
            rpl_str = data.get('status').get('username')
            if hhr['username'].replace("{}.".format(rpl_str), "") == worker_name:
                if hhr.get('hashrate'):
                    for k in hhr['hashrate']:
                        v = hhr['hashrate'].get(k)
                        arr.append(v)
                        break
                else:
                    arr.append(0)
    if len(arr) > 0:
        avg['h1']  = (sum(arr[len(arr)-1: ])     ) * 1000.0
        avg['h3']  = (sum(arr[len(arr)-2: ]) / 3 ) * 1000.0
        avg['h6']  = (sum(arr[len(arr)-6: ]) / 6 ) * 1000.0
        avg['h12'] = (sum(arr[len(arr)-12:]) / 12) * 1000.0
        avg['h24'] = (sum(arr[len(arr)-24:]) / 24) * 1000.0
    return avg

def get_coinblockers_averages(data):
    len = 0;
    tot = 0;
    for k in data:
        len = len + 1
        tot = tot + float(k.get('hashrate'))
        # t = datetime.datetime.fromtimestamp(int(k.get('time'))).strftime('%Y-%m-%d %H:%M:%S')
        # print ("{}: {}".format(t, ))
    return tot / len

def check_num_value(value):
    if value:
        return float(value)
    else:
        return None

def check_num_values(value1, value2):
    result = None
    if value1:
        result = float(value1)
    pass

# safely converts received number to float
def to_float(val):
    try:
        return float(val)
    except:
        return 0.0

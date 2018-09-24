import json

# output result to stdout
def output(data, conf=None):
    print(json.dumps(data, sort_keys=False,  indent=2,  separators=(',', ': ')))

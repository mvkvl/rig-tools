
class gpu:

    data = None

    def __init__(self, data):
        self.data = data
    def id(self):
        return self.data['id']
    def hashrate(self):
        return self.data['hashrate']
    def temperature(self):
        return self.data['temperature']
    def power(self):
        return self.data['power']
    def efficiency(self):
        return self.data['efficiency']
    def toJSON(self):
        return {'id'          : self.id(),
                'hashrate'    : self.hashrate(),
                'temperature' : self.temperature(),
                'power'       : self.power(),
                'efficiency'  : self.efficiency()
               }

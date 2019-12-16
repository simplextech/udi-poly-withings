
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsBPMNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(WithingsBPMNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.measures = measures
        self.parent = primary

    def start(self):
        if self.devices is not None:
            for dev in self.devices['body']['devices']:
                _device_id = dev['deviceid'][-3:].lower()
                _node = self.parent + _device_id

                if _node == self.address:
                    if dev['type'] == "Blood Pressure Monitor":
                        value = dev['battery']
                        if value == "low":
                            battery = 1
                        elif value == "medium":
                            battery = 2
                        elif value == "high":
                            battery = 3
                        else:
                            battery = 0
                        self.setDriver('BATLVL', battery)

        if self.measures is not None:
            for body in self.measures['body']['measuregrps']:
                _device_id = body['deviceid'][-3:].lower()
                _node = self.parent + _device_id

                if _node == self.address:
                    for measure in body['measures']:
                        _type = measure['type']
                        _unit = measure['unit']
                        _value = measure['value']

                        if _unit == -3:
                            value = _value / 1000
                        elif _unit == -2:
                            value = _value / 100
                        else:
                            value = _value

                        if _type == 11:  # Heart Rate (Pulse)
                            self.setDriver('ST', value)
                        if _type == 10:  # Systolic
                            self.setDriver('GV0', value)
                        if _type == 9:  # Diastolic
                            self.setDriver('GV1', value)

    def query(self, command=None):
        # command = [devices, measures, activities, sleep]
        if command is not None:
            self.devices = command[0]
            self.measures = command[1]
            self.start()
        else:
            self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_BPM'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 56},
               {'driver': 'GV1', 'value': 0, 'uom': 56}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }

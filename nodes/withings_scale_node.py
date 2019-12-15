
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsScaleNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(WithingsScaleNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.measures = measures

    def start(self):
        if self.devices is not None:
            for dev in self.devices['body']['devices']:
                if dev['type'] == "Scale":
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
                for measure in body['measures']:
                    _type = measure['type']
                    value = measure['value']
                    if _type == 1:  # Weight
                        val = utils.kilogram_to_pound_weight(value)
                        self.setDriver('ST', val)
                    if _type == 76:  # Muscle Mass
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV0', val)
                    if _type == 88:  # Bone Mass
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV1', val)
                    if _type == 8:  # Fat Mass Weight
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV2', val)
                    if _type == 5:  # Fat Free Mass
                        val = utils.kilogram_to_pound_weight(value)
                        self.setDriver('GV3', val)
                    if _type == 6:  # Fat Ratio
                        val = utils.json_to_normal(value)
                        self.setDriver('GV4', val)
                    if _type == 11:  # Heart Rate (Pulse)
                        val = value
                        self.setDriver('GV5', val)

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

    id = 'WITHINGS_SCALE'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 52},
               {'driver': 'GV1', 'value': 0, 'uom': 52},
               {'driver': 'GV2', 'value': 0, 'uom': 52},
               {'driver': 'GV3', 'value': 0, 'uom': 52},
               {'driver': 'GV4', 'value': 0, 'uom': 51},
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class WithingsScaleHRNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(WithingsScaleHRNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.measures = measures

    def start(self):
        if self.devices is not None:
            for dev in self.devices['body']['devices']:
                if dev['type'] == "Scale":
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
                for measure in body['measures']:
                    _type = measure['type']
                    value = measure['value']
                    if _type == 1:  # Weight
                        val = utils.kilogram_to_pound_weight(value)
                        self.setDriver('ST', val)
                    if _type == 76:  # Muscle Mass
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV0', val)
                    if _type == 88:  # Bone Mass
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV1', val)
                    if _type == 8:  # Fat Mass Weight
                        val = utils.kilogram_to_pound_mass(value)
                        self.setDriver('GV2', val)
                    if _type == 5:  # Fat Free Mass
                        val = utils.kilogram_to_pound_weight(value)
                        self.setDriver('GV3', val)
                    if _type == 6:  # Fat Ratio
                        val = utils.json_to_normal(value)
                        self.setDriver('GV4', val)
                    if _type == 11:  # Heart Rate (Pulse)
                        val = value
                        self.setDriver('GV5', val)

    def query(self, command=None):
        self.reportDrivers()

    id = 'WITHINGS_SCALE_HR'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 52},
               {'driver': 'GV1', 'value': 0, 'uom': 52},
               {'driver': 'GV2', 'value': 0, 'uom': 52},
               {'driver': 'GV3', 'value': 0, 'uom': 52},
               {'driver': 'GV4', 'value': 0, 'uom': 52},
               {'driver': 'GV5', 'value': 0, 'uom': 52},
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
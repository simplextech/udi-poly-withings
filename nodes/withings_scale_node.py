
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
        self.parent = primary

    def start(self):
        if self.devices is not None:
            for dev in self.devices['body']['devices']:
                _device_id = dev['deviceid'][-3:].lower()
                _node = self.parent + _device_id

                if _node == self.address:
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

                        if _type == 1:  # Weight
                            val = utils.kilogram_to_pound(value)
                            self.setDriver('ST', val)
                        if _type == 76:  # Muscle Mass
                            val = utils.kilogram_to_pound(value)
                            self.setDriver('GV0', val)
                        if _type == 88:  # Bone Mass
                            val = utils.kilogram_to_pound(value)
                            self.setDriver('GV1', val)
                        if _type == 8:  # Fat Mass Weight
                            val = utils.kilogram_to_pound(value)
                            self.setDriver('GV2', val)
                        if _type == 5:  # Fat Free Mass
                            val = utils.kilogram_to_pound(value)
                            self.setDriver('GV3', val)
                        if _type == 6:  # Fat Ratio
                            val = round(value, 1)
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


class WithingsScaleHRNode(WithingsScaleNode):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(WithingsScaleHRNode, self).__init__(controller, primary, address, name, devices, measures)

    id = 'WITHINGS_SCALE_HR'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 52},
               {'driver': 'GV1', 'value': 0, 'uom': 52},
               {'driver': 'GV2', 'value': 0, 'uom': 52},
               {'driver': 'GV3', 'value': 0, 'uom': 52},
               {'driver': 'GV4', 'value': 0, 'uom': 51},
               {'driver': 'GV5', 'value': 0, 'uom': 56},
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class OldWithingsScaleHRNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(OldWithingsScaleHRNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.measures = measures
        self.user_id = primary

    def start(self):
        if self.devices is not None:
            # _user = str(self.user_id).replace('0', '')[-3:].lower()

            for dev in self.devices['body']['devices']:
                _device_id = dev['deviceid']
                _node = self.user_id + _device_id

                if _node == self.address:
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
            # _user = str(self.user_id).replace('0', '')[-3:].lower()

            for body in self.measures['body']['measuregrps']:
                _device_id = str(body['deviceid'])[-3:].lower()
                _node = self.user_id + _device_id
                print("Device ID: " + _device_id)
                print("Node Address: " + _node)

                if _node == self.address:
                    for measure in body['measures']:
                        _type = measure['type']
                        _unit = measure['unit']
                        _value = measure['value']

                        if _unit == '-3':
                            value = _value / 1000
                        elif _unit == '-2':
                            value = _value / 100
                        else:
                            value = 0

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
                            # val = value
                            self.setDriver('GV5', value)

    def query(self, command=None):
        # command = [user_id, devices, measures, activities, sleep]
        if command is not None:
            self.user_id = command[0]
            self.devices = command[1]
            self.measures = command[2]
            self.start()
        else:
            self.reportDrivers()

    id = 'WITHINGS_SCALE_HR'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 52},
               {'driver': 'GV1', 'value': 0, 'uom': 52},
               {'driver': 'GV2', 'value': 0, 'uom': 52},
               {'driver': 'GV3', 'value': 0, 'uom': 52},
               {'driver': 'GV4', 'value': 0, 'uom': 51},
               {'driver': 'GV5', 'value': 0, 'uom': 56},
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
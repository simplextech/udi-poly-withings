
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsActivityTrackerNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, activities):
        super(WithingsActivityTrackerNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.activities = activities

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

        if self.activities is not None:
            for body in self.activities['body']['activities']:
                for act in body:
                    value = body[act]
                    if act == 'steps':
                        val = value
                        self.setDriver('ST', val)
                    if act == 'distance':
                        val = utils.meters_to_mile(value)
                        self.setDriver('GV0', val)
                    if act == 'elevation':
                        val = value
                        self.setDriver('GV1', val)
                    if act == 'soft':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV2', val)
                    if act == 'moderate':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV3', val)
                    if act == 'intense':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV4', val)
                    if act == 'active':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV5', val)
                    if act == 'calories':
                        val = round(value, 2)
                        self.setDriver('GV6', val)
                    if act == 'totalcalories':
                        val = round(value, 2)
                        self.setDriver('GV7', val)

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_ACTIVITY'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'BATLVL', 'value': 0, 'uom': 25},
               {'driver': 'GV0', 'value': 0, 'uom': 116},
               {'driver': 'GV1', 'value': 0, 'uom': 56},
               {'driver': 'GV2', 'value': 0, 'uom': 45},
               {'driver': 'GV3', 'value': 0, 'uom': 45},
               {'driver': 'GV4', 'value': 0, 'uom': 45},
               {'driver': 'GV5', 'value': 0, 'uom': 45},
               {'driver': 'GV6', 'value': 0, 'uom': 56},
               {'driver': 'GV7', 'value': 0, 'uom': 56}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class WithingsActivityTrackerHRNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, activities):
        super(WithingsActivityTrackerHRNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.activities = activities

    def start(self):
        if self.activities is not None:
            for body in self.activities['body']['activities']:
                for act in body:
                    value = body[act]
                    if act == 'hr_average':
                        val = value
                        self.setDriver('ST', val)
                    if act == 'hr_min':
                        val = value
                        self.setDriver('GV0', val)
                    if act == 'hr_max':
                        val = value
                        self.setDriver('GV1', val)
                    if act == 'hr_zone_0':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV2', val)
                    if act == 'hr_zone_1':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV3', val)
                    if act == 'hr_zone_2':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV4', val)
                    if act == 'hr_zone_3':
                        val = utils.seconds_to_minutes(value)
                        self.setDriver('GV5', val)

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_ACTIVITY_HR'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'GV0', 'value': 0, 'uom': 56},
               {'driver': 'GV1', 'value': 0, 'uom': 56},
               {'driver': 'GV2', 'value': 0, 'uom': 45},
               {'driver': 'GV3', 'value': 0, 'uom': 45},
               {'driver': 'GV4', 'value': 0, 'uom': 45},
               {'driver': 'GV5', 'value': 0, 'uom': 45}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
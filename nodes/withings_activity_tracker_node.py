
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
        self.user_id = None

    def start(self):
        if self.devices is not None:
            for dev in self.devices['body']['devices']:
                if dev['type'] == "Activity Tracker":
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
                        if value == 0:
                            self.setDriver('GV1', value, force=True)
                        else:
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

    def query(self, command=None):
        # command = [devices, measures, activities, sleep]
        if command is not None:
            self.devices = command[0]
            self.activities = command[2]
            self.start()
        else:
            self.reportDrivers()
    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_ACTIVITY'

    '''
    ST:     Steps
    GV0:    Distance
    GV1:    Elevation (floors)
    GV2:    Soft/Light Activity
    GV3:    Moderate Activity
    GV4:    Intense Activity
    GV5:    Sum Mod/Int Activity
    GV6:    Calories Burned
    GV7:    Total Calories Burned (Resting + Active)
    '''
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
        self.user_id = None

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

    def query(self, command=None):
        # command = [devices, measures, activities, sleep]
        if command is not None:
            self.devices = command[0]
            self.activities = command[2]
            self.start()
        else:
            self.reportDrivers()

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


class WithingsActivityTrackerSleepNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, sleep):
        super(WithingsActivityTrackerSleepNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.sleep = sleep
        self.user_id = None

    def start(self):
        if self.sleep is not None:
            for series in self.sleep['body']['series']:
                model = series['model']
                if model == 16:
                    for entry in series['data']:
                        value = series['data'][entry]
                        if entry == "sleep_score":
                            val = value
                            self.setDriver('ST', val)
                        if entry == "lightsleepduration":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV0', val)
                        if entry == "deepsleepduration":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV1', val)
                        if entry == "wakeupcount":
                            val = value
                            self.setDriver('GV2', val)
                        if entry == "wakeupduration":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV3', val)
                        if entry == "durationtosleep":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV4', val)
                        if entry == "durationtowakeup":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV5', val)
                        if entry == "hr_average":
                            val = value
                            self.setDriver('GV6', val)
                        if entry == "hr_min":
                            val = value
                            self.setDriver('GV7', val)
                        if entry == "hr_max":
                            val = value
                            self.setDriver('GV8', val)

    def query(self, command=None):
        # command = [devices, measures, activities, sleep]
        if command is not None:
            self.devices = command[0]
            self.sleep = command[3]
            self.start()
        else:
            self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_ACTIVITY_SLEEP'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'GV0', 'value': 0, 'uom': 45},
               {'driver': 'GV1', 'value': 0, 'uom': 45},
               {'driver': 'GV2', 'value': 0, 'uom': 56},
               {'driver': 'GV3', 'value': 0, 'uom': 45},
               {'driver': 'GV4', 'value': 0, 'uom': 45},
               {'driver': 'GV5', 'value': 0, 'uom': 45}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class WithingsActivityTrackerSleepHRNode(WithingsActivityTrackerSleepNode):
    def __init__(self, controller, primary, address, name, devices, sleep):
        super(WithingsActivityTrackerSleepHRNode, self).__init__(controller, primary, address, name, devices, sleep)

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_ACTIVITY_SLEEP_HR'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'GV0', 'value': 0, 'uom': 45},
               {'driver': 'GV1', 'value': 0, 'uom': 45},
               {'driver': 'GV2', 'value': 0, 'uom': 56},
               {'driver': 'GV3', 'value': 0, 'uom': 45},
               {'driver': 'GV4', 'value': 0, 'uom': 45},
               {'driver': 'GV5', 'value': 0, 'uom': 45},
               {'driver': 'GV6', 'value': 0, 'uom': 56},
               {'driver': 'GV7', 'value': 0, 'uom': 56},
               {'driver': 'GV8', 'value': 0, 'uom': 56}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsSleepNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, sleep):
        super(WithingsSleepNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.sleep = sleep
        self.user_id = None

    def start(self):
        if self.sleep is not None:
            for series in self.sleep['body']['series']:
                model = series['model']
                if model == 32:
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
                        if entry == "remsleepduration":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV2', val)
                        if entry == "wakeupcount":
                            val = value
                            self.setDriver('GV3', val)
                        if entry == "wakeupduration":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV4', val)
                        if entry == "durationtosleep":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV5', val)
                        if entry == "durationtowakeup":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV6', val)
                        if entry == "hr_average":
                            val = value
                            self.setDriver('GV7', val)
                        if entry == "hr_min":
                            val = value
                            self.setDriver('GV8', val)
                        if entry == "hr_max":
                            val = value
                            self.setDriver('GV9', val)
                        if entry == "rr_average":
                            val = value
                            self.setDriver('GV10', val)
                        if entry == "rr_min":
                            val = value
                            self.setDriver('GV11', val)
                        if entry == "rr_max":
                            val = value
                            self.setDriver('GV12', val)
                        if entry == "breathing_disturbances_intensity":
                            if value <= 30:
                                val = 1
                            elif value > 30 <= 60:
                                val = 2
                            elif value > 60:
                                val = 3
                            else:
                                val = 0
                            self.setDriver('GV13', val)
                        if entry == "snoring":
                            val = utils.seconds_to_minutes(value)
                            self.setDriver('GV14', val)
                        if entry == "snoringepisodecount":
                            val = value
                            self.setDriver('GV15', val)

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

    id = 'WITHINGS_SLEEP'

    '''
    ST:     Sleep Score
    GV0:    Light Sleep Duration
    GV1:    Deep Sleep Duration
    GV2:    REM Sleep Duration
    GV3:    Wakeup Count
    GV4:    Wakeup Duration
    GV5:    Duration to sleep
    GV6:    Duration to Wakeup
    GV7:    HR Average
    GV8:    HR Min
    GV9:    HR Max
    GV10:    RR Average
    GV11:   RR Min
    GV12:   RR Max
    GV13:   Breathing Disturbances Intensity
    GV14:   Snoring (seconds)
    GV15:   Snoring Episodes
    GV16:   In Bed
    '''

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 56},
               {'driver': 'GV0', 'value': 0, 'uom': 45},
               {'driver': 'GV1', 'value': 0, 'uom': 45},
               {'driver': 'GV2', 'value': 0, 'uom': 45},
               {'driver': 'GV3', 'value': 0, 'uom': 56},
               {'driver': 'GV4', 'value': 0, 'uom': 45},
               {'driver': 'GV5', 'value': 0, 'uom': 45},
               {'driver': 'GV6', 'value': 0, 'uom': 45},
               {'driver': 'GV7', 'value': 0, 'uom': 56},
               {'driver': 'GV8', 'value': 0, 'uom': 56},
               {'driver': 'GV9', 'value': 0, 'uom': 56},
               {'driver': 'GV10', 'value': 0, 'uom': 56},
               {'driver': 'GV11', 'value': 0, 'uom': 56},
               {'driver': 'GV12', 'value': 0, 'uom': 56},
               {'driver': 'GV13', 'value': 0, 'uom': 25},
               {'driver': 'GV14', 'value': 0, 'uom': 56},
               {'driver': 'GV15', 'value': 0, 'uom': 56},
               {'driver': 'GV16', 'value': 0, 'uom': 95}
               ]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
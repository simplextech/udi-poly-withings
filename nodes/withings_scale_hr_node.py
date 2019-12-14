
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsScaleHRNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, devices, measures):
        super(WithingsScaleHRNode, self).__init__(controller, primary, address, name)
        self.devices = devices
        self.measures = measures

    def start(self):
        custom_data = self.polyConfig['customData']
        for user_id in custom_data.keys():
            # access_token = custom_data[user_id]['access_token']
            user = custom_data[user_id]['user_id']
            # withings = Withings(access_token)
            parent_address = str(user)[-3:]

            devices = withings.get_devices()
            if devices is not None:
                for dev in devices['body']['devices']:
                    value = dev['battery']
                    if value == "low":
                        battery = 1
                    elif value == "medium":
                        battery = 2
                    elif value == "high":
                        battery = 3
                    else:
                        battery = 0

                    node_address = dev['deviceid'][-6:].lower()
                    self.nodes[node_address].setDriver('ST', battery)
        self.setDriver('ST', 1)

    # def shortPoll(self):
    #     LOGGER.debug('shortPoll')
    #
    # def longPoll(self):
    #     LOGGER.debug('longPoll')
    #
    # def setOn(self, command):
    #     self.setDriver('ST', 1)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)
    #
    # def query(self, command=None):
    #     self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_SCALE_HR'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52}]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import utils

LOGGER = polyinterface.LOGGER


class WithingsScaleNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, model_id):
        super(WithingsScaleNode, self).__init__(controller, primary, address, name)
        self.model_id = 0

    def start(self):
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

    id = 'WITHINGS_SCALE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 52}]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }
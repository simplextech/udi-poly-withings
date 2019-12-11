
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface


LOGGER = polyinterface.LOGGER


class WithingsDeviceNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, value):
        super(WithingsDeviceNode, self).__init__(controller, primary, address, name)
        self.value = value

    def start(self):
        if self.value == "low":
            battery = 1
        elif self.value == "medium":
            battery = 2
        elif self.value == "high":
            battery = 3
        else:
            battery = 0
        self.setDriver('ST', battery)

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

    id = 'WITHINGS_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 25}]

    commands = {
        # 'DON': setOn, 'DOF': setOff
    }

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface


LOGGER = polyinterface.LOGGER


class WithingsParentNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(WithingsParentNode, self).__init__(controller, primary, address, name)

    def start(self):
        self.setDriver('ST', 1)

    def shortPoll(self):
        LOGGER.debug('shortPoll')

    def longPoll(self):
        LOGGER.debug('longPoll')

    def setOn(self, command):
        self.setDriver('ST', 1)

    def setOff(self, command):
        self.setDriver('ST', 0)

    def query(self, command=None):
        LOGGER.debug('query')
        # self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'PARENT_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


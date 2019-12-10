#!/usr/bin/env python

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
from flask import Flask
from flask import Response
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from withings import Withings
import copy

LOGGER = polyinterface.LOGGER


def meters_to_feet(meters):
    ft = round((meters / 1000) * 3.2808, 1)
    return ft


def kilogram_to_pound(kilogram):
    lb = round((kilogram / 1000) * 2.2046, 2)
    return lb


class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Withings Controller'
        # self.poly.onConfig(self.process_config)
        self.server_data = {}
        self.access_token = None
        self.user_info = {}
        self.disco = 0

    def start(self):
        # This grabs the server.json data and checks profile_version is up to date
        # serverdata = self.poly.get_server_data()
        # LOGGER.info('Started Template NodeServer {}'.format(serverdata['version']))
        # self.check_params()
        # self.discover()
        # self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")
        # callback_server = threading.Thread(name='Callback Server', target=self.flask_server)
        # callback_server.setDaemon(True)
        # callback_server.start()

        print("-----------------------------------")
        print("httpsIngress: " + str(self.poly.init['netInfo']['httpsIngress']))
        print("publicIp: " + self.poly.init['netInfo']['publicIp'])
        print("-----------------------------------")
        # httpd = HTTPServer(('0.0.0.0', 3000), CallBackServer)
        # httpd.serve_forever()

        # cb_server = threading.Thread(name='Callback Server', target=CallBackServer.flask_server())
        # cb_server.setDaemon(True)
        # cb_server.start()
        if self.get_credentials():
            self.auth_prompt()
            if self.refresh_token():
                self.discover()
            else:
                self.auth_prompt()
        else:
            LOGGER.error("Credentials for OAuth are not available")

    # def flask_server(self):
    #     print("-----------------------------------")
    #     print("httpsIngress: " + str(self.poly.init['netInfo']['httpsIngress']))
    #     print("publicIp: " + self.poly.init['netInfo']['publicIp'])
    #     print("-----------------------------------")
    #     httpsIngress = self.poly.init['netInfo']['httpsIngress']
    #     publicIp = self.poly.init['netInfo']['publicIp']
    #
    #     app = Flask(__name__)
    #
    #     @app.route("/test")
    #     def hello():
    #         print("----------------- Hello World ------------------")
    #         return Response("{'a':'b'}", status=200, mimetype='application/json')
    #
    #     app.run(debug=True, use_reloader=False, host="0.0.0.0", port=3000)
    #     # app.run(host="0.0.0.0", port=3000)
    #     # app.debug = False
    #     # threading.Thread(target=app.run(host="0.0.0.0", port=3000)).start()

    def get_credentials(self):
        LOGGER.debug('---- Environment: ' + self.poly.stage + ' ----')
        LOGGER.debug('---- OAuth Dict: ----')
        LOGGER.debug(self.poly.init['oauth'])
        if self.poly.stage == 'test':
            if 'clientId' in self.poly.init['oauth']['test']:
                self.server_data['clientId'] = self.poly.init['oauth']['test']['clientId']
            else:
                LOGGER.error('Unable to find Client ID in the init data')
                return False
            if 'secret' in self.poly.init['oauth']['test']:
                self.server_data['clientSecret'] = self.poly.init['oauth']['test']['secret']
            else:
                LOGGER.error('Unable to find Client Secret in the init data')
                return False
            if 'redirectUrl' in self.poly.init['oauth']['test']:
                self.server_data['url'] = self.poly.init['oauth']['test']['redirectUrl']
            else:
                LOGGER.error('Unable to find URL in the init data')
                return False
            if self.poly.init['worker']:
                self.server_data['worker'] = self.poly.init['worker']
            else:
                return False
            return True
        elif self.poly.stage == 'prod':
            if 'clientId' in self.poly.init['oauth']['prod']:
                self.server_data['clientId'] = self.poly.init['oauth']['prod']['clientId']
            else:
                LOGGER.error('Unable to find Client ID in the init data')
                return False
            if 'secret' in self.poly.init['oauth']['test']:
                self.server_data['clientSecret'] = self.poly.init['oauth']['prod']['secret']
            else:
                LOGGER.error('Unable to find Client Secret in the init data')
                return False
            if 'redirectUrl' in self.poly.init['oauth']['test']:
                self.server_data['url'] = self.poly.init['oauth']['prod']['redirectUrl']
            else:
                LOGGER.error('Unable to find URL in the init data')
                return False
            if self.poly.init['worker']:
                self.server_data['worker'] = self.poly.init['worker']
            else:
                return False
            return True

    def auth_prompt(self):
        LOGGER.debug("----------- Running auth_prompt ----------------")
        _auth_url = "https://account.withings.com/oauth2_user/authorize2"
        _scope = "user.info,user.metrics,user.activity"

        _user_auth_url = _auth_url + \
                         "?client_id=" + self.server_data['clientId'] + \
                         "&response_type=" + "code" + \
                         "&scope=" + _scope + \
                         "&redirect_uri=" + self.server_data['url'] + \
                         "&state=" + self.server_data['worker']

        self.addNotice(
            {'myNotice': 'Click <a href="' + _user_auth_url + '">here</a> to link your Withings account'})

    def oauth(self, oauth):
        LOGGER.info('OAUTH Received: {}'.format(oauth))
        if 'code' in oauth:
            self.get_token(oauth['code'])
        else:
            print(oauth)

    def get_token(self, code):
        _token_url = "https://account.withings.com/oauth2/token"

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {"grant_type": "authorization_code",
                   "code": code,
                   "client_id": self.server_data['clientId'],
                   "client_secret": self.server_data['clientSecret'],
                   "redirect_uri": self.server_data['url']}

        # print("Get Token Begin----------------------------------")
        custom_data = copy.deepcopy(self.polyConfig['customData'])
        # print(custom_data)
        # print("Get Token Begin----------------------------------")

        try:
            r = requests.post(_token_url, headers=headers, data=payload)
            if r.status_code == requests.codes.ok:
                try:
                    resp = r.json()
                    access_token = resp['access_token']
                    refresh_token = resp['refresh_token']
                    expires_in = resp['expires_in']
                    user_id = resp['userid']

                    # print("------------ NEW USER: " + str(user_id) + " ----------------")
                    custom_data[user_id] = {'access_token': access_token,
                                            'refresh_token': refresh_token,
                                            'expires_in': expires_in}

                    # print("Get Token End----------------------------------")
                    # print(custom_data)
                    # print("Get Token End----------------------------------")

                    self.saveCustomData(custom_data)

                    return True
                except KeyError as ex:
                    LOGGER.error("get_token Error: " + str(ex))
            else:
                return False
        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))

    def refresh_token(self):
        _state = None
        _token_url = "https://account.withings.com/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        custom_data = copy.deepcopy(self.polyConfig['customData'])
        # print("---------------------------- refresh_token ----------------------------")

        for user_id in custom_data.keys():
            # print("----refresh token-------- USER: " + str(user_id) + " ----------------")
            payload = {"grant_type": "refresh_token",
                       "client_id": self.server_data['clientId'],
                       "client_secret": self.server_data['clientSecret'],
                       "refresh_token": custom_data[user_id]['refresh_token']
                       }
            # print("---refresh token ----- " + custom_data[user_id]['refresh_token'])
            try:
                r = requests.post(_token_url, headers=headers, data=payload)
                if r.status_code == requests.codes.ok:
                    resp = r.json()
                    access_token = resp['access_token']
                    refresh_token = resp['refresh_token']
                    expires_in = resp['expires_in']
                    # user_id = resp['userid']

                    custom_data[user_id] = {'access_token': access_token,
                                            'refresh_token': refresh_token,
                                            'expires_in': expires_in}

                    _state = True
                else:
                    _state = False
            except requests.exceptions.RequestException as e:
                LOGGER.error("Error: " + str(e))

        if _state:
            # print("---------------refresh  New Custom Data -----------------------")
            # print(custom_data)
            self.saveCustomData(custom_data)
            time.sleep(3)
            return True
        else:
            return False

    def shortPoll(self):
        if self.disco != 0:
            LOGGER.debug('shortPoll')

    def longPoll(self):
        LOGGER.debug('longPoll')

    def query(self, command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        measure_type_map = {
                            1: 'Weight',
                            4: 'Height',
                            5: 'Fat Free Mass',
                            6: 'Fat Ratio',
                            8: 'Fat Mass Weight',
                            9: 'Diastolic Blood Pressure',
                            10: 'Systolic Blood Pressure',
                            11: 'Heart Pulse',
                            12: 'Temperature',
                            54: 'SP02',
                            71: 'Body Temperature',
                            73: 'Skin Temperature',
                            76: 'Muscle Mass',
                            77: 'Hydration',
                            88: 'Bone Mass',
                            91: 'Pulse Wave Velocity'
                            }

        activities_map = {'steps': 'Steps',
                          'distance': 'Distance in Steps',
                          'elevation': 'Floors Climbed',
                          'soft': 'Light Activity',
                          'moderate': 'Moderate Activity',
                          'intense': 'Intense Activity',
                          'active': 'Sum of Intense and Moderate',
                          'calories': 'Active calories burned',
                          'totalcalories': 'Total calories burned',
                          'hr_average': 'Average heart rate',
                          'hr_min': 'Minimal heart rate',
                          'hr_max': 'Maximal heart rate',
                          'hr_zone_0': 'Duration in light zone',
                          'hr_zone_1': 'Duration in moderate zone',
                          'hr_zone_2': 'Duration in intense zone',
                          'hr_zone_3': 'Duration in maximal zone'}

        custom_data = self.polyConfig['customData']
        for user_id in custom_data.keys():
            access_token = custom_data[user_id]['access_token']
            # print("Access Token: " + access_token)
            withings = Withings(access_token)

            devices = withings.get_devices()
            for dev in devices['body']['devices']:
                node_name = dev['type']
                node_address = dev['deviceid'][-6:].lower()
                self.addNode(WithingsDeviceNode(self, self.address, node_address, node_name))
                time.sleep(1)

            # Create User ID Parent Nodes
            parent_address = str(user_id)[-3:]
            self.addNode(UserParentNode(self, parent_address, parent_address, "Withings User " + str(user_id)))
            time.sleep(1)

            # Create Measurement Nodes
            measures = withings.get_measure()
            for body in measures['body']['measuregrps']:
                for measure in body['measures'][-1]:
                    _type = measure['type']
                    if _type in measure_type_map:
                        type_label = measure_type_map[_type]
                        node_address = parent_address + str(_type).lower()
                        self.addNode(MeasureNode(self, parent_address, node_address, type_label))
                        time.sleep(2)
                    else:
                        print("Type Label Not Found")

            # Create Activity Nodes
            activities = withings.get_activities()
            for body in activities['body']['activities'][-1]:
                for act in body:
                    if act in activities_map:
                        act_label = activities_map[act]
                        node_address = parent_address + str(act).replace('_', '')[:8].lower()
                        self.addNode(MeasureNode(self, parent_address, node_address, act_label))
                        time.sleep(2)

    def delete(self):
        """
        Example
        This is sent by Polyglot upon deletion of the NodeServer. If the process is
        co-resident and controlled by Polyglot, it will be terminiated within 5 seconds
        of receiving this message.
        """
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        self.removeNoticesAll()
        self.addNotice('Hey there, my IP is {}'.format(self.poly.network_interface['addr']), 'hello')
        self.addNotice('Hello Friends! (without key)')
        default_user = "YourUserName"
        default_password = "YourPassword"
        if 'user' in self.polyConfig['customParams']:
            self.user = self.polyConfig['customParams']['user']
        else:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(self.user))
            st = False

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = default_password
            LOGGER.error(
                'check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            st = False
        # Make sure they are in the params
        self.addCustomParam({'password': self.password, 'user': self.user,
                             'some_example': '{ "type": "TheType", "host": "host_or_IP", "port": "port_number" }'})

        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password:
            # This doesn't pass a key to test the old way.
            self.addNotice('Please set proper user and password in configuration page, and restart this nodeserver')
        # This one passes a key to test the new way.
        self.addNotice('This is a test', 'test')

    def remove_notice_test(self, command):
        LOGGER.info('remove_notice_test: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNotice('test')

    def remove_notices_all(self):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        'REMOVE_NOTICE_TEST': remove_notice_test
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


class TemplateNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(TemplateNode, self).__init__(controller, primary, address, name)

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
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1, 2, 3, 4]

    id = 'templatenodeid'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


class WithingsDeviceNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(WithingsDeviceNode, self).__init__(controller, primary, address, name)

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
        self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'WITHINGS_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2},
               {'driver': 'BATLVL', 'value': 0, 'uom': 2}
               ]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


class UserParentNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(UserParentNode, self).__init__(controller, primary, address, name)

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
        self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'PARENT_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


class MeasureNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(MeasureNode, self).__init__(controller, primary, address, name)

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
        self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'MEASURE_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


class ActivityNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(ActivityNode, self).__init__(controller, primary, address, name)

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
        self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 2, 3, 4]

    id = 'ACTIVITY_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    commands = {
        'DON': setOn, 'DOF': setOff
    }


#
# class CallBackServer:
#     def __init__(self):
#         pass
#
#     def flask_server(self):
#         # print("-----------------------------------")
#         # print("httpsIngress: " + str(self.poly.init['netInfo']['httpsIngress']))
#         # print("publicIp: " + self.poly.init['netInfo']['publicIp'])
#         # print("-----------------------------------")
#         # httpsIngress = self.poly.init['netInfo']['httpsIngress']
#         # publicIp = self.poly.init['netInfo']['publicIp']
#
#         app = Flask(__name__)
#
#         @app.route("/test")
#         def hello():
#             print("----------------- Hello World ------------------")
#             return Response("{'a':'b'}", status=200, mimetype='application/json')
#
#         app.run(debug=True, use_reloader=False, host="0.0.0.0", port=3000)
#         # app.run(host="0.0.0.0", port=3000)
#         # app.debug = False
#         # threading.Thread(target=app.run(host="0.0.0.0", port=3000)).start()


class CallBackServer(BaseHTTPRequestHandler):
    LOGGER.info('Starting CallBack Server')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        LOGGER.info("=============== CallBack Server Test Line ======================")
        print(self.raw_requestline)

    # def do_POST(self):
    #     content_length = int(self.headers['Content-Length'])
    #     body = self.rfile.read(content_length)
    #     self.send_response(200)
    #     self.end_headers()
    #     response = BytesIO()
    #     # response.write(b'This is POST request. ')
    #     # response.write(b'Received: ')
    #     # response.write(body)
    #     # self.wfile.write(response.getvalue())
    #     # print(self.raw_requestline)
    #     # print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
    #     #         str(self.path), str(self.headers), body.decode('utf-8'))
    #     params = dict([p.split('=') for p in body.decode('utf-8').split('&')])
    #     control.add_nodes(params)

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Withings')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
        httpd = HTTPServer(('0.0.0.0', 3000), CallBackServer)
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
        polyglot.stop()
        sys.exit(0)

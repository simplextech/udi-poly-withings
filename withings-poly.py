#!/usr/bin/env python

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
import re
# from flask import Flask
# from flask import Response
# import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl
from withings import Withings
import copy
# from nodes import WithingsParentNode
# from nodes import WithingsDeviceNode
from nodes import *
# from nodes.withings_scale_node import WithingsScaleHRNode
import utils

LOGGER = polyinterface.LOGGER


class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Withings Controller'
        # self.poly.onConfig(self.process_config)
        self.server_data = {}
        self.access_token = None
        self.user_info = {}
        self.ingress = None
        self.disco = 0
        self.measure_type_map = {
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
        self.activities_map = {
            'steps': 'Steps',
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
            'hr_zone_3': 'Duration in maximal zone'
        }

    def start(self):
        self.setDriver('ST', 1)
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
        self.ingress = self.poly.init['netInfo']['httpsIngress']
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
        _scope = "user.info,user.metrics,user.activity,user.sleepevents"

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
            if self.get_token(oauth['code']):
                LOGGER.info("Withings OAuth Successful")
                self.discover()
            else:
                LOGGER.warn("Withings OAuth Failed")
        else:
            print(oauth)

    def get_token(self, code):
        _state = None

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
                                            'expires_in': expires_in,
                                            'user_id': user_id}

                    # print("Get Token End----------------------------------")
                    # print(custom_data)
                    # print("Get Token End----------------------------------")

                    self.saveCustomData(custom_data)
                    _state = True
                    return True
                except KeyError as ex:
                    LOGGER.error("get_token Error: " + str(ex))
            else:
                _state = False
                return False
        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))

        if _state:
            LOGGER.debug("---------------Get Token Complete -----------------------")
            self.discover()
        else:
            return False

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
                    _user_id = resp['userid']

                    custom_data[user_id] = {'access_token': access_token,
                                            'refresh_token': refresh_token,
                                            'expires_in': expires_in,
                                            'user_id': _user_id}

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
            self.withings_update()

    def longPoll(self):
        LOGGER.debug('longPoll')
        self.refresh_token()

    def query(self, command=None):
        self.withings_update()
        # self.check_params()
        # for node in self.nodes:
        #     self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        custom_data = self.polyConfig['customData']
        for user_id in custom_data.keys():
            access_token = custom_data[user_id]['access_token']
            withings = Withings(access_token, self.ingress)
            devices = withings.get_devices()
            measures = withings.get_measure()
            activities = withings.get_activities()
            sleep = withings.get_sleep_summary()

            # Create User ID Parent Nodes
            parent_address = str(user_id).replace('0', '')[-3:]
            self.addNode(WithingsParentNode(self, parent_address, parent_address, "Withings User " + str(user_id)))

            if devices is not None:
                for dev in devices['body']['devices']:
                    node_name = dev['type']
                    dev_type = dev['type']
                    model_id = dev['model_id']
                    node_address = parent_address + dev['deviceid'][-3:].lower()

                    if dev_type == "Scale":
                        if model_id == 6:
                            self.addNode(WithingsScaleHRNode(self, parent_address, node_address,
                                                             node_name, devices, measures))
                            time.sleep(2)
                        else:
                            self.addNode(WithingsScaleNode(self, parent_address, node_address,
                                                           node_name, devices, measures))
                            time.sleep(2)

                    if dev_type == "Activity Tracker":
                        if model_id == 59:
                            self.addNode(
                                WithingsActivityTrackerNode(
                                    self, parent_address, node_address, node_name, devices, activities)
                            )
                            time.sleep(2)

                            self.addNode(
                                WithingsActivityTrackerHRNode(
                                    self, parent_address, node_address + "hr", node_name + " HR", devices, activities)
                            )
                            time.sleep(2)

                            self.addNode(
                                WithingsActivityTrackerSleepHRNode(
                                    self, parent_address, node_address + "sl", node_name + " Sleep", devices, sleep)
                            )
                            time.sleep(2)
                        else:
                            self.addNode(
                                WithingsActivityTrackerNode(
                                    self, parent_address, node_address, node_name, devices, activities)
                            )
                            time.sleep(2)

                            self.addNode(
                                WithingsActivityTrackerSleepNode(
                                    self, parent_address, node_address + "sl", node_name + " Sleep", devices, sleep)
                            )
                            time.sleep(2)

                    if dev_type == "Blood Pressure Monitor":
                        self.addNode(
                            WithingsBPMNode(self, parent_address, node_address, node_name, devices, measures)
                        )
                        time.sleep(2)

                    if dev_type == "Sleep Monitor":
                        self.addNode(
                            WithingsSleepNode(self, parent_address, node_address, node_name, devices, sleep)
                        )
                        if withings.subscribe_bed_in():
                            LOGGER.info("Subscribe Bed-In Success")
                        else:
                            LOGGER.info("Subscribe Bed-In Error")

                        if withings.subscribe_bed_out():
                            LOGGER.info("Subscribe Bed-Out Success")
                        else:
                            LOGGER.info("Subscribe Bed-Out Error")

                        time.sleep(2)

            time.sleep(3)
        self.disco = 1

    def withings_update(self):
        custom_data = self.polyConfig['customData']
        for user_id in custom_data.keys():
            access_token = custom_data[user_id]['access_token']
            print(user_id, access_token)
            withings = Withings(access_token, self.ingress)
            devices = withings.get_devices()
            measures = withings.get_measure()
            activities = withings.get_activities()
            sleep = withings.get_sleep_summary()

            parent_address = str(user_id).replace('0', '')[-3:]
            for node in self.nodes:
                if self.nodes[node].address != "controller":
                    pattern = '^' + parent_address
                    node_address = self.nodes[node].address
                    re_result = re.match(pattern, node_address)
                    if re_result:
                        print("Node: " + self.nodes[node].address)
                        self.nodes[node].query(command=[devices, measures, activities, sleep])
                    else:
                        pass
                    time.sleep(2)
            print("Updated: " + str(user_id))
            time.sleep(3)

    def delete(self):
        LOGGER.info('Removing Withings Nodeserver')

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
        # 'REMOVE_NOTICES_ALL': remove_notices_all,
        # 'REMOVE_NOTICE_TEST': remove_notice_test
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


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

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        LOGGER.info("=============== CallBack Server Test Line ======================")
        print(self.raw_requestline)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        LOGGER.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))
        # params = dict([p.split('=') for p in post_data.decode('utf-8').split('&')])
        # print(params)
        print("-----Requests-----")
        print(self.raw_requestline)
        print(self.request)
        print(self.requestline)
        print(post_data)
        # params = parse_qsl(urlparse(self.raw_requestline).params)
        # params = parse_qsl(urlparse(self.request).query)

        print(params)

        self._set_response()
        # self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        #
        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)
        # self.send_response(200)
        # self.end_headers()
        # # response = BytesIO()
        # # response.write(b'This is POST request. ')
        # # response.write(b'Received: ')
        # # response.write(body)
        # # self.wfile.write(response.getvalue())
        # # print(self.raw_requestline)
        # # print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        # #         str(self.path), str(self.headers), body.decode('utf-8'))
        # params = dict([p.split('=') for p in body.decode('utf-8').split('&')])
        # print(params)


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
        httpd.server_close()
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
        polyglot.stop()
        sys.exit(0)

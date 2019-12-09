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

LOGGER = polyinterface.LOGGER


class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Withings Controller'
        self.poly.onConfig(self.process_config)
        self.server_data = {}
        self.access_token = None

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

        try:
            r = requests.post(_token_url, headers=headers, data=payload)
            if r.status_code == requests.codes.ok:
                try:
                    resp = r.json()
                    print(resp)
                    access_token = resp['access_token']
                    refresh_token = resp['refresh_token']
                    expires_in = resp['expires_in']
                    user_id = resp['userid']

                    cust_data = {'access_token': access_token,
                                 'refresh_token': refresh_token,
                                 'expires_in': expires_in,
                                 'user_id': user_id
                                 }

                    self.saveCustomData(cust_data)
                    self.access_token = access_token
                    self.remove_notices_all()
                    # print(cust_data)
                    return True
                except KeyError as ex:
                    LOGGER.error("get_token Error: " + str(ex))
            else:
                return False
        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))

    def refresh_token(self):
        if 'refresh_token' in self.polyConfig['customData']:
            _token_url = "https://account.withings.com/oauth2/token"

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            payload = {"grant_type": "refresh_token",
                       "client_id": self.server_data['clientId'],
                       "client_secret": self.server_data['clientSecret'],
                       "refresh_token": self.polyConfig['customData']['refresh_token']
                       }

            try:
                r = requests.post(_token_url, headers=headers, data=payload)
                if r.status_code == requests.codes.ok:
                    try:
                        resp = r.json()
                        print(resp)
                        access_token = resp['access_token']
                        refresh_token = resp['refresh_token']
                        expires_in = resp['expires_in']
                        user_id = resp['userid']

                        cust_data = {'access_token': access_token,
                                     'refresh_token': refresh_token,
                                     'expires_in': expires_in,
                                     'user_id': user_id
                                     }

                        self.saveCustomData(cust_data)
                        self.access_token = access_token
                        return True
                    except KeyError as ex:
                        LOGGER.error("get_token Error: " + str(ex))
                else:
                    return False
            except requests.exceptions.RequestException as e:
                LOGGER.error("Error: " + str(e))
        else:
            return False

    def shortPoll(self):
        LOGGER.debug('shortPoll')

    def longPoll(self):
        LOGGER.debug('longPoll')

    def query(self, command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # self.addNode(TemplateNode(self, self.address, 'templateaddr', 'Template Node Name'))
        if 'access_token' in self.polyConfig['customData']:
            if self.polyConfig['customData']['access_token'] == self.access_token:
                access_token = self.polyConfig['customData']['access_token']
            else:
                access_token = self.access_token

            withings = Withings(access_token)

            devices = withings.get_devices()
            print(devices)
            if devices is not None:
                for dev in devices['body']['devices']:
                    print(dev['type'])
                    print(dev['battery'])
                    print(dev['deviceid'])
                    name = dev['type']
                    naddr = dev['deviceid'][-12:].lower()
                    print(name)
                    print(naddr)
                    self.addNode(WithingsDeviceNode(self, self.address, naddr, name))
            else:
                print(devices)

            # activities map
            activities_map = [
                                {"steps", "Steps"},
                                {"distance", "Distance in Steps"},
                                {"elevation", "Elevation"},
                                {"soft", "Light Activity"},
                                {"moderate", "Moderate Activity"},
                                {"intense", "Intense Activity"},
                                {"active", "Active Activity"},
                                {"calories", "Activity Calories Used"},
                                {"totalcalories", "Total Calories Used"}
                                ]

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

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1, 2, 3, 4]

    id = 'WITHINGS_NODE'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2},
               {'driver': 'BATLVL', 'value': 0, 'uom': 2}
               ]

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

# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import json
from typing import Optional, Literal, List
from thingsboard.common.core.threaded import Threaded
from configobj import ConfigObj
import websockets.sync.client as websocket_client


class ThingsboardMonitorEndpointObserver(Threaded):
    """Allows to get telemetry changes from an Endpoint.

    Uses internally a WebSocket to subscribe to telemetry changes.
    """
    log = logging.getLogger(__name__)

    def __init__(self, config_file=None, *args, **kwargs):
        super(ThingsboardMonitorEndpointObserver, self).__init__(*args, **kwargs)

        self._config = None                                 # type: ConfigObj or None
        self._websocket = None                              # type: websocket_client.ClientConnection or None
        self._token = None
        self._cmdId = 0
        self._on_telemetry_update_callback = None
        self._is_ready = False

        if config_file:
            self._config = self.parse_config_file(config_file)

            host = self._config['websocket'].get('host', 'ws://localhost')
            port = str(self._config['websocket'].get('port', '8080'))
            path = self._config['websocket'].get('path', '/api/ws')
            uri = host + ':' + port + path

            try:
                self._websocket = websocket_client.connect(uri=uri)
                self.log.info('WebSocket connected')

                self.log.info('Requesting JWT...')
                success, self._token = self.get_jwt_session_token()
                if success:
                    self.log.info(f'Successfully received JWT ({self._token[:8]}...)')
                else:
                    self.log.error('Could not receive a JWT!')
            except Exception as e:
                self.log.exception(e, stack_info=True)

    def parse_config_file(self, config_file) -> ConfigObj:
        from thingsboard.common.utils import path_helpers

        config = None

        path_config_file = path_helpers.prettify(config_file)

        if path_config_file and os.path.isfile(path_config_file):
            config = ConfigObj(path_config_file)

        if config:
            # Check if most important configuration parameters are present
            assert 'thingsboard' in config, 'Missing group \'thingsboard\' in config file!'

            assert 'host' in config['thingsboard'], 'Missing \'host\' parameter in thingsboard group!'
            if 'port' not in config['thingsboard']:
                self.log.warning('\'port\' parameter in \'thingsboard\' group missing!')
            assert 'username' in config['thingsboard'], 'Missing \'username\' parameter in thingsboard group!'
            assert 'password' in config['thingsboard'], 'Missing \'password\' parameter in thingsboard group!'

            assert 'websocket' in config, 'Missing group \'websocket\' in config file!'

            assert 'host' in config['websocket'], 'Missing \'host\' parameter in thingsboard group!'
            if 'port' not in config['websocket']:
                self.log.warning('\'port\' parameter in \'websocket\' group missing!')
            if 'path' not in config['websocket']:
                self.log.warning('\'path\' parameter in \'websocket\' group missing!')
        else:
            sys.exit('Error reading config file!')

        return config

    @property
    def config(self):
        return self._config

    @property
    def is_ready(self):
        return self._is_ready

    def set_on_telemetry_update_callback(self, callback_method):
        self._on_telemetry_update_callback = callback_method

    def start(self, thread_name: str=None):

        if thread_name is None:
            thread_name = __name__

        # Setup and start internal thread
        self.setup_thread(name=thread_name)
        self.start_thread()

    def wait_until_ready(self):
        while not self.is_ready:
            time.sleep(0.2)

    def stop(self):
        self._websocket.close()
        self.wakeup_thread()
        self.stop_thread()

    def _run(self):
        self.authenticate_session()
        self._is_ready = True

        # device_id = self._config['angrybird']['deviceid']
        # self.subscribe_device_latest_telemetry(device_id)

        while self._thread_should_run:

            if self._websocket:
                message = None
                try:
                    message = self._websocket.recv()
                except Exception as e:
                    self.log.exception(e, stack_info=True)

                if message:
                    self.log.debug(f"Message received: {message}")

                    # Decode message JSON message to check for error
                    try:
                        parsed_message = json.loads(message)
                        if 'errorCode' in parsed_message and parsed_message['errorCode'] != 0:
                            self.log.warning(f"Error received: {parsed_message['errorMsg']}")
                            # When getting errorCode == 1 (Failed to fetch data!) it might be
                            # because the user is not a 'TENANT_ADMIN' nor 'CUSTOMER_USER' or
                            # the device is not accessible by this user!
                    except json.JSONDecodeError:
                        self.log.error("Received non-JSON message!")
                    except Exception as e:
                        self.log.exception(e, stack_info=True)

                    # Forward message to the upper layer
                    if self._on_telemetry_update_callback:
                        self._on_telemetry_update_callback(content=None, message=message)

            # Wait until next interval begins
            # if self._thread_should_run:
            #    self._thread_sleep_interval()

        self._thread_left_run_loop = True

    def get_jwt_session_token(self):
        import requests

        success = False
        token = "YOUR_JWT_TOKEN"

        host = self._config['thingsboard'].get('host', 'http://localhost')
        port = str(self._config['thingsboard'].get('port', '8080'))
        path = self._config['thingsboard'].get('path', '/api/auth/login')

        # API endpoint
        url = host + ':' + port + path

        # Headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Request payload
        data = {
            # Needs to be a 'TENANT_ADMIN' or 'CUSTOMER_USER' authority
            "username": self._config['thingsboard'].get('username', 'tenant@thingsboard.org'),
            "password": self._config['thingsboard'].get('password', 'tenant')
        }

        # Make the POST request
        response = requests.post(url, headers=headers, json=data)

        # Print the response
        self.log.debug(f"Status Code: {response.status_code}")
        self.log.debug(f"Response Headers: {response.headers}")
        self.log.debug(f"Response Body: {response.text}")

        # If you want to work with JSON response
        try:
            response_json = response.json()
            self.log.debug(f"JSON Response: {response_json}")
            token = response_json["token"]
            success = True
        except json.JSONDecodeError:
            self.log.debug("Response is not valid JSON")

        return success, token

    def _send(self, message_object):
        data = json.dumps(message_object)
        self._websocket.send(data)
        self.log.debug(f"Message sent: {data}")

    def authenticate_session(self):
        """Authenticate session using the received JWT token.

        Note: Needs to be done within 10 seconds after WebSocket connection!
        """
        message_object = {
            "authCmd": {
                "cmdId": self._cmdId,
                "token": self._token
            }
        }

        self._cmdId = self._cmdId + 1

        self._send(message_object)

    def subscribe_device_latest_telemetry(self, device_id: str, command_id: Optional[int] = None):

        if command_id is None:
            command_id = self._cmdId
            self._cmdId = self._cmdId + 1

        # Prepare the message object
        message_object = {
            "cmds": [
                {
                    "entityType": "DEVICE",
                    "entityId": device_id,
                    "scope": "LATEST_TELEMETRY",
                    "cmdId": command_id,
                    "type": "TIMESERIES"
                }
            ]
        }

        self._send(message_object)

        return command_id

    def subscribe_device_attributes(self, device_id: str,
                                    scope: str = Literal['SERVER_SCOPE', 'SHARED_SCOPE', 'CLIENT_SCOPE'],
                                    command_id: Optional[int] = None):
        if command_id is None:
            command_id = self._cmdId
            self._cmdId = self._cmdId + 1

        # Prepare the message object
        message_object = {
            "cmds": [
                {
                    "entityType": "DEVICE",
                    "entityId": device_id,
                    "scope": scope,
                    "cmdId": command_id,
                    "type": "ATTRIBUTES"
                }
            ]
        }

        self._send(message_object)

        return command_id

    def request_device_telemetry_history(self,
                                         device_id: str,
                                         keys: str,     # String with comma separated keys
                                         start_time_ms: int,
                                         end_time_ms: int,
                                         command_id: Optional[int] = None):
        """Request telemetry data based on a start and end timestamp.

        The start and end timestamp must be in milliseconds UTC time.

        Note: The start time needs to be smaller (more in the past) than the end time!
        """
        if command_id is None:
            command_id = self._cmdId
            self._cmdId = self._cmdId + 1

        if start_time_ms >= end_time_ms:
            self.log.warning("Parameter 'end_time_ms' should be bigger than 'start_time_ms'!")

        # Prepare the message object
        message_object = {
            "cmds": [
                {
                    "entityType": "DEVICE",
                    "entityId": device_id,
                    "cmdId": command_id,
                    "type": "TIMESERIES_HISTORY",
                    "keys": keys,
                    "startTs": start_time_ms,
                    "endTs": end_time_ms
                }
            ]
        }

        self._send(message_object)

        return command_id

    def request_device_telemetry_history_latest(self,
                                                device_id: str,
                                                keys: str,      # String with comma separated keys
                                                latest_x_seconds: int,
                                                end_time_ms: Optional[int] = None,
                                                command_id: Optional[int] = None):
        """Request most recent x seconds telemetry data.

        Note: The end_time_ms is calculated using your computers time. It may be
              different from the time on the ThingsBoard server!
        """
        from thingsboard.common.utils import datetime_helpers

        if end_time_ms is None:
            end_time_ms = datetime_helpers.get_current_timestamp()
        start_time_ms = end_time_ms - (latest_x_seconds * 1000)
        return self.request_device_telemetry_history(device_id=device_id,
                                                     keys=keys,
                                                     start_time_ms=start_time_ms,
                                                     end_time_ms=end_time_ms,
                                                     command_id=command_id)

# -*- coding: utf-8 -*-

import os
import sys
import logging

from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException
from thingsboard.common.utils import path_helpers
from .endpoint import ThingsboardMonitorEndpoint


class ThingsboardMonitorApp(object):
    """Allows to connect to ThingsBoard as client application and to communicate with endpoints (devices).

    """
    log = logging.getLogger(__name__)

    def __init__(self, config_file=None, *args, **kwargs):
        super(ThingsboardMonitorApp, self).__init__(*args, **kwargs)
        self._client = None         # type: RestClientCE or None
        self._endpoint = {}         # type: dict[str, ThingsboardMonitorEndpoint]
        self._appName = __name__

        ThingsboardMonitorEndpoint._app = self

        if config_file:
            config = self.parse_config_file(config_file)

            port = str(config['thingsboard'].get('port', '8080'))
            base_url = config['thingsboard']['host'] + ':' + port

            self._client = RestClientCE(base_url=base_url)

            try:
                self._client.login(username=config['thingsboard']['username'],
                                   password=config['thingsboard']['password'])
            except ApiException as e:
                self.log.exception(e)

    def parse_config_file(self, config_file):
        from configobj import ConfigObj

        config = None

        path_config_file = path_helpers.prettify(config_file)

        if path_config_file and os.path.isfile(path_config_file):
            config = ConfigObj(path_config_file)

        if config:
            # Check if most important configuration parameters are present
            assert 'thingsboard' in config, 'Missing group \'thingsboard\' in config file!'

            assert 'host' in config['thingsboard'], 'Missing \'host\' parameter in thingsboard group!'
            if 'port' not in config['thingsboard']:
                self.log.warning('\'port\' parameter in config file missing!')
            if 'cert' not in config['thingsboard']:
                self.log.warning('\'cert\' parameter in config file missing!')
            assert 'username' in config['thingsboard'], 'Missing \'username\' parameter in thingsboard group!'
            assert 'password' in config['thingsboard'], 'Missing \'password\' parameter in thingsboard group!'
        else:
            sys.exit('Error reading config file!')

        return config

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._appName

    def add_endpoint(self, name: str, thingsboard_device_id) -> ThingsboardMonitorEndpoint:
        self._endpoint[name] = ThingsboardMonitorEndpoint(name, thingsboard_device_id)
        return self._endpoint[name]

    def set_endpoint_parameter(self, endpoint_name: str, parameter_name: str, parameter_value) -> bool:
        if endpoint_name in self._endpoint:
            return self._endpoint[endpoint_name].set_endpoint_parameter(parameter_name, parameter_value)
        return False

    def set_node_parameter(self, endpoint_name: str, node_name: str, parameter_name: str, parameter_value) -> bool:
        if endpoint_name in self._endpoint:
            return self._endpoint[endpoint_name].set_endpoint_parameter(parameter_name, parameter_value,
                                                                        node_name=node_name)
        return False

    def set_server_parameter(self, endpoint_name: str, parameter_name: str, parameter_value) -> bool:
        if endpoint_name in self._endpoint:
            return self._endpoint[endpoint_name].set_server_parameter(parameter_name, parameter_value)
        return False

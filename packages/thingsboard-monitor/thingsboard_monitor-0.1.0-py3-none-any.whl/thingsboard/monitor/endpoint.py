# -*- coding: utf-8 -*-

import logging
from tb_rest_client.rest_client_ce import *
from .node import ThingsboardMonitorNode


# noinspection PyPackageRequirements
class ThingsboardMonitorEndpoint(object):
    """ Represents an Endpoint/Device on the application side.

    Used to communicate over the cloud (Thingsboard) to the real Endpoint.
    """
    log = logging.getLogger(__name__)
    _app = None     # ThingsboardMonitorApp

    def __init__(self, name, thingsboard_device_id):
        self._endPointName = name
        self._thingsboardDeviceId = thingsboard_device_id

        self._node = {}  # dict[str, ThingsboardMonitorNode]

    def add_node(self, node_name) -> ThingsboardMonitorNode:
        self._node[node_name] = ThingsboardMonitorNode(node_name=node_name,
                                                       endpoint=self)
        return self._node[node_name]

    def set_endpoint_parameter(self, parameter_name, parameter_value, node_name: Optional[str] = None, backtrace=True):
        """Changes the parameter of an endpoint or a node inside the endpoint.

        This is achieved by sending a ThingsBoard shared attribute.

        To be able the backtrace parameter settings by applications the change is logged as telemetry
        in a timeseries.
        """
        key_node_name = ''

        if node_name:
            # Check if node is present in endpoint
            node = self._node[node_name]

            if node:
                key_node_name = node_name + '/'
        else:
            self.log.warning(f'Could find associated node {node_name}!')
            return

        # Send the parameter as ThingsBoard attribute
        key_name = 'set/' + key_node_name + 'parameter/' + parameter_name
        body = {
            key_name: parameter_value
        }
        self._app.client.save_device_attributes(device_id=DeviceId(self._thingsboardDeviceId, 'DEVICE'),
                                                scope='SHARED_SCOPE',
                                                # 'SERVER_SCOPE', 'CLIENT_SCOPE' , 'SHARED_SCOPE'
                                                body=body)

        if backtrace:
            # Send the parameter change as Thingsboard telemetry to have a history/backtrace
            key_name = key_name + '/from/' + self._app.name
            body = {
                key_name: parameter_value
            }
            self._app.client.save_entity_telemetry(entity_id=EntityId(self._thingsboardDeviceId, 'DEVICE'),
                                                   scope='ANY',  # Not used (deprecated)
                                                   body=body)

    def set_server_parameter(self, parameter_name, parameter_value):
        """Sends an attribute to the cloud.

        This parameter does not get relayed to the endpoint, hence can be seen by the server, but not by the endpoint!

        This is achieved by sending a ThingsBoard server attribute.
        """
        key_name = self._app.name + '/' + parameter_name
        body = {
            key_name: parameter_value
        }
        self._app.client.save_device_attributes(device_id=DeviceId(self._thingsboardDeviceId, 'DEVICE'),
                                                scope='SERVER_SCOPE',
                                                body=body)

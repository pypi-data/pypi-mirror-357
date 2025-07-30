# -*- coding: utf-8 -*-

class ThingsboardMonitorNode(object):
    """ Represents a Node (living inside an endpoint) on the application side.

    Nodes are used to split the content of an endpoint into different groups.
    """
    def __init__(self, node_name, endpoint):
        super(ThingsboardMonitorNode, self).__init__()
        self._nodeName = node_name
        self._endpoint = endpoint

    @property
    def name(self):
        return self._nodeName

    def set_parameter(self, parameter_name, parameter_value):
        self._endpoint.set_endpoint_parameter(node_name=self._nodeName,
                                              parameter_name=parameter_name,
                                              parameter_value=parameter_value)

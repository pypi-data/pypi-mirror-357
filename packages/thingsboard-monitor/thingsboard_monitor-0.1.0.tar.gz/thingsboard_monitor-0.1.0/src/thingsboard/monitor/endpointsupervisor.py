import logging
import json
from collections.abc import Callable
from thingsboard.monitor.endpointobserver import ThingsboardMonitorEndpointObserver


class ThingsboardMonitorEndpointSupervisor(ThingsboardMonitorEndpointObserver):
    """Allows to monitor attributes of an Endpoint.

    It allows to subscribe to 'shared', 'server' and 'client' attribute updates allowing
    to get the actual values of the attributes right after subscription and attribute updates
    when
    """
    log = logging.getLogger(__name__)

    def __init__(self, device_id: str, config_file=None, autostart=True, *args, **kwargs):
        super(ThingsboardMonitorEndpointSupervisor, self).__init__(config_file=config_file, *args, **kwargs)

        self._device_id = device_id         # type: str
        self._callback_method = dict()      # type: dict[int, Callable[[dict], None]]

        # Register callback method to receive all messages received by the WebSocket
        self.set_on_telemetry_update_callback(self._on_message_received)

        if autostart:
            self.start()

    @property
    def device_id(self):
        return self._device_id

    def start(self, wait_until_ready=True):
        super(ThingsboardMonitorEndpointSupervisor, self).start(thread_name=__name__)
        if wait_until_ready:
            super(ThingsboardMonitorEndpointSupervisor, self).wait_until_ready()

    def subscribe_device_shared_attribute_changes(self, callback_method: Callable[[dict], None]):
        if not self.is_ready:
            return False

        command_id = 33

        if command_id not in self._callback_method:
            # Subscribe to client attribute changes
            cmd_id = self.subscribe_device_attributes(
                device_id=self._device_id,
                scope='SHARED_SCOPE',
                command_id=command_id
            )

            self._callback_method[cmd_id] = callback_method
            return True
        return False

    def subscribe_device_server_attribute_changes(self, callback_method: Callable[[dict], None]) -> bool:
        if not self.is_ready:
            return False

        command_id = 44

        if command_id not in self._callback_method:
            # Subscribe to server attribute changes
            cmd_id = self.subscribe_device_attributes(
                device_id=self._device_id,
                scope='SERVER_SCOPE',
                command_id=command_id
            )

            self._callback_method[cmd_id] = callback_method
            return True
        return False

    def subscribe_device_client_attribute_changes(self, callback_method: Callable[[dict], None]):
        if not self.is_ready:
            return False

        command_id = 55

        if command_id not in self._callback_method:
            # Subscribe to client attribute changes
            cmd_id = self.subscribe_device_attributes(
                device_id=self._device_id,
                scope='CLIENT_SCOPE',
                command_id=command_id
            )

            self._callback_method[cmd_id] = callback_method
            return True
        return False

    def _on_message_received(self, content: str, message: str):
        try:
            parsed_message = json.loads(message)
            if 'errorCode' in parsed_message and parsed_message['errorCode'] == 0:
                if parsed_message['subscriptionId'] in self._callback_method:
                    # Forward message to registered callback method
                    self._callback_method[parsed_message['subscriptionId']](parsed_message)
                else:
                    self.log.warning(f'No registered delivery path for received message: {parsed_message}')
        except json.JSONDecodeError:
            self.log.error("Received non-JSON message!")
        except Exception as e:
            self.log.exception(e, stack_info=True)

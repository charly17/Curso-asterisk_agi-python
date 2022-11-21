import pystrix
import logging
from asgiref.sync import async_to_sync
from pystrix.ami.ami import _Request, _Aggregate
from channels.layers import get_channel_layer
from Fastagi.settings import AMI_HOST, AMI_USER, AMI_PASSWD, AMI_PORT

channel_layer = get_channel_layer()


class AMIAsterisk():

    def __init__(self):
        self._ami = pystrix.ami.Manager()
        self._ami.connect(host=AMI_HOST, port=int(AMI_PORT))
        self._register_callbacks()
        challenge_response = self.execute(
            pystrix.ami.core.Challenge()
        )

        if challenge_response and challenge_response.success:
            action = pystrix.ami.core.Login(
                AMI_USER, AMI_PASSWD,
                challenge=challenge_response.result['Challenge']
            )
            self.execute(action)
        else:
            self._kill_flag = True
            logging.error(
                'Asterisk did not provide an MD5 challenge token' +
                (challenge_response is None and ': timed out' or '')
            )
        self._ami.monitor_connection()

    def _register_callbacks(self):
        self._ami.register_callback(
            '', self.show_events
        )

    def execute(self, action):
        try:
            return self._ami.send_action(action)
        except pystrix.ami.ManagerSocketError as e:
            self._kill_flag = True
            logging.error(
                f'Unable to connect to Asterisk server: {e}'
            )
        except pystrix.ami.core.ManagerAuthError as reason:
            self._kill_flag = True
            logging.error(
                f'Unable to authenticate to Asterisk server: {reason}'
            )
        except pystrix.ami.ManagerError as reason:
            self._kill_flag = True
            logging.error(
                f'An unexpected Asterisk error occurred: {reason}'
            )

    def get_command_list(self):
        return self.execute(pystrix.ami.core.ListCommands())

    def get_iax_peers(self):
        return self.execute(IAXPeers())

    def make_call(self, channel, context, extension, priority):
        return self.execute(
            pystrix.ami.core.Originate_Context(
                channel, context, extension, priority
            )
        )

    def show_events(self, event, manager):
        if hasattr(event, '_name'):
            if event._name == 'IAXPeers_Aggregate':
                async_to_sync(
                    channel_layer.group_send
                )('ami_socket',
                    {
                        'type': 'send_message',
                        'message': {
                            'action': 'iax_peers',
                            'event': event[pystrix.ami.core_events.PeerEntry]},
                    }
                  )
        event_name = event.get('Event', False)
        logging.warning(event_name)
        logging.warning(event_name == 'DeviceStateChange')
        if event_name == 'DeviceStateChange':
            async_to_sync(
                channel_layer.group_send
            )('ami_socket',
                {
                    'type': 'send_message',
                    'message': event,
                }
              )


class IAXPeersAggregate(_Aggregate):
    _name = 'IAXPeers_Aggregate'

    _aggregation_members = (
        pystrix.ami.core_events.PeerEntry,
    )
    _aggregation_finalisers = (
        pystrix.ami.core_events.PeerlistComplete,
    )

    def _evaluate_action_id(self, event):
        if self._action_id == event.action_id or event['Event'] == 'PeerEntry':
            return True
        return False


class IAXPeers(_Request):
    aggregate = True
    _aggregates = (
        IAXPeersAggregate,
    )

    def __init__(self):
        _Request.__init__(self, "IAXpeers")

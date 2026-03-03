import pystrix
import logging
from datetime import datetime

# Configuración del logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='asterisk_manager.log',
                    filemode='a')  # 'a' para añadir al archivo existente

# También mostrar logs en la consola
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

AMI_HOST = '198.58.111.115'
AMI_USER = 'asteriskami1'
AMI_PASSWD = 'inbtel-2025ñ'
AMI_PORT = '5038'

class AMIAsterisk:
    def __init__(self):
        self._ami = pystrix.ami.Manager()
        try:
            self._ami.connect(host=AMI_HOST, port=int(AMI_PORT))
            self._register_callbacks()
            challenge_response = self.execute(pystrix.ami.core.Challenge())
            if challenge_response and challenge_response.success:
                action = pystrix.ami.core.Login(AMI_USER, AMI_PASSWD, challenge=challenge_response.result['Challenge'])
                self.execute(action)
            else:
                logging.error('Asterisk did not provide an MD5 challenge token' + (challenge_response is None and ': timed out' or ''))
            self._ami.monitor_connection()
        except Exception as e:
            logging.error(f"Failed to initialize AMI connection: {e}", exc_info=True)

    def _register_callbacks(self):
        self._ami.register_callback(pystrix.ami.core_events.Reload, self.reload_events)
        self._ami.register_callback(pystrix.ami.core_events.CoreShowChannel, self.core_show_channels_events)
        self._ami.register_callback('', self.show_events)

    def execute(self, action):
        try:
            return self._ami.send_action(action)
        except pystrix.ami.ManagerSocketError as e:
            logging.error(f'Unable to connect to Asterisk server: {e}', exc_info=True)
        except pystrix.ami.core.ManagerAuthError as reason:
            logging.error(f'Unable to authenticate to Asterisk server: {reason}', exc_info=True)
        except pystrix.ami.ManagerError as reason:
            logging.error(f'An unexpected Asterisk error occurred: {reason}', exc_info=True)

    def core_show_channels_events(self, event, manager):
        logging.info(f'CoreShowChannels event received: {event}')

    def reload_events(self, event, manager):
        logging.info(f'Reload event received: {event}')

    def show_events(self, event, manager):
        event_name = event.get('Event', False)
        if event_name == 'DialState':
            logging.info(f'DialState event: {event}')
        elif event_name == 'DialEnd':
            logging.info('Starting recording')
            action = MixMonitor(event['Channel'], f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.wav')
            manager.send_action(action)
            logging.info(f'DialEnd event: {event}')
        elif event_name == 'SoftHangupRequest':
            logging.info('Stopping recording')
            manager.send_action(pystrix.ami.core.StopMonitor(event['Channel']))
            logging.info(f'SoftHangupRequest event: {event}')

class MixMonitor(pystrix.ami.ami._Request):
    def __init__(self, channel, filename):
        super().__init__('MixMonitor')
        self['Channel'] = channel
        self['File'] = filename
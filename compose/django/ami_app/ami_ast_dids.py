import pystrix
import logging
from datetime import datetime
from Fastagi.settings import AMI_HOST, AMI_USER, AMI_PASSWD, AMI_PORT

_HOST = 'localhost'
_USERNAME = 'admin'
_PASSWORD = 'inbtel-2025ñ'

""" # Configura tu cliente Pystrix
ari_url = 'http://localhost:8088/ari'
username = 'asterisk_user'
password = 'asterisk_password'

client = pystrix(ari_url, username, password)

# Ejecuta el comando de recarga del dialplan
response = client.execute("dialplan reload")

if response.status == 200:
    print("Dialplan recargado exitosamente.")
else:
    print(f"Error al recargar el dialplan: {response.status}")
 """


class AMIAsterisk():

    def __init__(self):
        self._ami = pystrix.ami.Manager()
        self._ami.connect(host=AMI_HOST, port=int(AMI_PORT))
        # Registramos los callbacks con los que llamamos a las funciones
        self._register_callbacks()
        # Se genera un challenge para la autenticación
        challenge_response = self.execute(
            pystrix.ami.core.Challenge()
        )

        # Se genera un challenge para la autenticación
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

    # Declaramos una función para registrar los callbacks, AQUI ESCUCHAMOS LOS EVENTOS  de asterisk.
    def _register_callbacks(self):
        # La estructura para registrar un callback es la siguiente"Llamamos la funcion register_callback":
        self._ami.register_callback(
            # Indicamos el evento que queremos escuchar, este se encuentra en el modulo pystrix como parte de los eventos de AMI
            pystrix.ami.core_events.Reload,
            # Le damos un nombre a nuestra funcion la cual se desarrollara mas abajo
            self.reload_events
        )
        self._ami.register_callback(
            pystrix.ami.core_events.CoreShowChannel,
            self.core_show_channels_events
        )
        # Registramos un callback para capturar todos los eventos y los asociamos a una función (show_events)
        self._ami.register_callback(
            '', self.show_events
        )


    # Los actions son los comandos que se envian a asterisk y se realizan mediante esta funcion.
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

    def core_show_channels_events(self, event, manager):
        logging.error(f'core_show_channels events {event}')

    def reload_events(self, event, manager):
        logging.error(f'reload events {event}')

    # La funcion definida en la clase AMIAsterisk (register_callback) y que se asocia a la función show_events se declara aqui.
    def show_events(self, event, manager):
        event_name = event.get('Event', False)
        if 'DialState' == event_name:
            logging.warning(f'DialState events {event}')
        if 'DialEnd' == event_name:
            logging.warning(event)
            logging.warning('iniciamos grabación')
            # action = pystrix.ami.core.Monitor(
            #     event['Channel'],
            #     datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
            #     mix=True
            # )
            action = MixMonitor(
                event['Channel'],
                f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.wav'
            )
            logging.warning(action)
            manager.send_action(action)
            logging.warning(f'general events {event}')
        if 'SoftHangupRequest' == event_name:
            logging.warning('detenemos grabación')
            manager.send_action(
                pystrix.ami.core.StopMonitor(
                    event['Channel']
                )
            )
            logging.warning(f'general events {event}')

    def get_command_list(self):
        return self.execute(pystrix.ami.core.ListCommands())

    def make_call(self, channel, context, extension, priority):
        return self.execute(
            pystrix.ami.core.Originate_Context(
                channel, context, extension, priority
            )
        )

    def get_active_channels(self):
        return self.execute(
            #pystrix.ami.core.CoreShowChannels()
            pystrix.ami.core.Reload()
            print("Dialplan recargado exitosamente.")
        )

class MixMonitor(pystrix.ami.ami._Request):
    def __init__(self, channel, filename):
        pystrix.ami.ami._Request.__init__(self, 'MixMonitor')
        self['Channel'] = channel
        self['File'] = filename

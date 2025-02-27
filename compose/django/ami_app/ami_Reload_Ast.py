import pystrix
import logging
from datetime import datetime
#from Fastagi.settings import AMI_HOST, AMI_USER, AMI_PASSWD, AMI_PORT
AMI_HOST = '198.58.111.115'
# AMI_HOST = '192.168.122.124'
AMI_USER = 'asteriskami1'
AMI_PASSWD = 'inbtel-2025ñ'
AMI_PORT = '5038'
class AMIAsterisk():

    def __init__(self):
        # Inicializamos el Objeto de pystrix
        self._ami = pystrix.ami.Manager()
        # Creamos la funcion de conexion
        self._ami.connect(host=AMI_HOST, port=int(AMI_PORT))
        challenge_response = self._ami.send_action(
            pystrix.ami.core.Challenge()
        )

        if challenge_response and challenge_response.success:
            action = pystrix.ami.core.Login(
                AMI_USER, AMI_PASSWD,
                challenge=challenge_response.result['Challenge']
            )
            self._ami.send_action(action)
        else:
            self._kill_flag = True
            logging.error(
                'Asterisk did not privide an MD5 challenge token' +
                (challenge_response is None and ': timed out' or '')
            )
        self._ami.monitor_connection()


    def reloadast(self):
        self._ami.send_action(
            pystrix.ami.core.Reload())

# Crear una instancia de AMIAsterisk y ejecutar la función reloadast al ejecutar el script
if __name__ == "__main__":
    ami = AMIAsterisk()
    datos = ami.reloadast()  # Ejecutar la recarga al iniciar el script
    #print(datos)
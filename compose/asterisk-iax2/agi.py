#!/usr/bin/python3
import sys
import logging
# Manejo de errores, guardamos el log.
logging.basicConfig(level=logging.INFO, filename='/var/log/agi.log', format='%(asctime)s:%(levelname)s:%(message)s')
# Declaramos las variables con las que manejaremos las entradas y salidas.
cursor_sdtin = sys.stdin
cursor_sdtout = sys.stdout

def get_env_vars():
   # Obtenemos las variables de asterisk y las almacenamos en un diccionario.
   # para que quede de la siguiente manera
    """{
        'agi_request': 'agi.py',
        'agi_channel': 'IAX2/100-10643',
        'agi_language': 'es',
        'agi_type': 'IAX2',
        'agi_uniqueid': '1677866318.72',
        'agi_version': '18.15.0',
        'agi_callerid': '100',
        'agi_calleridname': 'Test',
        'agi_callingpres': '1',
        'agi_callingani2': '0',
        'agi_callington': '0',
        'agi_callingtns': '0',
        'agi_dnid': '1500',
        'agi_rdnis': 'unknown',
        'agi_context': 'from-internal',
        'agi_extension': '1500',
        'agi_priority': '2',
        'agi_enhanced': '0.0', 
        'agi_accountcode': '',
        'agi_threadid': '140407944936248'
    }"""
    info = {}
    """
    Se leen las variables de asterisk y se almacenan en un diccionario.
    Por ejemplo:
    {
        'agi_request': 'agi.py',
        'agi_channel': 'IAX2/100-10643'
    }
    Esto leyendo las entradas stdin linea por linea hasta recibir una linea vacia o una linea con un salto de linea.
    """
    for line in cursor_sdtin:
        # Si me manda un salto de linea o linea vacia se rompe el bucle por que indicaria que ya termino de enviarme los parametros
        if line == '' or line == '\n':
            break
        else:
            # Se guardan los datos en el diccionario info
            key, value = line.split(':', 1)
            info[key] = value.strip()
    return info

""" Enviar comandos a asterisk.
Primero se formatea el comando con los argumentos.
Luego se escribe en el canal de salida stdout.
Se guarda el log y se limpia el buffer.
"""
def send_command(command, *args):
    arguments = ' '.join(map(str, args))
    full_command = f'{command} {arguments}\n'
    # Una vez formateado el comando se escribe en el canal de salida "se envia a STDOUT"
    cursor_sdtout.write(full_command)
    logging.info(f'COMMAND: {full_command}')
    cursor_sdtout.flush()   # Vaciamos el buffer
# Se lee la respuesta de asterisk
def agi_response():
    return cursor_sdtin.readline()
# Se imprime la respuesta de manera mas legible.
def response():
    return f'RESPONSE: {agi_response()}'
"""
La idea es ir enviando un comnado a asterisk y recibir la respuesta.
Si no se sigue esta idea asterisk se cuelga.
"""
if __name__ == '__main__':
    try:
        variables = get_env_vars()
        logging.info(variables)
        send_command('ANSWER')
        logging.info(response())
        send_command('VERBOSE','PRUEBA', 1)
        logging.info(response())
        send_command('GET VARIABLE','EXTEN')
        logging.info(response())
        # Mandamos un comando, enviamos un audio y tambien las respuestas que pueden presionar y al final en tiempo de espera para continuar.
        send_command('STREAM FILE','custom/BIENV_ENC', "'1,2,3,4'", 0)
        # Nos devuelve un string el cual debemos formatear (remover los espacios) y el ultimo numero es la respueta que presionaron.
        result = agi_response().split(' ')[1] 
        logging.info(f'RESPONSE {chr(int(result.split("=")[-1]))}')
        send_command('HANGUP', variables['agi_channel'])
        logging.info(response())

    except Exception as error:
        logging.error(error)
        sys.stderr(error)
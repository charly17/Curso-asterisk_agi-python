#!/opt/virtualenv/bin/python
import re
import threading
import time
import pystrix


class FastAGIServer(threading.Thread):
    """
    A simple thread that runs a FastAGI server forever.
    """
    _fagi_server = None  # The FastAGI server controlled by this thread

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self._fagi_server = pystrix.agi.FastAGIServer(interface='0.0.0.0')

        self._fagi_server.register_script_handler(
            re.compile('variables'), self.variables)

        self._fagi_server.register_script_handler(
            re.compile('channel-variables'), self.channel_variables)

        self._fagi_server.register_script_handler(
            re.compile('dial-app'), self.dial_app)

        self._fagi_server.register_script_handler(
            re.compile('say-alfa-digit'), self.say_alfa_digit)

        self._fagi_server.register_script_handler(
            re.compile('llamada-pin'), self.llamada_pin)

    def variables(self, agi, *args, **kwargs):
        agi.execute(pystrix.agi.core.Answer())
        agi.execute(pystrix.agi.core.SetVariable('DESCRIPCION',
                                                 'Mostramos variables')
                    )
        agi.execute(pystrix.agi.core.SetVariable('DESTINO', '102'))
        agi.execute(pystrix.agi.core.SetVariable('TIEMPO', '10'))
        agi.execute(pystrix.agi.core.SetVariable('OPCIONES', 'TtR'))

    def channel_variables(self, agi, *args, **kwargs):
        agi.execute(pystrix.agi.core.SetVariable('CHANVAR2',
                    agi.execute(pystrix.agi.core.GetFullVariable('${EXTEN}'))
            )
        )
        agi.execute(pystrix.agi.core.SetVariable('CHANVAR1',
                    agi.execute(pystrix.agi.core.GetFullVariable('${CONTEXT}'))
            )
        )
        agi.execute(pystrix.agi.core.SetVariable('CHANVAR3',
                    agi.execute(
                        pystrix.agi.core.GetFullVariable('${PRIORITY}'))
            )
        )
        agi.execute(pystrix.agi.core.SetVariable('CHANVAR4',
                    agi.execute(pystrix.agi.core.GetFullVariable('${CHANNEL}'))
            )
        )
        agi.execute(pystrix.agi.core.SetVariable('CHANVAR5',
                    agi.execute(
                        pystrix.agi.core.GetFullVariable('${CALLERID(all)}'))
            )
        )

    def dial_app(self, agi, *args, **kwargs):
        agi.execute(pystrix.agi.core.Exec('Dial',
                    options=('IAX2/102', '50', 'TtR'))
                    )

    def say_alfa_digit(self, agi, *args, **kwargs):
        agi.execute(pystrix.agi.core.SayDigits(1234)
                    )

        agi.execute(pystrix.agi.core.SayAlpha('abcd')
                    )

    def llamada_pin(self, agi, *args, **kwargs):
        opcion = 2
        allowed_extension = {
            '102': '8765'
        }
        password = agi.execute(
            pystrix.agi.core.GetFullVariable('${CONTRASENA}')
        )
        extension = agi.execute(
            pystrix.agi.core.GetFullVariable('${NUMERO}'))

        for exten, passwd in allowed_extension.items():
            agi.execute(
                pystrix.agi.core.Verbose(f'{password} {passwd}', level=1))
            agi.execute(
                pystrix.agi.core.Verbose(f'{extension} {exten}', level=1))
            if exten == extension and passwd == password:
                opcion = 1

        agi.execute(pystrix.agi.core.SetVariable('OPCION', opcion))

    def kill(self):
        self._fagi_server.shutdown()

    def run(self):
        self._fagi_server.serve_forever()


if __name__ == '__main__':
    fastagi_core = FastAGIServer()
    fastagi_core.start()

    while fastagi_core.is_alive():
        time.sleep(1)
    fastagi_core.kill()

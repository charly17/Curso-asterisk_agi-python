#!/opt/virtualenv/bin/python
import os
import re
import sys
import time
import django
import logging
import pystrix
import threading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fastagi.settings')
django.setup()
from survey.models import Survey  # noqa: E402


class FastAGIServer(threading.Thread):

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
            re.compile('llamada-pin$'), self.llamada_pin)

        self._fagi_server.register_script_handler(
            re.compile('llamada-pin-py'), self.llamada_pin_py)

        self._fagi_server.register_script_handler(
            re.compile('survey'), self.survey)

# -------------------------------------------------------------------------------------
#   Agi apps del laboratorio 1
# -------------------------------------------------------------------------------------
    def variables(self, agi, *args, **kwargs):
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

# -------------------------------------------------------------------------------------
#   Agi apps del laboratorio 2
# -------------------------------------------------------------------------------------

    def llamada_pin(self, agi, *args, **kwargs):
        opcion = 2
        allowed_extension = {
            '102': '8765'
        }
        password = agi.execute(
            pystrix.agi.core.GetFullVariable('${CONTRASENA}')
        )
        extension = agi.execute(
            pystrix.agi.core.GetFullVariable('${NUMERO}')
        )

        if extension in allowed_extension.keys():
            if password == allowed_extension[extension]:
                opcion = 1

        agi.execute(pystrix.agi.core.SetVariable('OPCION', opcion))

    def llamada_pin_py(self, agi, *args, **kwargs):
        validate = False
        allowed_extension = {
            '102': '6543'
        }
        agi.execute(
            pystrix.agi.core.Verbose('Capturamos contrasena', level=1)
        )
        agi.execute(pystrix.agi.core.Answer())
        extension = agi.execute(
            pystrix.agi.core.GetFullVariable('${CALLERID(num)}')
        )
        while not validate:
            password, _ = agi.execute(pystrix.agi.core.GetData(
                'custom/ingresar_contrasena', 5000, 4)
            )

            if extension in allowed_extension.keys():
                if password == allowed_extension[extension]:
                    validate = True

            if validate:
                agi.execute(
                    pystrix.agi.core.Exec('dial', ('IAX2/102', '60', 'TtR'))
                )
            else:
                agi.execute(
                    pystrix.agi.core.StreamFile('custom/contrasena_incorrecta')
                )

    def survey(self, agi, *args, **kwargs):

        survey_options = [
            {
                'audio': 'custom/BIENV_ENC',
                'type': 1,
                'options': []
            },
            {
                'audio': 'custom/P1_ENC',
                'type': 2,
                'options': [1, 2, 3, 4, 5]
            },
            {
                'audio': 'custom/P2_ENC',
                'type': 2,
                'options': '12345'
            },
            {
                'audio': 'custom/P3_ENC',
                'type': 2,
                'options': ['1', '2', '3', '4', '5']
            },
        ]
        self.recusive_call_survey(agi, survey_options, 0)

    def recusive_call_survey(self, agi, survey, option):
        """
        It's a recursive function that plays a survey, and if the user doesn't
        respond, it plays a message and then calls itself again

        :param agi: The AGI object
        :param survey: This is the list of questions that will be asked
        :param option: The option number to be played
        """
        try:
            if len(survey) > option:
                option_content = survey[option]
                if option_content['type'] == 1:
                    opt = self.decorator_playback(
                        agi,
                        pystrix.agi.core.StreamFile,
                        filename=option_content['audio'],
                        sample_offset=5000
                    )
                elif option_content['type'] == 2:
                    opt = self.decorator_playback(
                        agi,
                        pystrix.agi.core.GetOption,
                        attempt=3,
                        filename=option_content['audio'],
                        escape_digits=option_content['options'],
                        timeout=5000
                    )

                if opt is None and option_content['type'] != 1:
                    self.decorator_playback(
                        agi,
                        pystrix.agi.core.StreamFile,
                        filename='custom/DESP_ENC',
                        sample_offset=2000
                    )
                else:
                    if option_content['type'] != 1:
                        unique_id = agi.execute(
                            pystrix.agi.core.GetFullVariable('${UNIQUEID}')
                        )
                        caller_id = agi.execute(
                            pystrix.agi.core.GetFullVariable(
                                '${CALLERID(num)}'
                            )
                        )
                        Survey.objects.create(
                            unique_id=unique_id,
                            phone_number=caller_id,
                            question=option,
                            answer=int(opt[0])
                        )
                        self.decorator_playback(
                            agi,
                            pystrix.agi.core.StreamFile,
                            filename='custom/RESP_REG',
                            sample_offset=2000
                        )
                    option += 1
                    self.recusive_call_survey(agi, survey, option)
            else:
                self.decorator_playback(
                    agi,
                    pystrix.agi.core.StreamFile,
                    filename='custom/DESP_ENC',
                    sample_offset=2000
                )
        except pystrix.agi.agi_core.AGIAppError:
            logging.warning('Ha ocurrido un error')

    def decorator_playback(self, agi, playback_func, attempt=1, **kwargs):
        """
        It will keep playing the recording until the user presses a key or the
        number of attempts is
        reached

        :param agi: The AGI object
        :param playback_func: The function that will be called to play the
        audio file
        :param attempt: The number of times to play the recording, defaults
        to 1 (optional)
        :return: The response of the playback function.
        """
        response = None
        attempt_number = 0
        while response is None and attempt_number < attempt:
            response = agi.execute(playback_func(**kwargs))
            attempt_number += 1
        return response

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

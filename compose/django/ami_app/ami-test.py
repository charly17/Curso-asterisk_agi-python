import pystrix
import logging
from datetime import datetime
from Fastagi.settings import AMI_HOST, AMI_USER, AMI_PASSWD, AMI_PORT

class AMIAsterisk():

    def _init_(self):
        self._ami = pystrix.ami.Manager()
        self._ami.connect(host=AMI_HOST, port=init(AMI_PORT))
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
                'Asterisk did not privide an MD5 challenge token' +
                (challenge_response is None and ': timed out' or '')
            )
        self._ami.monitor_connection()

    def _register_callbacks(self):
        self._ami.register_callback(
            '', self.events
        )

    def events(self, events):
        logging.warning(events)


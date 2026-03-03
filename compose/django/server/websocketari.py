import websocket
from ari import ARI
import rel
import json


class SurveyAri:

    survey_options = [
        {
            'audio': 'custom/BIENV_ENC',
            'type': 1,
            'options': []
        },
        {
            'audio': 'custom/P1_ENC',
            'type': 2,
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'audio': 'custom/P2_ENC',
            'type': 2,
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'audio': 'custom/P3_ENC',
            'type': 2,
            'options': ['1', '2', '3', '4', '5']
        },
    ]

    def __init__(self, max_attempts=3):
        self.question = 0
        self.sound = None
        self.options = None
        self.attempts = 0
        self.playback_id = None
        self.answers = {}
        self.max_attempts = max_attempts

    def get_sound(self):
        return self.survey_options[self.question]['audio']

    def get_options(self):
        return self.survey_options[self.question]['options']

    def get_type(self):
        return self.survey_options[self.question]['type']

    def next_question(self):
        if self.question < len(self.survey_options):
            self.question += 1

    def inc_attempts(self):
        self.attempts += 1

    def answer_register(self, answer):
        if self.question not in self.answers.keys():
            self.answers[self.question] = answer
            self.next_question()

    def is_finish(self):
        return (True if self.question >= len(self.survey_options) or
                self.attempts >= self.max_attempts else False)

    def is_answered(self):
        return self.question in self.answers


memory_route = {}


def on_message(ws, message):
    ari_object = ARI('astuser2', 'asterisk', host='asterisk')
    event_to_dict = json.loads(message)
    event = event_to_dict.get('type', 'default')
    print(event_to_dict)

    if event == 'StasisStart':
        channel = event_to_dict['channel']['id']
        if channel not in memory_route.keys():
            memory_route[channel] = SurveyAri()

        ari_object.answer(event_to_dict['channel']['id'])
        ari_object.playback(
            channel,
            memory_route[channel].get_sound()
        )

    if event == 'ChannelDtmfReceived':
        option = event_to_dict['digit']
        channel = event_to_dict['channel']['id']
        current_channel = memory_route[channel]
        if option in current_channel.get_options():
            ari_object.stop_playback(current_channel.playback_id)
            current_channel.answer_register(option)
            current_channel.attempts = 0

    if event == 'PlaybackStarted':
        target = event_to_dict['playback']['target_uri']
        _, channel = target.split(':')
        memory_route[channel].playback_id = event_to_dict['playback']['id']

    if event == 'PlaybackFinished':
        target = event_to_dict['playback']['target_uri']
        _, channel = target.split(':')
        current_channel = memory_route[channel]

        if not current_channel.is_finish():
            if current_channel.get_type() == 1:
                current_channel.next_question()

            if (current_channel.get_type() == 2 and
               not current_channel.is_answered()):
                current_channel.inc_attempts()

            ari_object.playback(
                channel,
                current_channel.get_sound()
            )
        else:
            ari_object.playback(
                channel,
                'custom/DESP_ENC'
            )
            ari_object.continue_call(channel)


def on_error(ws, error):
    print(f'error: {error}')


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("Opened connection")


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://asterisk:8088/ari/events?api_key=astuser2:asterisk&app=survey",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

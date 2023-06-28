import requests


class ARI:

    def __init__(self, user, password, host='localhost', port='8088'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def post(self, route):
        uri = f'http://{self.host}:{self.port}/ari/{route}'
        print(uri)
        return requests.post(uri, auth=(self.user, self.password))

    def get(self, route):
        uri = f'http://{self.host}:{self.port}/ari/{route}'
        return requests.post(uri, auth=(self.user, self.password))

    def delete(self, route):
        uri = f'http://{self.host}:{self.port}/ari/{route}'
        return requests.delete(uri, auth=(self.user, self.password))

    def playback(self, channel_id, sound):
        route = f'channels/{channel_id}/play?media=sound:{sound}'
        return self.post(route)

    def stop_playback(self, playback_id):
        route = f'playbacks/{playback_id}'
        return self.delete(route)

    def get_playback(self, playback_id):
        route = f'playbacks/{playback_id}'
        return self.get(route)

    def answer(self, channel_id):
        route = f'channels/{channel_id}/answer'
        return self.post(route)

    def continue_call(self, channel_id):
        route = f'channels/{channel_id}/continue'
        return self.post(route)

    def create_channel(self, channel):
        route = f'channels?endpoint={channel}&app=survey'
        return self.post(route)

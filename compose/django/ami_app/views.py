import logging
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from requests.auth import HTTPBasicAuth
import requests
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import TemplateView
from rest_framework.renderers import JSONRenderer
from ami_app.ami import AMIAsterisk
from ami_app.serializer import Click2CallSerializer



class AMICommandsViewSet(GenericViewSet, ListModelMixin):

    def list(self, request, *args, **kwargs):
        response_ami = AMIAsterisk().get_command_list()
        if response_ami is not None:
            response = {
                'result': response_ami[0],
                'response': response_ami[1],
                'request': response_ami[2],
                'action_id': response_ami[3],
                'success': response_ami[4],
                'time': response_ami[5],
                'events': response_ami[6],
                'events_timeout': response_ami[7],
            }
            return Response(response)

        return Response({'msg': 'Ooops! Ha ocurrido un error en la petición'})


class IAXPeersViewSet(GenericViewSet, ListModelMixin):

    def list(self, request, *args, **kwargs):
        response_ami = AMIAsterisk().get_iax_peers()
        if response_ami is not None:
            response = {
                'result': response_ami[0],
                'response': response_ami[1],
                'request': response_ami[2],
                'action_id': response_ami[3],
                'success': response_ami[4],
                'time': response_ami[5],
                'events': response_ami[6],
                'events_timeout': response_ami[7],
            }
            return Response(response)

        return Response({'msg': 'Ooops! Ha ocurrido un error en la petición'})


class IAXPeersView(TemplateView):

    template_name = 'amilab1.html'


class Click2CallViewset(GenericViewSet, CreateModelMixin):

    serializer_class = Click2CallSerializer

    def create(self, request, *args, **kwargs):
        action = self.get_serializer(data=request.data)
        if action.is_valid():

            response = AMIAsterisk().make_call(**action.data)
            logging.warning(response)
            if response is not None:
                return Response(response[0])
        return Response({'msg': 'error'})

class ARIConnect(TemplateView):

    template_name = 'ari.html'


class ARIVariable(TemplateView):

    template_name = 'ari_variable.html'


class ARIOriginate(TemplateView):

    template_name = 'ari_originate.html'


class ARIInterface(GenericViewSet):
    ari_user = 'astuser2'
    ari_passwd = 'asterisk'

    @action(
        detail=False, url_path='post',
        url_name='requests', methods=['GET', 'POST', 'PUT', 'DELETE'],
        renderer_classes=[JSONRenderer]
    )
    def post_request(self, request, *args, **kwargs):
        """
        object_example = {
            "method": "GET | POST | DELETE | PUT",
            "uri": "http://asterisk/ari/channels/{channelid}/play",
            "query_params": "media=sound:digits/1"
        }
        """
        data = request.data
        if (not data.get('method', False) or
           not data.get('uri', False)):
            return Response({'msg': 'missing arguments'})

        params = data.get('query_params', '')
        auth = auth = HTTPBasicAuth(self.ari_user, self.ari_passwd)
        headers = {
            'Content-Type': 'application/json'
        }
        response = {
            'msg': 'no se ejecutó ningún procedimiento'
        }
        print(request.data)
        # try:
        if data['method'] == 'GET':
            response = requests.get(
                data['uri'],
                params,
                auth=auth,
                headers=headers
            )

        if data['method'] == 'POST':
            response = requests.post(
                data['uri'],
                params,
                auth=auth,
                headers=headers
            )

        if data['method'] == 'DELETE':
            response = requests.delete(
                data['uri'],
                auth=auth,
                headers=headers
            )

        if data['method'] == 'PUT':
            response = requests.put(
                data['uri'],
                params,
                auth=auth,
                headers=headers
            )
        return Response(response)
        # except Exception as error:
        #     print(error)
        #     return Response({
        #         'msg': 'Ocurrió un error en su solicitud'
        #     })


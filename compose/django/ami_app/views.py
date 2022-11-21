import logging
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from django.views.generic import TemplateView
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

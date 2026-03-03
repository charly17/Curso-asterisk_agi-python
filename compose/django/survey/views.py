from rest_framework import viewsets, mixins
from rest_framework.response import Response
from survey.models import Survey


class SurveyViewSets(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Survey.objects.all()

    def list(self, request, *args, **kwargs):
        data_response = self.get_queryset()
        custom_response = {}
        for data in data_response:
            if data.unique_id not in custom_response:
                custom_response[data.unique_id] = {
                    'timestamp': data.created_at,
                    data.phone_number: []
                }
            custom_response[data.unique_id][data.phone_number].append(
                {
                    'question': data.question,
                    'answer': data.answer,
                }
            )
        return Response(custom_response)

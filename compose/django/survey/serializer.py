from rest_framework import serializers
from .models import Survey


class SurveySerializer(serializers.ModelSerializer):
    dict_response = {}

    class Meta:
        model = Survey
        fields = '__all__'

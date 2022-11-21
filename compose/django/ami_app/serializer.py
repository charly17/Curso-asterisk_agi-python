from rest_framework import serializers


class Click2CallSerializer(serializers.Serializer):
    channel = serializers.CharField(
        max_length=255, default='local/6000@from-internal'
    )
    context = serializers.CharField(max_length=255, default='from-internal')
    extension = serializers.IntegerField(default=102)
    priority = serializers.IntegerField(default=1)

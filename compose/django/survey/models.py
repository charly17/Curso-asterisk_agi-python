from django.db import models
# Create your models here.


class Survey(models.Model):
    unique_id = models.CharField(max_length=255)
    question = models.IntegerField()
    answer = models.IntegerField()
    phone_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

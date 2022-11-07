# Django y rest_framework
from rest_framework import routers
from django.urls import include, path
from .views import SurveyViewSets

# create routers
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'', SurveyViewSets, basename='survey')

urlpatterns = [
    path('', include(router.urls)),
]

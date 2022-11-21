# Django y rest_framework
from rest_framework import routers
from django.urls import include, path
from .views import (
    AMICommandsViewSet, IAXPeersViewSet, IAXPeersView, Click2CallViewset
)

# create routers
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'command_list/', AMICommandsViewSet, basename='ami')
router.register(r'iax2_peers/', IAXPeersViewSet, basename='ami')
router.register(r'make_call/', Click2CallViewset, basename='ami')

urlpatterns = [
    path('ami/', include(router.urls)),
    path(
        route='ami/iax2_peers_ws/',
        view=IAXPeersView.as_view(),
        name='iax_peer_ws'
    ),
]

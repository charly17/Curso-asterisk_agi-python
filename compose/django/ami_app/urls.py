# Django y rest_framework
from rest_framework import routers
from django.urls import include, path
from .views import (
    AMICommandsViewSet, IAXPeersViewSet, IAXPeersView, Click2CallViewset,
    ARIConnect, ARIInterface, ARIVariable, ARIOriginate
)

# create routers
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'command_list/', AMICommandsViewSet, basename='ami')
router.register(r'iax2_peers/', IAXPeersViewSet, basename='ami')
router.register(r'make_call/', Click2CallViewset, basename='ami')

# create router to ari
router_ari = routers.SimpleRouter(trailing_slash=False)
router_ari.register(r'api', ARIInterface, basename='ari')

urlpatterns = [
    path('ami/', include(router.urls)),
    path('ari/', include(router_ari.urls)),
    path(
        route='ami/iax2_peers_ws/',
        view=IAXPeersView.as_view(),
        name='iax_peer_ws'
    ),
    path(
        route='ari/connect',
        view=ARIConnect.as_view(),
        name='ari'
    ),
    path(
        route='ari/variables',
        view=ARIVariable.as_view(),
        name='ari_variable'
    ),
    path(
        route='ari/originate',
        view=ARIOriginate.as_view(),
        name='ari_originate'
    ),
]

from rest_framework import mixins, viewsets
from rest_framework import filters

class CreateDestroyViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    ):
    pass
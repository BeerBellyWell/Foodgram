from rest_framework import mixins, viewsets
from rest_framework import filters

class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass
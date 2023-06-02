from rest_framework import mixins, viewsets


class CreateDestroyViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    pass

from django.apps import apps
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.generic import View

from acl.serializers import UserListSerializer
from acl.services import GeneralUserService


class UsersBaseViewSet(ModelViewSet, GenericViewSet):
    model = apps.get_model('acl', 'CustomUser')
    serializer_class = UserListSerializer
    queryset = model.objects.all()
    search_fields = ['first_name', 'last_name', 'user_type', 'email', 'phone_number' ]
    permission_classes = (AllowAny, )

    class_path = 'users'


    def get_queryset(self):
        return self.queryset.distinct()


    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        login_response = GeneralUserService().login(request.data)
        return Response(login_response, status=status.HTTP_200_OK)




from django.apps import apps
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse
from acl.serializers import LoginResponseSerializer, LoginSerializer, SignUpSerializer, UserCreateSerializer, UserListSerializer
from acl.services import GeneralUserService



class UsersBaseViewSet(ModelViewSet, GenericViewSet):
    """
    Base class view for user managemet
    """
    model = apps.get_model('acl', 'CustomUser')
    serializer_class = UserListSerializer
    search_fields = ['first_name', 'last_name', 'user_type', 'email', 'phone_number' ]

    class_path = 'users'

    def get_permissions(self):
        """
        Allow unauthenticated access only for create and login.
        Everything else uses the default (AuthenticatedUserPermission).
        """
        if self.action in ('create', 'login'):
            return [AllowAny()]
        return super().get_permissions()


    def get_queryset(self):
        if str(self.request.query_params.get('include_deleted', 0)) ==str(1): # type:ignore
            return self.model.objects_all.all() # type:ignore
        return self.model.objects.all().distinct()


    @extend_schema(
        request=LoginSerializer,                 
        responses={
            200: OpenApiResponse(
                description="Successful login",
                response=LoginResponseSerializer
            ),
            400: OpenApiResponse(description="Invalid credentials"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Authenticate a user and return tokens / user data.",
        tags=["acl"],                               
    )
    @action(detail=False, methods=['POST'], url_path='login', authentication_classes=[],)
    def login(self, request):
        login_response = GeneralUserService().login(request.data)
        return Response(login_response, status=status.HTTP_200_OK)

    @extend_schema(
            request=SignUpSerializer,  
            responses={201: UserListSerializer},               
            description="Create a user",
            tags=["acl"],                               
        )
    def create(self, request, *args, **kwargs):
        self.serializer_class = UserCreateSerializer
        return super().create(request, *args, **kwargs)

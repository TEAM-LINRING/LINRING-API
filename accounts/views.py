import django_filters
from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.jwt_auth import set_jwt_access_cookie, set_jwt_refresh_cookie
from dj_rest_auth.views import UserDetailsView, sensitive_post_parameters_m, LogoutView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from fcm_django.models import FCMDevice
from rest_framework import status, filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User, TagSet
from accounts.serializers import NewCookieTokenRefreshSerializer, UserSerializer, TagSetSerializer
from utils.pagination import StandardResultsSetPagination


# override after then fixed remove
class UserDetailsViewOverride(UserDetailsView):
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]


class UserLogoutViewOverride(LogoutView):
    def logout(self, request):
        devices = FCMDevice.objects.filter(user=request.user).delete()
        return super().logout(request)


class PasswordChangeView(GenericAPIView):
    """
    Calls Django Auth SetPasswordForm save method.

    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = api_settings.PASSWORD_CHANGE_SERIALIZER
    permission_classes = (IsAuthenticated,)
    throttle_scope = 'dj_rest_auth'
    authentication_classes = [JWTAuthentication]

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'New password has been saved.'})


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'last_login': ['gt'],
        }


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = UserFilter
    filterset_fields = ['tagset_user__place', 'tagset_user__person', 'tagset_user__method']
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ('-last_login',)
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def get_refresh_view():
    """ Returns a Token Refresh CBV without a circular import """
    from rest_framework_simplejwt.settings import api_settings as jwt_settings
    from rest_framework_simplejwt.views import TokenRefreshView

    class RefreshViewWithCookieSupport(TokenRefreshView):
        serializer_class = NewCookieTokenRefreshSerializer

        def finalize_response(self, request, response, *args, **kwargs):
            if response.status_code == status.HTTP_200_OK and 'access' in response.data:
                set_jwt_access_cookie(response, response.data['access'])
                response.data['access_expiration'] = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            if response.status_code == status.HTTP_200_OK and 'refresh' in response.data:
                set_jwt_refresh_cookie(response, response.data['refresh'])
                response.data['refresh_expiration'] = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            return super().finalize_response(request, response, *args, **kwargs)

    return RefreshViewWithCookieSupport


class TagSetViewSet(ModelViewSet):
    queryset = TagSet.objects.all()
    serializer_class = TagSetSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = TagSet.objects.filter(owner=self.request.user)
        return queryset

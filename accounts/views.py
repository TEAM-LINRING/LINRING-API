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
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from accounts.models import User, TagSet
from accounts.serializers import NewCookieTokenRefreshSerializer, UserSerializer, TagSetSerializer, NickNameSerializer
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = UserFilter
    filterset_fields = ['tagset_user__place', 'tagset_user__person', 'tagset_user__method']
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ('-last_login',)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['validationNickName']:
            return NickNameSerializer
    # @action(['post'], detail=False, url_path="validation/nickname")
    # def validationNickName(self, request, *args, **kwargs):
    #     print("validationName")
    #     # return super().list(request, *args, **kwargs)
    #     #TODO : 적극적인 시리얼라이저 활용
    #     nickname = NickNameSerializer(request.data)
    #     nickname.is_valid(True)
    #
    # def validationEmail(self, request, *args, **kwargs):
    #     print("validationEmail")


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
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = TagSet.objects.filter(owner=self.request.user)
        return queryset

# 태그 ID를 넣으면
class UserSearch(APIView):
    tags = TagSet.objects.filter(is_active=True)
    def get(self, request, id):
        user = request.user
        # user_tag = TagSet.objects.filter(id=id, is_active=True)[0]  # 태그를 리스트 형태로 받아옴.
        user_tag = user.tagset_user.exclude(id=id, is_active=True)[0]  # 태그를 리스트 형태로 받아옴.
        place = user_tag.place
        person = user_tag.person
        method = user_tag.method
        self.tags = self.fisrtFiltering(place, method)  # 1차 필터링
        self.secondFiltering(person, user)
        serializer = TagSetSerializer(self.tags, many=True)
        return Response(serializer.data)
    def fisrtFiltering(self, place, method):
        return self.tags.exclude(place=place, method=method)

    def secondFiltering(self, person, user):
        if "학번" in person:          # 학번 모델 나오면 해야할 듯.
            for tag in self.tags:
                other_user = tag.owner
            pass
        elif person == "선배" or person == "후배" or person == "동기":
            print("2")
        elif "과" in person:
            print("3")
        elif person == "아무나":
            print("4")
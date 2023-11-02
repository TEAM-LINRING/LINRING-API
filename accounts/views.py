import django_filters
from django.db.models import Q
from rest_framework import permissions
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
from accounts.serializers import NewCookieTokenRefreshSerializer, UserSerializer, TagSetSerializer, NickNameSerializer, \
    EmailSerializer
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
            print("nickname")
            return NickNameSerializer
        if self.action in ['validationEmail']:
            return EmailSerializer

    @action(detail=False, url_path="validation/nickname", methods=['post'], permission_classes=[permissions.AllowAny])
    def validationNickName(self, request, *args, **kwargs):
        # Check if a user with the given nickname already exists
        nickname = request.data.get('nickname', '')
        if User.objects.filter(nickname=nickname).exists():
            # If the nickname already exists, return an error response
            response_data = {"message": "Nickname is already in use"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If the nickname is available, return a success response
            response_data = {"message": "Nickname is available"}
            return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="validation/email", methods=['post'], permission_classes=[permissions.AllowAny])
    def validationEmail(self, request, *args, **kwargs):
        # Check if a user with the given nickname already exists
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():
            # If the nickname already exists, return an error response
            response_data = {"message": "email is already in use"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If the nickname is available, return a success response
            response_data = {"message": "email is available"}
            return Response(response_data, status=status.HTTP_200_OK)


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


class UserSearch(APIView):
    def __init__(self):
        self.tags = None
        self.tags_score = dict()

    def get(self, request, id):
        user = request.user
        user_tag = user.tagset_user.get(id=id)
        users = User.objects.exclude(id=user.id)
        self.tags = TagSet.objects.exclude(owner=user.id)

        # 만약 태그가 4개 미만인 경우 매칭 알고리즘, 추천 알고리즘 미적용 후 리턴
        if len(self.tags) < 4:
            seriallizer = TagSetSerializer(self.tags, many=True)
            return Response(seriallizer.data)

        rating_mean = 0
        for u in users:
            rating_mean += u.rating
        rating_mean /= len(users)
        for tag in self.tags:
            self.tags_score[tag.id] = 0
        place = user_tag.place
        method = user_tag.method
        self.fisrtTagCheck(place, method)
        self.secondTagCheck(user_tag)
        # print(f"user tag : {place}에서 {'같은 과' if user_tag.isSameDepartment else '다른 과'} {user_tag.person}와 {method}하기")
        # for i in range(0, len(self.tags)):
        #     print(
        #         f"tag{i + 1} : {self.tags[i].place}에서 {'같은 과' if self.tags[i].isSameDepartment else '다른 과'} {self.tags[i].person}와 {self.tags[i].method}하기 | tag_score : {self.tags_score[i + 1]}")
        result_tags = self.recommend(rating_mean)
        # for i in range(0, len(self.tags)):
        #     print(f"tag{i + 1} : {self.tags[i].place}에서 {'같은 과' if self.tags[i].isSameDepartment else '다른 과'} {self.tags[i].person}와 {self.tags[i].method}하기 | tag_score : {self.tags_score[i + 1]}")
        # print(result_tags)
        serializer = TagSetSerializer(result_tags, many=True)
        return Response(serializer.data)

    def fisrtTagCheck(self, place, method):
        equal_place_tags = self.tags.filter(place=place)
        equal_method_tags = self.tags.filter(method=method)

        for i in equal_method_tags:
            self.tags_score[i.id] += 1

        for i in equal_place_tags:
            self.tags_score[i.id] += 1

    # 같은 과, 다른 과 + 선배, 동기, 후배, 아무나
    # 나만 맞으면 1점, 상대도 같이 맞으면 1점 총 2점
    def secondTagCheck(self, user_tag):
        is_same_department = user_tag.isSameDepartment
        for other_tag in self.tags:
            is_same_other_department = other_tag.isSameDepartment
            self.tagCheck(user_tag, other_tag, is_same_department, True)
            self.tagCheck(other_tag, user_tag, is_same_other_department, False)

    def tagCheck(self, user_tag, other_user_tag, is_same_department, is_check):
        user_person = user_tag.person
        user = User.objects.get(id=user_tag.owner_id)
        user_student_number = user.student_number
        user_department = user.department

        other_user = User.objects.get(id=other_user_tag.owner_id)
        other_user_department = other_user.department
        other_user_student_number = User.objects.get(id=other_user_tag.owner_id).student_number

        if is_same_department and user_department == other_user_department:
            pass
        elif not is_same_department and user_department != other_user_department:
            pass
        else:
            return

        if user_person == "선배":
            if user_student_number > other_user_student_number and is_check:
                self.tags_score[other_user_tag.id] += 1
            elif user_student_number > other_user_student_number and not is_check:
                self.tags_score[user_tag.id] += 1
        elif user_person == "동기":
            if user_student_number == other_user_student_number and is_check:
                self.tags_score[other_user_tag.id] += 1
            elif user_student_number == other_user_student_number and not is_check:
                self.tags_score[user_tag.id] += 1
        elif user_person == "후배":
            if user_student_number < other_user_student_number and is_check:
                self.tags_score[other_user_tag.id] += 1
            elif user_student_number < other_user_student_number and not is_check:
                self.tags_score[user_tag.id] += 1
        else:
            if is_check:
                self.tags_score[other_user_tag.id] += 1
            else:
                self.tags_score[user_tag.id] += 1

    # n(매칭 알고리즘 결과 점수) + (상대 유저 매너점수 - 유저 매너점수 평균)
    def recommend(self, rating_mean):
        for tag in self.tags:
            self.tags_score[tag.id] += tag.owner.rating - rating_mean
        result_tag_list = list(dict(sorted(self.tags_score.items(), key=lambda x:x[1], reverse=True)))[:4]
        result_tag = list()
        for i in result_tag_list:
            result_tag.append(TagSet.objects.filter(id=i)[0])
        return result_tag

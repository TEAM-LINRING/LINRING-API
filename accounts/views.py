import django_filters
from django.db.models import Q
from rest_framework import permissions
from decimal import Decimal, getcontext
from dj_rest_auth.app_settings import api_settings
from django.shortcuts import get_object_or_404
from dj_rest_auth.jwt_auth import set_jwt_access_cookie, set_jwt_refresh_cookie
from dj_rest_auth.views import UserDetailsView, sensitive_post_parameters_m, LogoutView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password 
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
from rest_framework import generics, permissions
from rest_framework.schemas import ManualSchema
import json

from dj_rest_auth.views import PasswordResetConfirmView
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


from accounts.models import User, TagSet
from accounts.serializers import NewCookieTokenRefreshSerializer, UserSerializer, TagSetSerializer, NickNameSerializer, \
    EmailSerializer, RatingUpdateSerializer, UserDeleteSerializer, BlockUserSerializer
from utils.pagination import StandardResultsSetPagination


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
    filterset_fields = ['tagset_user__place', 'tagset_user__person', 'tagset_user__method']
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ('-last_login',)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = get_user_model().objects
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['validationNickName']:
            return NickNameSerializer
        if self.action in ['validationEmail']:
            return EmailSerializer
        if self.action in ['updateRating']:
            return RatingUpdateSerializer
        if self.action in ['custom_destroy']:
            return UserDeleteSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        password = request.data.get('password')
        if check_password(password, instance.password):
            instance.delete()
            return Response({'messege': 'Deleted successfully'})
        return Response({'messege': 'Invalid password'}, status=400)

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
        
class RatingUpdateView(generics.UpdateAPIView):
    serializer_class = RatingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_model().objects.all()

    def get_object(self):
        user_id = self.request.data.get('user', '')
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=user_id)
        return obj

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        rating = request.data.get('rating', '')
        user.rating = (Decimal(rating) + Decimal(user.rating)) / 2
        user.save()
        response_data = {
            'user': user.id,
            'new_rating': user.rating,
        }
        return Response(response_data)


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
        if isinstance(self.request.user, User):
            queryset = TagSet.objects.filter(owner=self.request.user)
            return queryset
        else:
            return TagSet.objects.none()

class BlockUserUpdateView(generics.UpdateAPIView):
    serializer_class = BlockUserSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        return get_user_model().objects.all()

    def get_object(self):
        user_id = self.request.data.get('user', '')
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=user_id)
        return obj

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        block_user_id = request.data.get('block_user', '')
        try:
            block_user = json.loads(user.block_user.replace("\'", "\""))
        except:
            block_user = {"user":[]}
        serializer_instance = BlockUserSerializer(data={'user':user, 'block_user':block_user_id})
        is_valid = serializer_instance.is_valid()
        serializer_instance.validate(serializer_instance.data)
        block_user["user"].append(int(block_user_id))
        user.block_user = json.dumps(block_user)
        user.save()
        response_data = {
            'user': user.id,
            'block_user': block_user["user"],
        }
        return Response(response_data)

        

class UserSearch(APIView):
    def __init__(self):
        self.tags = None
        self.tags_score = dict()

    def get(self, request, id):
        user = request.user
        user_tag = user.tagset_user.get(id=id)
        try:
            block_user = json.loads(user.block_user.replace("\'", "\""))
        except:
            block_user = {"user":[]}
        print(block_user["user"])
        users = User.objects.exclude(Q(id=user.id) | Q(id__in=block_user["user"]))
        print(users)
        self.tags = TagSet.objects.exclude(owner=user.id).exclude(is_active=False).exclude(owner__in=block_user["user"])

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
        result_tags = self.recommend(rating_mean)
        serializer = TagSetSerializer(result_tags, many=True)
        return Response(serializer.data)

    def fisrtTagCheck(self, place, method):
        equal_place_tags = self.tags.filter(place=place)
        equal_method_tags = self.tags.filter(method=method)

        for i in equal_method_tags:
            self.tags_score[i.id] += 1

        for i in equal_place_tags:
            self.tags_score[i.id] += 1

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

    def recommend(self, rating_mean):
        for tag in self.tags:
            self.tags_score[tag.id] += tag.owner.rating - rating_mean
        result_tag_list = list(dict(sorted(self.tags_score.items(), key=lambda x: x[1], reverse=True)))[:4]
        result_tag = list()
        for i in result_tag_list:
            result_tag.append(TagSet.objects.filter(id=i)[0])
        return result_tag

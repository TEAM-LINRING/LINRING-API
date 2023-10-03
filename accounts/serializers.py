from allauth.account.adapter import get_adapter
from allauth.utils import email_address_exists
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from allauth.account import app_settings as allauth_account_settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import TagSet


class UserRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    birthday = serializers.DateField(required=False)
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    number = serializers.CharField(max_length=128)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        domain = email.split("@")[1]
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    'A user is already registered with this e-mail address.',
                )
            if "kookmin.ac.kr" != domain:
                raise serializers.ValidationError(
                    'This domain is invalid.',
                )
        return email

    def validate_password1(self, password):
        print(password)
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'birthday': self.validated_data.get('birthday', None),
            'number': self.validated_data.get('number', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'name': self.validated_data.get('name', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.birthday = self.cleaned_data['birthday']
        user.number = self.cleaned_data['number']
        user.name = self.cleaned_data['name']
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        # self.custom_signup(request, user)
        # setup_user_email(request, user, [])
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ['password', 'is_staff', 'is_superuser']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ['is_staff', 'is_superuser']


class ResetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=256)
    password1 = serializers.CharField(max_length=256)
    password2 = serializers.CharField(max_length=256)


class CheckAvailableSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UpdateTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        ret = super().validate(attrs)
        if api_settings.UPDATE_LAST_LOGIN:
            token = AccessToken(ret['access'])
            user_id = token.payload['user_id']
            user = get_user_model().objects.get(id=user_id)
            update_last_login(None, user)
        return ret


class NewCookieTokenRefreshSerializer(UpdateTokenRefreshSerializer):
    refresh = serializers.CharField(required=False, help_text='WIll override cookie.')

    def extract_refresh_token(self):
        request = self.context['request']
        if 'refresh' in request.data and request.data['refresh'] != '':
            return request.data['refresh']
        cookie_name = api_settings.JWT_AUTH_REFRESH_COOKIE
        if cookie_name and cookie_name in request.COOKIES:
            return request.COOKIES.get(cookie_name)
        else:
            from rest_framework_simplejwt.exceptions import InvalidToken
            raise InvalidToken('No valid refresh token found.')

    def validate(self, attrs):
        attrs['refresh'] = self.extract_refresh_token()
        return super().validate(attrs)


class TagSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagSet
        fields = '__all__'

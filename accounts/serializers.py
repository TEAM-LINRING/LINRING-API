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

DEPARTMENT_CHOICES = (
    ('한국어문학부', '한국어문학부'),
    ('영어영문학부', '영어영문학부'),
    ('중국학부', '중국학부'),
    ('한국역사학과', '한국역사학과'),
    ('행정학과', '행정학과'),
    ('행정관리학과', '행정관리학과'),
    ('정치외교학과', '정치외교학과'),
    ('사회학과', '사회학과'),
    ('미디어광고학부', '미디어광고학부'),
    ('교육학과', '교육학과'),
    ('러시아유라시아학과', '러시아유라시아학과'),
    ('일본학과', '일본학과'),
    ('법학부', '법학부'),
    ('기업융합법학과', '기업융합법학과'),
    ('법학부', '법학부'),
    ('국제통상학과', '국제통상학과'),
    ('경영학부', '경영학부'),
    ('기업경영학부', '기업경영학부'),
    ('경영정보학부', '경영정보학부'),
    ('KMU KIBS', 'KMU KIBS'),
    ('재무금융회계학부', '재무금융회계학부'),
    ('AI빅데이터융합경영학과', 'AI빅데이터융합경영학과'),
    ('신소재공학부', '신소재공학부'),
    ('기계공학부', '기계공학부'),
    ('건설시스템공학부', '건설시스템공학부'),
    ('전자공학부', '전자공학부'),
    ('소프트웨어학부', '소프트웨어학부'),
    ('인공지능학부', '인공지능학부'),
    ('자동차공학과', '자동차공학과'),
    ('자동차IT융합학과', '자동차IT융합학과'),
    ('산림환경시스템학과', '산림환경시스템학과'),
    ('임산생명공학과', '임산생명공학과'),
    ('나노전자물리학과', '나노전자물리학과'),
    ('응용화학부', '응용화학부'),
    ('식품영양학과', '식품영양학과'),
    ('정보보안암호수학과', '정보보안암호수학과'),
    ('바이오발효융합학과', '바이오발효융합학과'),
    ('건축학부', '건축학부'),
    ('공업디자인학과', '공업디자인학과'),
    ('시각디자인학과', '시각디자인학과'),
    ('금속공예학과', '금속공예학과'),
    ('도자공예학과', '도자공예학과'),
    ('의상디자인학과', '의상디자인학과'),
    ('공간디자인학과', '공간디자인학과'),
    ('영상디자인학과', '영상디자인학과'),
    ('자동차운송디자인학과', '자동차운송디자인학과'),
    ('AI디자인학과', 'AI디자인학과'),
    ('음악학부', '음악학부'),
    ('미술학부', '미술학부'),
    ('공연예술학부', '공연예술학부'),
    ('스포츠교육학과', '스포츠교육학과'),
    ('스포츠산업레저학과', '스포츠산업레저학과'),
    ('스포츠건강재활학과', '스포츠건강재활학과'),
    ('미래모빌리티학과', '미래모빌리티학과'),
    ('교양대학', '교양대학'),
    ('인문기술융합학부', '인문기술융합학부'),
)

GRADE_CHOICES = (
    ("1학년", "1학년"),
    ("2학년", "2학년"),
    ("3학년", "3학년"),
    ("4학년", "4학년"),
    ("5학년", "5학년"),
    ("졸업생", "졸업생"),
    ("기타", "기타"),
)

SIGNIFICANT_CHOICES = (
    ("유학생", "유학생"),
    ("전과생", "전과생"),
    ("편입생", "편입생"),
    ("외국인", "외국인"),
    ("교환학생", "교환학생"),
    ("복수전공생", "복수전공생"),
    ("부전공생", "부전공생"),
    ("휴학생", "휴학생"),
)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(max_length=256, write_only=True)
    password2 = serializers.CharField(write_only=True)
    nickname = serializers.CharField(max_length=6)
    department = serializers.CharField(max_length=20)
    gender = serializers.CharField(max_length=10)
    student_number = serializers.IntegerField()
    grade = serializers.CharField(max_length=10)
    significant = serializers.CharField(max_length=10)

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


class NickNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('nickname',)


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email',)


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

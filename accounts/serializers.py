from allauth.account.adapter import get_adapter
from allauth.utils import email_address_exists
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from decimal import Decimal
from allauth.account import app_settings as allauth_account_settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import User
from accounts.models import TagSet
from accounts.models import Significant
from accounts.models import Profile
import json


COLLEGE_CHOICES = (
    ("글로벌인문지역대학", "글로벌인문지역대학"),
    ("사회과학대학", "사회과학대학"),
    ("법과대학", "법과대학"),
    ("경상대학", "경상대학"),
    ("경영대학", "경영대학"),
    ("창의공과대학", "창의공과대학"),
    ("소프트웨어융합대학", "소프트웨어융합대학"),
    ("자동차융합대학", "자동차융합대학"),
    ("과학기술대학", "과학기술대학"),
    ("건축대학", "건축대학"),
    ("조형대학", "조형대학"),
    ("예술대학", "예술대학"),
    ("체육대학", "체육대학"),
    ("미래모빌리티학과", "미래모빌리티학과"),
    ("교양대학", "교양대학"),
    ("인문기술융합학부", "인문기술융합학부")
)

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

GENDER_CHOICES = (
    ("남", "남"),
    ("여", "여")
)


class ProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    profile_image = serializers.ImageField()


class UserRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128, required=True)
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(max_length=256, write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    nickname = serializers.CharField(max_length=6, required=True)
    college = serializers.ChoiceField(required=True, choices=COLLEGE_CHOICES)
    department = serializers.ChoiceField(required=True, choices=DEPARTMENT_CHOICES)
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), required=True)
    gender = serializers.ChoiceField(required=True, choices=GENDER_CHOICES)
    student_number = serializers.IntegerField(required=True)
    birth = serializers.IntegerField(required=True)
    grade = serializers.ChoiceField(required=True, choices=GRADE_CHOICES)
    significant = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Significant.objects.all(),
        required=False
    )

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
        return get_adapter().clean_password(password)

    def validate_nickname(self, nickname):
        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError(
                'A user is already registered with this nickname.',
            )
        return nickname

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'department': self.validated_data.get('department', ''),
            'student_number': self.validated_data.get('student_number', ''),
            'grade': self.validated_data.get('grade', ''),
            'gender': self.validated_data.get('gender', ''),
            'college': self.validated_data.get('college', ''),
            'profile': self.validated_data.get('profile', ''),
            'name': self.validated_data.get('name', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'significant': self.validated_data.get('significant', []),
            'birth': self.validated_data.get('birth', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.name = self.cleaned_data['name']
        user.nickname = self.cleaned_data['nickname']
        user.profile = self.cleaned_data['profile']
        user.college = self.cleaned_data['college']
        user.department = self.cleaned_data['department']
        user.student_number = self.cleaned_data['student_number']
        user.grade = self.cleaned_data['grade']
        user.gender = self.cleaned_data['gender']
        user.birth = self.cleaned_data['birth']

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()

        if 'significant' in self.cleaned_data:
            user.significant.set(self.cleaned_data['significant'])
        user.save()
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

class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('password',)

class RatingUpdateSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    rating = serializers.DecimalField(max_digits=5, decimal_places=2)


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


class SignificantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Significant
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class BlockUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    block_user = serializers.IntegerField()

    def validate(self, data):
        user = data.get('user')
        block_user_id = int(data.get('block_user'))
        users = User.objects.all()
        try:
            block_user = json.loads(user.block_user.replace("\'", "\""))
        except:
            block_user = {"user":[]}

        if block_user_id in block_user['user']:
            raise serializers.ValidationError("이미 차단한 유저입니다.")

        if User.objects.get(id=block_user_id) not in users:
            raise serializers.ValidationError("존재하지 않는 유저입니다.")
        
        if User.objects.get(id=block_user_id) == user:
            raise serializers.ValidationError("자신을 차단할 수 없습니다.")
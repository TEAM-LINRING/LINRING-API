from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django_extensions.db.models import TimeStampedModel


class CustomUserManager(BaseUserManager):
    def create_user(self, extra_fields):
        user = self.model(
            **extra_fields
        )
        user.is_active = False
        user.set_password(user.password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(
            email=email, password=password
        )
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user


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


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    username = models.CharField(max_length=128, verbose_name="이름", null=True)
    email = models.EmailField(unique=True, verbose_name="이메일")
    password = models.CharField(max_length=256, verbose_name="패스워드")
    nickname = models.CharField(max_length=6, verbose_name="닉네임", null=True, blank=True, unique=True)
    profile = models.ImageField(verbose_name="프로필 이미지", null=True, blank=True)
    department = models.CharField(max_length=20, verbose_name="학과", choices=DEPARTMENT_CHOICES, null=True)
    student_number = models.IntegerField(null=True)
    grade = models.CharField(max_length=10, verbose_name="학년", choices=GRADE_CHOICES, null=True)
    significant = models.CharField(max_length=10, verbose_name="특이사항", choices=SIGNIFICANT_CHOICES, null=True,
                                   blank=True)
    rating = models.DecimalField(max_digits=100, default=0, decimal_places=2, verbose_name="평점", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="활성화 여부", default=True)
    is_staff = models.BooleanField(verbose_name="스태프 여부", default=False)
    is_superuser = models.BooleanField(verbose_name="최고 관리자 여부", default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    PASSWORD_FIELD = 'password'

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "유저 관리"
        verbose_name = "유저 관리"


PLACE_CHOICES = (
    ('북악관', '북악관'),
    ('예술대', '예술대'),
    ('미래관', '미래관'),
    ('공학관', '공학관'),
    ('경상관', '경상관'),
    ('본부관', '본부관'),
    ('용두리', '용두리'),
    ('도서관', '도서관'),
    ('복지관 열람실', '복지관 열람실'),
    ('자율주행스튜디오', '자율주행스튜디오'),
    ('어디서든', '어디서든'),
)

PERSON_CHOICES = (
    ('유학생', '유학생'),
    ('타과생', '타과생'),
    ('선배', '선배'),
    ('후배', '후배'),
    ('23학번', '23학번'),
    ('22학번', '22학번'),
    ('새내기', '새내기'),
    ('아무랑', '아무랑'),
    ('동기', '동기'),
)

METHOD_CHOICES = (
    ('스터디', '스터디'),
    ('모각코', '모각코'),
    ('식사', '식사'),
    ('수다', '수다'),
)


class TagSet(TimeStampedModel):
    place = models.CharField(max_length=12, verbose_name="장소", choices=PLACE_CHOICES)
    person = models.CharField(max_length=12, verbose_name="대상", choices=PERSON_CHOICES)
    method = models.CharField(max_length=12, verbose_name="행동", choices=METHOD_CHOICES)

    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    introduction = models.CharField(max_length=30, verbose_name="한줄소개", null=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="tagset_user", verbose_name="유저")

    def __str__(self):
        return self.owner.email

    class Meta:
        verbose_name_plural = "태그셋 관리"
        verbose_name = "태그셋 관리"

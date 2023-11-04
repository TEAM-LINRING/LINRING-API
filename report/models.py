from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

REASON_CHOICES = (
    ('1', '비속어를 사용했어요.'),
    ('2', '약속 장소에 나오지 않았어요.'),
    ('3', '허위정보를 기재했어요.'),
    ('4', '기타 사유'),
)

class Report(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="report_user", verbose_name="유저")
    target = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="report_target",
                               verbose_name="신고 대상")
    reason = models.CharField(max_length=100, verbose_name="신고 사유", choices=REASON_CHOICES)
    description = models.CharField(max_length=100, verbose_name="신고 사유 입력", null=True, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = "신고 관리"
        verbose_name = "신고 관리"

# Create your models here.

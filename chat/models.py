from django.contrib.auth import get_user_model
from django_extensions.db.models import TimeStampedModel
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver


class Room(TimeStampedModel):
    relation = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="관계자",
                                 related_name="relate")
    relation2 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="관계자2",
                                  related_name="relate2")

    tagset = models.ForeignKey("accounts.TagSet", on_delete=models.CASCADE, verbose_name="태그셋1", related_name="room_tagset")
    tagset2 = models.ForeignKey("accounts.TagSet", on_delete=models.CASCADE, verbose_name="태그셋2", related_name="room_tagset2")
    reservation_time = models.DateTimeField(null=True, verbose_name="만남예약시간", blank=True)
    
    latest_message = models.OneToOneField('Message', verbose_name="가장 최근 메시지", null=True, blank=True,
                                          on_delete=models.SET_NULL, related_name="latest_message")

    def update_latest_message(self):
        latest_message = self.message_room.latest('created')
        self.latest_message = latest_message
        self.save()

    class Meta:
        verbose_name_plural = "채팅방 관리"
        verbose_name = "채팅방 관리"


class Message(TimeStampedModel):
    room = models.ForeignKey('Room', verbose_name="채팅방", on_delete=models.CASCADE, related_name="message_room")
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="전송자",
                               related_name="room_sender")
    receiver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="수신자",
                                 related_name="room_receiver")
    message = models.TextField(verbose_name="메시지", default="")
    is_read = models.BooleanField(verbose_name="읽음 여부", default=False)
    type = models.IntegerField(verbose_name="메세지 타입", default=1)
    args = models.TextField(verbose_name="인자값", default=None, null=True, blank=True)


@receiver(post_save, sender=Message)
def update_latest_message(sender, instance, **kwargs):
    instance.room.update_latest_message()


class Meta:
    verbose_name_plural = "메시지 관리"
    verbose_name = "메시지 관리"

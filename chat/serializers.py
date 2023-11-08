from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.serializers import UserDetailSerializer, TagSetSerializer
from .models import Room, Message
from django.utils import timezone

class RoomWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def validate(self, data):
        print(data['relation'])
        if data['relation'] == data['relation2']:
            raise ValidationError('같은 사용자로 채팅을 열 수 없습니다.')

        if len(self.Meta.model.objects.filter(Q(relation=data["relation"],
                                                tagset=data["tagset"],
                                                relation2=data["relation2"],
                                                tagset2=data["tagset2"])
                                              | Q(relation2=data["relation"],
                                                  tagset2=data["tagset"],
                                                  relation=data["relation2"],
                                                  tagset=data["tagset2"]))) > 0:
            raise ValidationError('같은 사용자와 태그로 채팅을 열 수 없습니다.')
        return super().validate(data)

class RoomReservationTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('tagset', 'tagset2', 'reservation_time')
    
    def validate(self, data):
        if data['tagset'] == data['tagset2']:
            raise ValidationError('같은 태그로 예약 시간을 설정할 수 없습니다.')

        if data['reservation_time'] < timezone.localtime():
            raise ValidationError('지금보다 더 전으로 시간을 예약할 수 없습니다.')

        self.set_is_active(data)

        return super().validate(data)
    
    def set_is_active(self, data):
        room = self.Meta.model.objects.get(tagset=data["tagset"], tagset2=data["tagset2"])
        tagset = room.tagset
        tagset2 = room.tagset2
        tagset.is_active = False
        tagset2.is_active = False
        tagset.save()
        tagset2.save()
        self.send_create_message(room=room, data=data)
    
    def send_create_message(self, room, data):
        message = Message(room=room, type=2, args=data['reservation_time'], receiver=room.relation, sender=room.relation2, is_read=True)
        message.save()
    
class RoomSerializer(serializers.ModelSerializer):
    relation = UserDetailSerializer(read_only=True)
    relation2 = UserDetailSerializer(read_only=True)
    tagset = TagSetSerializer(read_only=True)
    tagset2 = TagSetSerializer(read_only=True)
    notice = serializers.SerializerMethodField(read_only=True)
    reservation_time = serializers.DateTimeField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_notice(self, obj):
        request = self.context.get("request")

        return obj.message_room.filter(receiver=request.user, is_read=False).count()


class MessageWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__' 
        

class MessageSerializer(serializers.ModelSerializer):
    sender = UserDetailSerializer(read_only=True)
    receiver = UserDetailSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

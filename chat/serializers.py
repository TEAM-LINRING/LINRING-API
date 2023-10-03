from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.serializers import UserDetailSerializer
from .models import Room, Message


class RoomWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def validate(self, data):
        if data['relation'] == data['relation2']:
            raise ValidationError('같은 사용자로 채팅을 열 수 없습니다.')
        return super().validate(data)


class RoomSerializer(serializers.ModelSerializer):
    relation = UserDetailSerializer(read_only=True)
    relation2 = UserDetailSerializer(read_only=True)
    notice = serializers.SerializerMethodField(read_only=True)

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

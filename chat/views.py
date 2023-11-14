import json

import firebase_admin
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Notification
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from utils.pagination import StandardResultsSetPagination
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer, MessageWritableSerializer, RoomWritableSerializer

from django.conf import settings


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['relation', 'relation2', 'relation__id', 'relation2__id']
    ordering_fields = [field.name for field in Room._meta.fields]
    ordering = ('created',)

    def get_queryset(self):
        queryset = Room.objects.filter(Q(relation=self.request.user.id) | Q(relation2=self.request.user.id))
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return RoomWritableSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        if settings.CHAT_UNIQUE_ROOM:
            chat = self.queryset.filter(
                Q(relation=request.data['relation']) & Q(relation2=request.data['relation2']) | Q(
                    relation2=request.data['relation']) & Q(relation=request.data['relation2']))
            if len(chat) > 0:
                serializer = self.get_serializer(chat[0])
                res_status = status.HTTP_200_OK
            else:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                serializer.save(relation=request.user)
                res_status = status.HTTP_201_CREATED

        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(relation=request.user)
            res_status = status.HTTP_201_CREATED

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=res_status, headers=headers)


def convertValueString(data: dict):
    ret = {}
    for key in data.keys():
        ret[key] = json.dumps(data[key])
    return ret


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room__id', 'room']
    ordering_fields = [field.name for field in Message._meta.fields]
    ordering = ('created',)

    def get_queryset(self):
        queryset = Message.objects.filter(Q(sender=self.request.user.id) | Q(receiver=self.request.user.id))
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return MessageWritableSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset.filter(receiver=self.request.user.id, is_read=False).update(is_read=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(sender=request.user)
        devices = FCMDevice.objects.filter(user=obj.receiver)

        for device in devices:
            device.send_message(
                firebase_admin.messaging.Message(
                    data=convertValueString(serializer.data),
                )
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

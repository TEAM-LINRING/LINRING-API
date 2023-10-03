"""
URL configuration for teatalk_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from dj_rest_auth.views import PasswordResetConfirmView
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from accounts.views import UserDetailsViewOverride, PasswordChangeView
from .views import RoomViewSet, MessageViewSet

# from gamept.views import RequestViewSet

router = routers.DefaultRouter()
router.register('room', RoomViewSet)
router.register('message', MessageViewSet)
urlpatterns = [
    path('', include(router.urls))
]

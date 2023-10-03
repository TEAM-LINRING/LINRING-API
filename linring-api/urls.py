"""
URL configuration for linring-api accounts.

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
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

schema_view = get_schema_view(
    openapi.Info(
        title="LINRING REST API",
        default_version="v1",
        description="LINRING REST API documents for developer",
        # terms_of_service="https://",
        # contact=openapi.Contact(name="", email=""),
        # license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

router.register('devices', FCMDeviceAuthorizedViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('accounts/', include('accounts.urls')),
        path('chat/', include('chat.urls')),
        path('health-check/', lambda request: JsonResponse({})),
        path('fcm/', include(router.urls))
    ])),
]
urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
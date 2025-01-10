
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import HttpResponse, render

from app.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

    path('403', lambda request: HttpResponse('403'), name='403'),
    path(
        'change_language/',
        lambda request: render(request, 'change_language.html'),
        name='change_language',
    ),

    path('index/', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('change_password/', change_password, name='change_password'),
    path('forget_password/', forget_password, name='forget_password'),
    path(
        'reset_password/<uidb64>/<token>/',
        reset_password,
        name = 'reset_password',
    ),

    path(
        'api_order_detail/<int:order_id>/',
        api_order_detail,
        name = 'api_order_detail'
    ),
]

urlpatterns += i18n_patterns(

    # prefix_default_language = False
)


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
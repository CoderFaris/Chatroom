from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('choice/', views.choice, name='choice'),
    path('chatroom/', views.chatroom, name='chatroom'),
    path('private-chat/', views.private_chat, name='private_chat'),
    path('upload/', views.FileUploadView.as_view(), name='file-upload')
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
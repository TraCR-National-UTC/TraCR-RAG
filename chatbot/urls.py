from django.urls import path
from . import views 

urlpatterns = [
    path('',views.index, name='index'),
    path("index/", views.index, name="index"),
    path("api/chat/", views.api_chat, name="api_chat"),
    path("api/chat/stream/", views.api_chat_stream, name="chat_sse"), # NEW
]
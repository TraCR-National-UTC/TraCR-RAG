from django.urls import path
from . import views 

urlpatterns = [
    # path('',views.chatbot, name='chatbot'),
    # path('tree-indexing/',views.chatbot_2, name='chatbot_2'),
    # path('alpha/',views.chatbot_turbo, name='chatbot_turbo'),
    # path('beta/',views.chatbot_beta, name='chatbot_beta'),
    # path('test/',views.test, name='test'),
    # path('static/<str:path>',views.test, name='static'),
    # path('static/',views.chatbot_turbo),
    path('turbo/',views.chatbot_turbo, name='chatbot_turbo'),
    path('',views.chatbot_titan, name='chatbot_titan'),
    path('test/',views.test, name='test'),
    path('npm/',views.npm, name='npm'),


]
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('send-message-stream/', views.send_message_stream_ndjson, name='send_message_stream'),
]

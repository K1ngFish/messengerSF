from django.urls import path
from . import views
from .views import chat_with_user, chat_with_group

urlpatterns = [
    path('send_message/', views.send_message, name='send_message'),
    path('create_chat_group/', views.create_chat_group, name='create_chat_group'),
    path('chat_with_user/<int:user_id>/', chat_with_user, name='chat_with_user'),
    path('edit_chat_group/<int:group_id>/', views.edit_chat_group, name='edit_chat_group'),
    path('delete_chat_group/<int:group_id>/', views.delete_chat_group, name='delete_chat_group'),
    path('user_chats/', views.get_user_chats, name='user_chats'),
    path('send_message_to_group/<int:group_id>/', views.send_message_to_group, name='send_message_to_group'),
    path('messages/', views.messages_page, name='messages_page'),
    path('create_chat_group_form/', views.create_chat_group_form, name='create_chat_group_form'),
    path('chat_with_group/<int:group_id>/', chat_with_group, name='chat_with_group'),
    path('edit_chat_group/<int:group_id>/', views.edit_chat_group, name='edit_chat_group'),

]

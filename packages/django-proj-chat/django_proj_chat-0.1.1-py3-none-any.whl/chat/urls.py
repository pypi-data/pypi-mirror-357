from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('messages/<int:recipient_id>/', views.messages_view, name='messages'),
]
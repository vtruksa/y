from django.urls import path, include
from . import views

urlpatterns = [
    path('api/get-conversation/', views.ConversationSerializer),
    path('api/follow/', views.follow),
    path('api/set-password/', views.password_change),
    path('api/del-user/', views.delUser),

    path('api/chat-get/', views.chat_get_create),
    path('api/send-message/', views.send_message),

    path('api/get-posts/', views.getPosts),
    path('api/get-posts/<str:tag>', views.getPosts),
    path('api/get-posts/<int:pk>', views.getPosts),
    path('api/post-post', views.postPost),
    path('api/like-post/', views.likePost),
    path('api/react-post/', views.reactPost),
    path('api/share-post/', views.sharePost),
    path('api/del-post/', views.delPost),
    path('api/block-tag/', views.blockTag),
    path('api/unblock-tag/', views.unblockTag),
]


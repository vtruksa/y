from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from user.views import loginView, registerView, logoutView, profileView, editProfileView, chat, settingsView
from post.views import viewTag
from .views import homeView, premiumView, aboutView, errorView
from .utils import runBgTasks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homeView, name='home'),

    path('login/', loginView, name='login'),
    path('register/', registerView, name='register'),
    path('logout/', logoutView, name='logout'),
    path('profile/<str:pk>/', profileView, name='profile'),
    path('profile-edit/', editProfileView, name="profile-edit"),
    path('settings/', settingsView, name="settings"),
    path('chat/', chat, name='chat'),
    path('about/', aboutView, name='about'),

    path('tag/<str:tag>/', viewTag, name='tag'),

    path('premium/', premiumView, name='premium'),
    path('error/', errorView, name='error'),

    path('api/bg_tasks/', runBgTasks),

    path('', include('api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
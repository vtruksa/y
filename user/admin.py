from django.contrib import admin
from .models import UserProfile, Conversation, ChatMessage, Address, UserProfileSettings

admin.site.register(UserProfile)
admin.site.register(UserProfileSettings)
admin.site.register(Conversation)
admin.site.register(ChatMessage)
admin.site.register(Address)
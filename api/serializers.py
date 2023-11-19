import datetime
from rest_framework import serializers
from django.contrib.auth.models import User

from user.models import Conversation, ChatMessage, UserProfile, UserProfileSettings
from user.utils import decrypt
from post.models import Post

class UserMiniSerializer(serializers.ModelSerializer):
    premium = serializers.SerializerMethodField()

    def get_premium(self, obj):
        sett = UserProfile.objects.get(user=obj)
        if sett.premium_id is None: return False
        return True

    class Meta:
        model = User
        fields = ['username', 'id', 'premium']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()

    def get_body(self, obj):
        return decrypt(open('api/prk.pem', 'rb').read(), obj.body)

    def get_sender(self, obj):
        return obj.sender.user.id if obj.sender else None

    class Meta:
        model = ChatMessage
        fields = '__all__'
        
class ConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        users = obj.users.all()
        return (str(users[0])+str(users[1]))

    class Meta:
        model = Conversation
        fields = '__all__'

# Smaller serializer for the 'reply_to'post
class PostSerializerNested(serializers.ModelSerializer):
    author = UserMiniSerializer()
    class Meta:
        model = Post
        fields = ['author', 'body', 'created', 'id']

class PostSerializer(serializers.ModelSerializer):
    reply_to = PostSerializerNested()
    author = UserMiniSerializer()

    class Meta:
        model = Post
        fields = '__all__'


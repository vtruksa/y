import os

from django.db import models
from django.contrib.auth.models import User
from django.utils import timesince
from .utils import get_upload_path_avatars

from post.models import Post, Tag

private_key = os.environ.get('CHAT_PRIVATE_KEY')
public_key = os.environ.get('CHAT_PUBLIC_KEY')

class UserProfile(models.Model):
    avatar = models.FileField(upload_to=get_upload_path_avatars, blank=True, null=True, default='/avatars/default.png')
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    _visibility = models.BigIntegerField(default=1)
    
    public = models.BooleanField(default=True)

    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following_u', blank=True)
    following_t = models.ManyToManyField(Tag, related_name='following_t', blank=True)
    conversations = models.ManyToManyField('Conversation', related_name="conversations")
    premium_time = models.DateField(null=True)
    premium_id = models.CharField(null=True, max_length=256)
    posts = models.ManyToManyField(Post, blank=True, editable=False)

    _puk = models.BinaryField(null=False, default=b'')
    _prk = models.BinaryField(null=False, default=b'')
    
    bio = models.TextField(max_length=5000, blank=True, null=True)
    address = models.ForeignKey('Address', null=True, on_delete=models.SET_NULL)
    birth_date = models.DateField(null=True)

    def __str__(self):
        return self.user.username + '\t' + str(self.id)

    @classmethod
    def add_posts():
        i = 0
        all_posts = Post.objects.all()
        for post in all_posts:
            prof = UserProfile.objects.get(id=post.author)
            if post not in prof.posts.all(): 
                prof.posts.add()
                prof.save()
            if i%500 == 0: print('Progress: ' + str(i*100/len(all_posts)))
            i+=1

    

class UserProfileSettings(models.Model):
    u = models.OneToOneField(User, on_delete=models.CASCADE, editable=False, null=True)

    notifications_follow = models.BooleanField(default=True)
    notifications_like = models.BooleanField(default=True)
    notifications_share = models.BooleanField(default=True)
    notifications_tags = models.BooleanField(default=True)
    notifications_message = models.BooleanField(default=True)

    notifications_to = models.EmailField(null=True)

    filter_explicit = models.BooleanField(default=True)
    filter_tag = models.ManyToManyField(Tag)


    # TODO
    def download_data(self):
        pass


class Conversation(models.Model):
    users = models.ManyToManyField(UserProfile, related_name='users', max_length=2)
    messages = models.ManyToManyField('ChatMessage', related_name='messages')
    created = models.DateTimeField(auto_now = True)
    photo = models.FileField(upload_to="", blank=True, null=True)

    def __str__(self):
        tmp = ""
        for u in self.users.all(): tmp += str(u)
        return tmp

    def get_name(self, user):
        for u in self.users.all(): 
            if u.user.username != user:
                return u.user.username


class ChatMessage(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    body = models.TextField()
    time_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body

    class Meta:
        ordering = ['-time_sent']

class Address(models.Model):
   country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
   region = models.ForeignKey('cities_light.Region', on_delete=models.SET_NULL, null=True, blank=True)
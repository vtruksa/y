from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timesince, timezone
from django.contrib.auth.models import User

from math import sqrt

class PostManager(models.Manager):
    def all(self, f_explicit=True, f_tag=[]):
        # # No filter, fetch all posts
        if not f_explicit: posts = super().all()        
        else: posts = super().exclude(profanity=True)

        if f_tag != []:
            f_tags = []
            # for ease of use of the method, check wether f_tag needs to be converted from a QuerySet to a Tag field
            if isinstance(f_tag, QuerySet):
                for t in f_tag: f_tags.append(t)
            else:
                f_tags = f_tag
            # exclude all posts including tags in f_tags
            posts = posts.exclude(tags_new__in = f_tags)

        return posts 


class Post(models.Model):
    _visibility = models.BigIntegerField(default=1, editable=False)
    body = models.TextField(max_length=256)
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='reply', editable=False)
    just_a_share = models.BooleanField(default=False, editable=False)
    liked = models.ManyToManyField(User, related_name='liked', editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    tags_new = models.ManyToManyField('Tag', related_name='tags', editable=True)

    profanity = models.BooleanField(default=False)

    # assign PostManager as the only object manager
    objects = PostManager()

    def __str__(self):
        return str(str(self.author) + ';'+ str(self.id))


class Tag(models.Model):
    _visibility = models.BigIntegerField(default=1 ,editable=False)
    tag = models.CharField(max_length=32, unique=True)
    posts = models.ManyToManyField(Post, blank=False)

    def __str__(self): return self.tag

    @staticmethod
    def detect_make_tags(tag_string):
        tag_string = str(tag_string)
        hashtags = [i for i, char in enumerate(tag_string) if char == '#']
        tags = []

        while len(hashtags) > 0:
            end = hashtags[0]+1
            print(hashtags[0])
            try:
                while tag_string[end].isalnum():
                    end+=1
            except:
                end=-1
            if end == -1: 
                tags.append(tag_string[hashtags[0]::]) 
            else: tags.append(tag_string[hashtags[0]:end])
            del hashtags[0]
        
        for tag in tags:
            tag = tag.replace('"', '')
            tag = tag.replace("'", '')

            try:
                t = Tag.objects.create(tag=tag)
            except Exception as e:
                t = Tag.objects.get(tag=tag)

            tag_string = tag_string.replace(tag, "<a href='"+reverse('tag', args=[tag.replace('#', '')])+"' class='tag'>" + tag + "</a>")

        return tag_string, tags

def delete_unused_tags():
    for tag in Tag.objects.all():
        if len(tag.posts.all()) == 0: 
            tag.delete()
            print('deleted: ' + str(tag))
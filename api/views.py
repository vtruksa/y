from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework.decorators import api_view

import base64, datetime

# Message encryption
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

# Own models
from .serializers import ConversationSerializer, PostSerializer
from user.models import Conversation, UserProfile, UserProfileSettings, ChatMessage
from user.utils import encrypt
from post.models import Post, Tag
from y import alg


def getConversaion(request, id):
    if not request.user.is_authenticated:
        return Response(data={'e':'You are trying to change a password when youre not logged in'}, status=401)
    try:
        convo = Conversation.objects.get(id=id)
        if UserProfile.objects.get(user=request.user) not in convo.users:
            return Response(data={'e':'You are trying to access somebody elses conversation'}, status=401)
    except:
        return Response(data={'e':'You are trying to access a conversation that doesnt exist'}, status=400)

    serializer = ConversationSerializer(convo)
    return Response(serializer.data)


# Status 411 = Couldnt reset the password
# TODO set a password change mail
@api_view(('POST', ))
def password_change(request):
    if not request.user.is_authenticated:
        return Response(data={'e':'You are trying to change a password when youre not logged in'}, status=401)
    try:
        # get the old and new passwords
        op = request.POST.get('op')
        np = request.POST.get('np')
        e = None
        # check the old password
        if not request.user.check_password(op):
            return Response(data={'e':'You entered the old password incorrectly'}, status=401)
        try: 
            # use django validation to validate and change the password
            validate_password(np)
            request.user.set_password(np)
            request.user.save()
            return Response(data={'message':'Success!'}, status=200)
        except Exception as e:
            return Response(data={'e':e}, status=411)
    except Exception as e:
        return Response(data={'e':'Unknown error: ' + str(e)}, status=400)

@api_view(('POST', ))
def follow(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to post a post without being logged in"}, status=401)

    try:
        followee = UserProfile.objects.get(id=request.POST.get('up_id'))
        follower = UserProfile.objects.get(user=request.user)
        # used to track whether this is a follow or an unfollow
        f = True
        if follower.user not in followee.followers.all():
            followee.followers.add(follower.user)
            follower.following.add(followee.user)
            # if UserProfileSettings.objects.get(u = followee.user).notifications_to != '':
            #     send_mail(
            #         subject="Y.COM - You have a new follower",
            #         message="Congratulations, " + follower.user.username + " is now following you on Y.COM!",
            #         from_email="y@y.com",
            #         recipient_list=[UserProfileSettings.objects.get(u = followee.user).notifications_to],
            #         fail_silently=False
            #     )
        else:
            followee.followers.remove(follower.user)
            follower.following.remove(followee.user)
            f = False
        followee.save()
        follower.save()
        alg.UserVisibility([followee])
        return Response(data={'follower':f}, status=200)
    except Exception as e:
        return Response(data={'e':e}, status=500)

@api_view(('GET',))
def getPosts(request, tag=None):
    # tracks the number of posts that have already been loaded
    l = int(request.GET.get('l'))

    if not request.user.is_authenticated:
        # return most popular posts
        posts = Post.objects.all().order_by('-_visibility')[l:l+20]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    profile = UserProfile.objects.get(user=request.user)
    settings = UserProfileSettings.objects.get(u=request.user)
    if tag != None:
        try:
            tag = '#'+tag
            posts = Tag.objects.get(tag=tag).posts.all(f_tag=settings.filter_tag.all(), f_explicit=settings.filter_explicit)
        except Exception as e:
            print('tag: '+ str(e))
            return Response(data={'exception':str(e)}, status=404)
    elif request.GET.get('user_p') != None:
        try:
            posts = UserProfile.objects.get(id=request.GET.get('user_p')).posts.all(f_tag=settings.filter_tag.all(), f_explicit=settings.filter_explicit)
        except Exception as e:
            print('user: '+ str(e))
            return Response(data={'exception':str(e)}, status=500)
    else:
        posts = Post.objects.all(f_tag=settings.filter_tag.all(), f_explicit=settings.filter_explicit)

    # show posts from followed people first
    posts = posts.annotate(
        followed_first = Case(
            *[When(author=author, then=Value(0)) for author in profile.following.all()],
            default=Value(1),
            output_field=IntegerField()
        )
    )

    # if the user is on users profile, sort posts by the time they were created, otherwise show followed users with the highest visibility posts first
    if request.GET.get('user_p') != None: posts = posts.order_by('-created')[l:l+20]
    else: posts = posts.order_by('followed_first', '-_visibility')[l:l+20]

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(('POST', ))
def postPost(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to post a post without being logged in"}, status=401)
    if request.user.is_authenticated:
        post = request.POST.get('post')

        # returns 'post' with <a> elements added around tags and 'tags' field that contains the tags in said post
        post, tags = Tag.detect_make_tags(post)

        p = Post.objects.create(
            body=post, 
            author=request.user,
        )
        up = UserProfile.objects.get(user = request.user)
        up.posts.add(p)
        up.save()

        # add the post to its Tag objects
        for t in tags:
            tag = Tag.objects.get(tag=t)
            tag.posts.add(p)
            tag.save()
            p.tags_new.add(tag)
            p.save()
        
        return Response(PostSerializer(p, many=False).data)

@api_view(('POST',))
def likePost(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to like a post without being logged in"}, status=401)
    if request.user.is_authenticated:
        if request.POST.get('id') != None:
            try: 
                p = Post.objects.get(id=request.POST.get('id'))
                user_in = request.user in p.liked.all()
                if user_in: p.liked.remove(request.user)
                else: p.liked.add(request.user)
                user_in = not user_in
                p.save()
                alg.PostVisibility([p])
                return Response({
                    'Liked':len(p.liked.all()),
                    'user_in':user_in
                })
            except Exception as e:
                return Response(data={'e':'An unknown error has occured'}, status=500)
        else: 
            return Response("You didn't specify the post you want to like")

@api_view(('POST', ))
def reactPost(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to react to a post without being logged in"}, status=401)
    try:
        post, tags = Tag.detect_make_tags(request.POST.get('commentary'))

        post = Post.objects.create(
            body=post,
            author=request.user,
            reply_to=Post.objects.get(id=request.POST.get('id')),
        )
        # recalculate the _visibility of the post that is being replied to
        alg.PostVisibility([post.reply_to])
        up = UserProfile.objects.get(user=request.user)
        up.posts.add(post)
        up.save()

        for t in tags:
            try:
                tag = Tag.objects.get(tag=t)
            except:
                tag = Tag.objects.create(tag=t)
            tag.posts.add(post)
            tag.save()
            post.tags_new.add(tag)
            post.save()

        post = PostSerializer(post).data
        
    except Exception as e:
        print(e)
        return Response(data={'e':str(e)}, status=500)
    
    return Response(data={'post':post}, status=200)

@api_view(('POST',))
def sharePost(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to share a post without being logged in"}, status=401)
    try:
        post = Post.objects.create(
            author=request.user,
            reply_to=Post.objects.get(id=request.POST.get('id')),
            just_a_share=True
        )
        up = UserProfile.objects.get(user=post.author)
        up.posts.add(post)
        up.save()
        alg.PostVisibility([post.reply_to])
        post = PostSerializer(post).data
    except Exception as e:
        return Response(data={'e':e}, status=500)
    
    return Response(data={'post':post}, status=200)

@api_view(('POST',))
def delPost(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to delete a post without being logged in"}, status=401)
    else:
        try: 
            id = request.POST.get('id')
            post = Post.objects.get(id=id)

            if request.user == post.author:
                post.delete()
                alg.UserVisibility(UserProfile.objects.get(user=request.user))
                return Response('Success deleting a post', status=200)
            else:
                return Response("You cannot delete somebody else's post", status=404)
        except:
            return Response("There was an unknown error deleting your post", status=500)

# TODO finish user deletion
@api_view(('POST', ))
def delUser(request):
    if not request.user.is_authenticated:
        return Response(data={'e':"You're trying to delete a post without being logged in"}, status=401)
    try:
        u = request.user
        u.delete()
        logout(request)
        return Response(status=200)
    except Exception as e:
        return Response(data={'e':"There was an error deleting your account: " + str(e)}, status=500)

@api_view(('GET', ))
def blockTag(request):
    if not request.user.is_authenticated:
        return Response(data={'e':'You are trying to block a tag when youre not logged in'}, status=401)

    sett = UserProfileSettings.objects.get(u=request.user.id)
    tag = Tag.objects.get(tag=request.GET.get('tag'))

    if tag not in sett.filter_tag.all(): sett.filter_tag.add(tag)
    return Response(data={}, status=200)

@api_view(('GET', ))
def unblockTag(request):
    if not request.user.is_authenticated:
        return Response(data={'e':'You are trying to unblock a tag when youre not logged in'}, status=401)
    sett = UserProfileSettings.objects.get(u=request.user.id)
    tag = Tag.objects.get(id=request.GET.get('tag'))

    if tag in sett.filter_tag.all(): sett.filter_tag.remove(tag)
    return Response(data={}, status=200)

@api_view(('POST', ))
def chat_get_create(request):
    convo = None

    if request.POST['id_type'] == 'user':
        to = UserProfile.objects.get(id = request.POST['id'])
        sender = UserProfile.objects.get(user = request.user)

        convo = Conversation.objects.create()
        convo.users.set([to, sender]) 
        convo.save()
        
        to.conversations.add(convo)
        sender.conversations.add(convo)
    else:
        convo = Conversation.objects.get(id=request.POST['id'])

    users = convo.users.all()
    data = ConversationSerializer(convo).data
    data['name'] = data['name'].replace(str(request.user), '')
    return Response(data)

@api_view(('POST', ))
def send_message(request):
    puk = open('api/puk.pem', 'r').read()
    
    data = {}
    message = ChatMessage.objects.create(
        sender = UserProfile.objects.get(user=request.user),
        conversation = Conversation.objects.get(id=request.POST['conversation_id']),
        body = encrypt(puk, request.POST['message'])
    )
    message.conversation.messages.add(message)

    return Response(status=200)
import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.http import JsonResponse
from django.db import models

from dotenv import load_dotenv
from PIL import Image

from .models import UserProfile, Conversation, ChatMessage
from .models import UserProfileSettings as up_settings
from .utils import crop_to_square, get_upload_path_avatars, delete_image
from .forms import LoginForm, RegisterForm, RegisterFormExtended, EditForm, EditFormExtended, UserProfileSettingsForm
from api.serializers import ConversationSerializer

def loginView(request):
    if request.user.is_authenticated:
        messages.success(request, 'You already are logged in')
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username.lower())
        except:
            print('Wrong username')
            messages.error(request, 'You entered a wrong username')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print('Wrong password')
            messages.error(request, 'You entered a wrong password')
    previous_url = request.META.get('HTTP_REFERER')
    context = {
        'site':'login',
        'form':LoginForm,
        'prev_url':previous_url
    }
    return render(request, 'login.html', context)

def registerView(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            user = User.objects.create_user(
                username=request.POST.get('username').lower(),
                password=request.POST.get('password'),
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),)
            login(request, user)

            profile = UserProfile.objects.create(
                user=user,
                bio=request.POST.get('bio'))
            return redirect('home')
        else:
            messages.error(request, 'There was an error during the registration proccess')
            if form.errors is not None:
                for e in form.errors:
                    messages.error(request, e)

    context = {
        'site':'register',
        'form':RegisterForm,
        'forme':RegisterFormExtended,
    }
    return render(request, 'register.html', context)

def logoutView(request):
    logout(request)
    return redirect('home')

def profileView(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view other user's profiles")
        return redirect('login')
    # Find user by 'pk' included in the URL
    try: 
        user = User.objects.get(id=pk)
    except:
        e = "We were unable to find the page you were searching for"
        return render(request, '_error.html', {'e':e})

    profile = UserProfile.objects.get(user=user)

    # Check wether the logged in user is friends with the viewed user
    try:
        current_user = UserProfile.objects.get(user=request.user)

        if user in current_user.following.all():
            follows = True
        else:
            follows = False
    except Exception as e:
        e = "We're sorry, but there was an unexpected error during the loading process"
        return render(request, '_error.html', {'e':e})

    posts = profile.posts.all()

    context = {
        'user':user,
        'profile':profile,
        'follows':follows,
        'posts':posts,
    }

    return render(request, 'user.html', context)

def editProfileView(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to edit your profile")
        return redirect('login')
    u = User.objects.get(id=request.user.id)
    try:
        u2 = UserProfile.objects.get(user=u)
    except:
        u2 = UserProfile.objects.create(user=u)

    if request.method == 'POST':
        try:
            avatar = request.FILES['avatar']
            # Open the uploaded image
            img = Image.open(avatar)

            # Crop the image to a square
            img = crop_to_square(img)

            delete_image(u2.avatar.url)

            # Save the cropped image
            img.save(os.path.join('media/', get_upload_path_avatars(request, avatar.name)))
            u2.avatar = os.path.join('avatars', str(request.user.id) + '_avatar.' + avatar.name.split('.')[-1])
        except:
            avatar = u2.avatar

        u.username = request.POST.get('username').lower()
        u.email = request.POST.get('email')
        u.first_name = request.POST.get('first_name')
        u.last_name = request.POST.get('last_name')
        u2.bio = request.POST.get('bio')
        u.save()
        u2.save()

        previous_url = request.META['HTTP_REFERER']
        return redirect('/profile/'+str(request.user.id)+'/')
   
    form = EditForm(instance=u)
    form2 = EditFormExtended(instance=u2)
    context = {
        'form':form,
        'form2':form2
    }
    return render(request, 'user_edit.html', context)

def chat(request):
    if not request.user.is_authenticated:
        messages.error(request, "Can't access chats when you're not logged in")
        return redirect('login')

    
    profile = UserProfile.objects.get(user = request.user)
    convos = UserProfile.objects.get(user=request.user).conversations.all()

    # changes the converstaion name format
    exclude_from_new_chat = [profile.id]

    for convo in convos:
        users = convo.users.all()
        convo.name = convo.get_name(request.user.username)
        user = convo.users.exclude(user=request.user).first()
        exclude_from_new_chat.append(user.id)
    message_to = UserProfile.objects.exclude(id__in = exclude_from_new_chat)


    open_chat = None
    if convos: open_chat = convos.first().id

    context = {
        'open_chat': open_chat,
        'convos':convos,
        'message_to':message_to,
    }
    return render(request, 'chats.html', context)

def settingsView(request):
    if not request.user.is_authenticated:
        messages.error(request, "Can't access settings when you're not logged in")
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)
    settings = up_settings.objects.get(u=request.user)
    
    if request.method == 'POST':
        # The checkboxes return values 'on' and 'None' instead of True and False for some reason
        # Once repaired, this function can be deleted
        def onToTrue(transform):
            if transform == None: return False
            else: return True

        settings.notifications_follow = onToTrue(request.POST.get('notifications_follow'))
        settings.notifications_like = onToTrue(request.POST.get('notifications_like'))
        settings.notifications_share = onToTrue(request.POST.get('notifications_share'))
        settings.notifications_tags = onToTrue(request.POST.get('notifications_tags'))
        settings.notifications_message = onToTrue(request.POST.get('notifications_message'))
        settings.notifications_to = request.POST.get('notifications_to')
        settings.filter_explicit = onToTrue(request.POST.get('filter_explicit'))
        settings.save()


    form = UserProfileSettingsForm(instance=settings)
    context = {
        'form':form,
        'tags':settings.filter_tag.all()
    }

    return render(request, 'settings.html', context)
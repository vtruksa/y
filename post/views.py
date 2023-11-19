from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from .models import Post, Tag

def viewTag(request, tag):
    if not request.user.is_authenticated:
        messages.error(request, "Can't view tags if you're not logged in!")
        return redirect('login')

    if tag[0] != '#': tag = '#' + tag

    try:
        obj = Tag.objects.get(tag=tag)
        context = {
            'tag':obj,
        }
        return render(request, 'tag.html', context)
    except Exception as e:
        e = "We're sorry, but there we couldn't find the tag you're searching for"
        return render(request, '_error.html', {'e':e})

    return render(request, 'tag.html', context)
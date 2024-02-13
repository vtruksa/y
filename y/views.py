from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import models
import stripe

from post.models import Post, Tag
from user.models import UserProfile
from .forms import CardForm
from .utils import create_payment_charge
from y.settings import STRIPE_SECRET_KEY

def homeView(request):
    popular_tags = Tag.objects.all().order_by('-_visibility')[:5]

    context = {
        'poptags': popular_tags,
    }
    return render(request, 'home.html', context)

stripe.api_key = STRIPE_SECRET_KEY

def errorView(request):
    context = {}
    return render(request, '_error.html', context)

def premiumView(request):        
    if not request.user.is_authenticated:
        messages.error(request, "Can't access Y.PREMIUM when you're not logged in")
        return redirect('login')
    
    user = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        card = request.POST.get('card-number')
        exp_month = request.POST.get('exp_m')
        exp_year = request.POST.get('exp_yr')
        cvc = request.POST.get('cvc')
        # Create stripe payment intent
        payment= stripe.PaymentIntent.create(
            amount=500,
            currency="gbp",
            payment_method="pm_card_visa",
        )

        user.premium_time = timezone.now() + relativedelta(months=1)
        user.premium_id = payment.id

        user.save()

        payment.confirm(return_url='http://127.0.0.1:8000/premium/')

    form = CardForm()
    
    context = {
        'form':form,
        'user':user
    }

    return render(request, 'premium.html', context)

def aboutView(request): return render(request, 'about.html', {})
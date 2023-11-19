import stripe
import traceback

from django.http import JsonResponse

from .bg_tasks import *

def create_payment_charge(tokenid,amount):

    payment = stripe.Charge.create(
                amount= int(amount)*100,                  # convert amount to cents
                currency='usd',
                description='Example charge',
                source=tokenid,
                )

    payment_check = payment['paid']    # return True for successfull payment

    return payment_check

def runBgTasks(request):
    try:
        checkPremiums(repeat=86400)
        recalculateVisibilities(repeat=43200)
        
        return JsonResponse({}, status=200)
    except Exception as e:
        return JsonResponse({"e":traceback.format_exc()}, status=400)
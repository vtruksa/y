from datetime import timedelta, datetime

from background_task import background
from user.models import UserProfile
from y import alg

import threading

# cancel expired premiums
@background()
def checkPremiums():
    print('running premiums check')
    users = UserProfile.objects.all()
    timenow = datetime.now().date()
    for user in users:
        # if the premium is expired, set all premium variables to none
        if user.premium_time != None:
            if (timenow - user.premium_time).days >= 31:
                user.premium_time = None
                user.premium_id = None
                user.save()



# recalculate visibilities
@background()
def recalculateVisibilities():
    print('recalculating all visibilities')
    # post visibility calls uservisibility() and tagvisibility() inside
    alg.PostVisibility()

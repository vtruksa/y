from django.test import Client
from y.views import *
from tests.test_user import YTestCase

from django.contrib.auth.models import User

class YViewsTest(YTestCase):
    def test_home_view(self):
        self.login()
        res = self.c.get('/')
        self.assertEquals(res.status_code, 200)

    def test_premium_view(self):
        self.login()
        res = self.c.post('/premium/', {
            'card-number':4242424242424242,
            'exp_m':10,
            'exp_yr':2028,
            'cvc':999
        })
        self.assertEquals(res.status_code, 200)

    def test_premium_view_wrong(self):
        self.login()
        res = self.c.post('/premium/', {
            'card-number':844,
            'exp_m':10,
            'exp_yr':2020,
            'cvc':999
        })
        print(res.context)
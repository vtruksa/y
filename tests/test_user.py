from django.test import TestCase
from django.test import Client
from user.models import UserProfile, UserProfileSettings
from user.views import *

from django.contrib.auth.models import User

class YTestCase(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create(
            user = User.objects.create(
                username='usernumber1',
                email='mail1@y.com'
            )
        )
        self.u1.user.set_password('pass')
        self.u1.user.save()

        self.c = Client()

    def login(self):
        self.c.post('/login/', {'username':self.u1.user.username, 'password':'pass'}, follow=True)

class UserTest(YTestCase):
    def test_login_wrong(self):
        res = self.c.post('/login/', {'username':self.u1.user.username, 'password':''})
        self.assertFalse(res.context['user'].is_authenticated)

    def test_login_correct(self):
        res = self.c.post('/login/', {'username':self.u1.user.username, 'password':'pass'}, follow=True)
        self.assertTrue(res.context['user'].is_authenticated)

    def test_register(self):
        res = self.c.post('/register/', {
            'username':'user0',
            'password':'pass',
            'email':'m@mmm.com',
            'first_name':'User',
            'last_name':'Test'
        })
        try:
            u = User.objects.get(username='user0')
            u_p = UserProfile.objects.get(user=u)
            u_s = UserProfileSettings(u=u)
        except: raise AssertionError
        self.assertIsNotNone(u)
        self.assertIsNotNone(u_p)
        self.assertIsNotNone(u_s)

    def test_profile_view_unlogged(self):
        res = self.c.get(f'/profile/{self.u1.user.id}/')
        self.assertEqual(res.url, '/login/')

    def test_profile_view_logged(self):
        self.c.post('/login/', {'username':self.u1.user.username, 'password':'pass'}, follow=True)
        res = self.c.get(f'/profile/{self.u1.user.id}/')
        self.assertEqual(res.status_code, 200)
        
    def test_profile_wrong_id(self):
        self.c.post('/login/', {'username':self.u1.user.username, 'password':'pass'}, follow=True)
        res = self.c.get('/profile/9/', follow=True)
        self.assertEqual(res.context['e'], 'We were unable to find the page you were searching for')

    def test_profile_edit_unlogged(self):
        res = self.c.get(f'/profile-edit/')
        self.assertEqual(res.url, '/login/')

    def test_profile_edit(self):
        self.c.post('/login/', {'username':self.u1.user.username, 'password':'pass'}, follow=True)
        res = self.c.post('/profile-edit/', {
            'username':'usernumber1',
            'email':'mail1@y.com',
            'first_name':'User',
            'last_name':'Testy',
            'bio':'bio'
        })
        u = User.objects.get(username=self.u1.user.username)
        self.assertEqual(u.last_name, 'Testy')

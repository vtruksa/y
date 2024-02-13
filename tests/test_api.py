from django.test import TestCase, Client
from rest_framework.test import APIRequestFactory, force_authenticate
from user.models import UserProfile, UserProfileSettings
from post.models import Post, Tag
from api.views import *

class APITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='user',
            email='mail@mail.com'
        )  
        self.user.set_password('pass')
        self.user.save() 

        self.user2 = User.objects.create(
            username='user2',
            email='mail2@mail.com'
        )
        self.user2.set_password('pass')
        self.user2.save()

        self.up = UserProfile.objects.create(user=self.user)
        self.up2 = UserProfile.objects.create(user=self.user2)
        self.ups = UserProfileSettings.objects.create(u=self.user)
        self.ups2 = UserProfileSettings.objects.create(u=self.user2)

        self.factory = APIRequestFactory()

    def test_password_change(self):
        req = self.factory.post(
            '/api/set-password/',
            {
                'op':'pass',
                'np':'pass2#2ssap'
            }
        )
        force_authenticate(req, user=self.user)
        res = password_change(req)
        self.assertEquals(res.status_code, 200)
        self.assertTrue(User.objects.get(username='user').check_password('pass2#2ssap'))

    def test_password_change_wrong_pass(self):
        req = self.factory.post(
            '/api/set-password/',
            {
                'op':'pas',
                'np':'pass2#2ssap'
            }
        )
        force_authenticate(req, user=self.user)
        res = password_change(req)
        self.assertEquals(res.status_code, 401)

    def test_follow(self):
        req = self.factory.post('/api/follow/', {'up_id':self.up2.id})
        force_authenticate(req, user=self.user)
        res = follow(req)
        self.assertEquals(res.status_code, 200)

    def test_follow_wrong_followee(self):
        req = self.factory.post('/api/follow/', {'up_id':72})
        force_authenticate(req, user=self.user)
        res = follow(req)
        self.assertEquals(res.status_code, 500)

    def __post(self, post):
        req = self.factory.post('/api/post-post/', {'post':post})
        force_authenticate(req, user=self.user)
        return postPost(req)

    def test_post_post(self):
        res = self.__post('Test post')
        if len(Post.objects.all()) > 0: assert True
        else: raise AssertionError

    def test_get_post(self):
        self.__post('Test post')
        req = self.factory.get('/api/get-posts/', {'l':0})
        force_authenticate(req, self.user)
        res = getPosts(req)
        self.assertEquals(len(res.data), 1)

    def test_get_post_user(self):
        self.__post('Test Post')
        # Check the user who posted
        req = self.factory.get('/api/get-posts/', {'l':0, 'user_p':self.up.id})
        force_authenticate(req, self.user)
        res1 = getPosts(req)
    	# Check the empty user
        req = self.factory.get('/api/get-posts/', {'l':0, 'user_p':self.up2.id})
        force_authenticate(req, self.user)
        res2 = getPosts(req)

        self.assertEquals(len(res1.data), 1)
        self.assertEquals(len(res2.data), 0)

    def test_hashtag_detection(self):
        self.__post('#test #post')
        tags = Tag.objects.all()
        self.assertEquals(len(tags), 2)

    def test_hashtag_load(self):
        self.__post('#tag #on #post')
        req = self.factory.get('/api/get-posts/', {'l':0, 'tag':'tag'})
        force_authenticate(req, self.user)
        res = getPosts(req)
        self.assertEquals(len(res.data), 1)

    def test_like_post(self):
        self.__post('Test post')
        req = self.factory.post('/api/like-post/', {'id':Post.objects.all()[0].id})
        force_authenticate(req, user=self.user)
        res = likePost(req)
        self.assertEquals(res.data['Liked'], 1)

    def test_react_post(self):
        self.__post('Test post')
        req = self.factory.post('/api/react-post/', {'commentary':'Test comment', 'id':Post.objects.all()[0].id})
        force_authenticate(req, user=self.user2)
        res = reactPost(req)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(Post.objects.all()), 2)

    def test_share_post(self):
        self.__post('Test post')
        req = self.factory.post('/api/share-post/', {'id':Post.objects.all()[0].id})
        force_authenticate(req, user=self.user2)
        res = sharePost(req)
        self.assertEquals(len(Post.objects.all()), 2)

    def test_del_post(self):
        self.__post('Test post')
        req = self.factory.post('/api/del-post/', {'id':Post.objects.all()[0].id})
        force_authenticate(req, user=self.user)
        res = delPost(req)
        print(res)
        print(res.data)
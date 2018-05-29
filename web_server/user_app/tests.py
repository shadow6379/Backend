import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from user_app import models

# Create your tests here.


class RegistryTestCase(TestCase):
    def setUp(self):
        pass

    def test_registry(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
            'email': '15975129956@139.com'
        }
        response = client.post('/user_app/registry/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'username': 'test',
            'password': '12345678',
            'email': '15975129956@139.com'
        }
        response = client.post('/user_app/registry/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'test',
            'password': '123456',
            'email': '15975129956@163.com'
        }
        response = client.post('/user_app/registry/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'te',
            'password': '123',
            'email': '15975129956@139.com'
        }
        response = client.post('/user_app/registry/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )

    def test_login(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        response = client.post('/user_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'username': 'test',
            'password': '123',
        }
        response = client.post('/user_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'te',
            'password': '123456',
        }
        response = client.post('/user_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'te',
            'password': '123',
        }
        response = client.post('/user_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class LogoutTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )

    def test_logout(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/user_app/login/', request)
        response = client.post('/user_app/logout/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')


class CategoryTestCase(TestCase):
    def setUp(self):
        models.TypeInfo.objects.create(name='computer')

        for i in range(1, 10):
            obj = models.BookInfo(
                name='name%s' % i,
                author='author%s' % i,
                brief='brief%s' % i,
                ISBN='ISBN%s' % i,
                publish_time='publish time %s' % i,
                press='press%s' % i,
                contents='contents%s' % i,
            )
            obj.save()
            obj.types.set([1])

    def test_category(self):
        client = Client()

        response = client.get('/user_app/category/1_3-5/')
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        response = client.get('/user_app/category/2_3-5/')
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class DetailTestCase(TestCase):
    def setUp(self):
        CategoryTestCase.setUp(TestCase)

    def test_detail(self):
        client = Client()

        response = client.get('/user_app/detail/5/')
        # print(json.loads(response.content.decode())['msg'])
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        response = client.get('/user_app/detail/11/')
        # print(json.loads(response.content.decode())['msg'])
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class CollectBookTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )
        user = User.objects.filter(username='test').first()
        models.UserInfo.objects.create(
            user=user,
        )
        models.BookInfo.objects.create(
            name='name',
            author='author',
            brief='brief',
            ISBN='ISBN',
            publish_time='publish time',
            press='press',
            contents='contents',
        )

    def test_collect_book(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/user_app/login/', request)

        request = {
            'bid': '1',
        }
        response = client.post("/user_app/collect_book/", request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'bid': '3',
        }
        response = client.post("/user_app/collect_book/", request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class RetrieveTestCase(TestCase):
    def setUp(self):
        CategoryTestCase.setUp(TestCase)

    def test_retrieve(self):
        client = Client()
        # Accurate matching
        request = {
            'key': 'name'
        }
        response = client.post('/user_app/retrieve/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        # fuzzy matching
        request = {
            'key': 'auth'
        }
        response = client.post('/user_app/retrieve/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        # failed matching
        request = {
            'key': 'failed'
        }
        response = client.post('/user_app/retrieve/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failed')


class UserProfileTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )
        models.UserInfo.objects.create(user=user)

    def test_user_profile(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }

        request_new = {
            'other': 'very handsome',
            'old_password': '123456',
            'new_password': '1234567890',
        }
        client.post('/user_app/login/', request)

        # test get method, have user
        response = client.get('/user_app/user_profile/1/')
        # print(response.content.decode())
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        # test get method, have user
        response = client.get('/user_app/user_profile/2/')
        # print(response.content.decode())
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        # test post method, change nothing
        response = client.post('/user_app/user_profile/1/')
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        # test post method, change password
        response = client.post('/user_app/user_profile/1/', request_new)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        # after change password, login failure by old password
        response = client.post('/user_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')
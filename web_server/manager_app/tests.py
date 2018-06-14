import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from manager_app import models
from user_app import models as tmp

# Create your tests here.


class LoginTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
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
        response = client.post('/manager_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'username': 'test',
            'password': '123',
        }
        response = client.post('/manager_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'te',
            'password': '123456',
        }
        response = client.post('/manager_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'username': 'te',
            'password': '123',
        }
        response = client.post('/manager_app/login/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class LogoutTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
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
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/logout/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        response = client.post('/manager_app/logout/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')


class ManagerInfoTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
            username='test',
            password='123456',
            email='test@163.com',
        )

    def test_manager_info(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/manager_info/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        response = client.post('/manager_app/manager_info/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class ReportInfoBoxTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
            username='test',
            password='123456',
            email='test@163.com',
        )

        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )
        user = User.objects.filter(username='test').first()
        u = tmp.UserInfo.objects.create(
            user=user,
        )
        u.save()

        b = tmp.BookInfo(
            name='name',
            author='author',
            brief='brief',
            ISBN='ISBN',
            publish_time='publish time',
            press='press',
            contents='contents',
        )
        b.save()

        c = tmp.Comment(
            uid=u,
            bid=b,
            content='MySQL, Redis'
        )
        c.save()

        tmp.AttitudeRecord.objects.create(
            cid=c,
            uid=u,
            attitude=2,
            report_reason=4,
        )

    def test_get(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/report_info_box/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

    def test_post(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {
            'protocol': '1',
            'cid': '1',
        }
        response = client.post('/manager_app/report_info_box/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'protocol': '0',
            'cid': '1',
        }
        response = client.post('/manager_app/report_info_box/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'protocol': '2',
            'cid': '1',
        }
        response = client.post('/manager_app/report_info_box/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class InventoryManagementTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
            username='test',
            password='123456',
            email='test@163.com',
        )

        tmp.TypeInfo.objects.create(
            name='computer'
        )

        book = tmp.BookInfo(
            name='name',
            author='author',
            brief='brief',
            ISBN='ISBN',
            publish_time='publish time',
            press='press',
            contents='contents',
        )
        book.save()
        book.types.set([1])
        book.save()

        tmp.BookInstance.objects.create(
            bid=book,
            state=0,
        )

    def test_get(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/inventory_management/?key=ISBN', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {}
        response = client.get('/manager_app/inventory_management/?key=name', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {}
        response = client.get('/manager_app/inventory_management/?key=author', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {}
        response = client.get('/manager_app/inventory_management/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

    def test_post(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {
            'protocol': '0',
            'msg': {
                'cover': '',
                'name': '',
                'author': '',
                'brief': '',
                'ISBN': 'test',
                'publish_time': '',
                'press': '',
                'contents': '',
                'inventory': '2',
                'types': {},
            },
        }
        request['msg']['types'] = json.dumps(request['msg']['types'])
        request['msg'] = json.dumps(request['msg'])
        response = client.post('/manager_app/inventory_management/', request)
        print(json.loads(response.content.decode())['error_msg'])
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'protocol': '0',
            'msg': {
                'cover': '',
                'name': '',
                'author': '',
                'brief': '',
                'ISBN': 'test',
                'publish_time': '',
                'press': '',
                'contents': '',
                'inventory': '2',
                'types': {},
            },
        }
        request['msg']['types'] = json.dumps(request['msg']['types'])
        request['msg'] = json.dumps(request['msg'])
        response = client.post('/manager_app/inventory_management/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {
            'protocol': '1',
            'msg': {
                'cover': '',
                'name': '',
                'author': '',
                'brief': '',
                'ISBN': 'ISBN',
                'publish_time': '',
                'press': '',
                'contents': '',
                'inventory': '2',
                'types': {},
            },
        }
        request['msg']['types'] = json.dumps(request['msg']['types'])
        request['msg'] = json.dumps(request['msg'])
        response = client.post('/manager_app/inventory_management/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')


class DebitTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
            username='test',
            password='123456',
            email='test@163.com',
        )

        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )
        user = User.objects.filter(username='test').first()
        tmp.UserInfo.objects.create(
            user=user,
        )

        tmp.BookInfo.objects.create(
            name='name',
            author='author',
            brief='brief',
            ISBN='ISBN',
            publish_time='publish time',
            press='press',
            contents='contents',
        )

        tmp.BookInstance.objects.create(
            bid=tmp.BookInfo.objects.filter(id=1).first(),
            state=0,
        )

        tmp.ActiveRecord.objects.create(
            uid=tmp.UserInfo.objects.filter(id=1).first(),
            bid=tmp.BookInstance.objects.filter(id=1).first(),
            active=0,
        )

    def test_get(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/debit/?username=test', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {}
        response = client.get('/manager_app/debit/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

    def test_post(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = dict()
        request['msg'] = json.dumps({'username': 'test', 'bid': '1'})
        response = client.post('/manager_app/debit/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        response = client.post('/manager_app/debit/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')


class ReturnTestCase(TestCase):
    def setUp(self):
        models.ManagerInfo.objects.create(
            username='test',
            password='123456',
            email='test@163.com',
        )

        User.objects.create_user(
            username='test',
            password='123456',
            email='test@163.com',
        )
        user = User.objects.filter(username='test').first()
        tmp.UserInfo.objects.create(
            user=user,
        )

        tmp.BookInfo.objects.create(
            name='name',
            author='author',
            brief='brief',
            ISBN='ISBN',
            publish_time='publish time',
            press='press',
            contents='contents',
        )

        tmp.BookInstance.objects.create(
            bid=tmp.BookInfo.objects.filter(id=1).first(),
            state=0,
        )

        tmp.ActiveRecord.objects.create(
            uid=tmp.UserInfo.objects.filter(id=1).first(),
            bid=tmp.BookInstance.objects.filter(id=1).first(),
            active=1,
        )

    def test_get(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {}
        response = client.get('/manager_app/return/?username=test', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {}
        response = client.get('/manager_app/return/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

    def test_post(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {
            'rid': '1',
        }
        response = client.post('/manager_app/return/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'success')

        request = {
            'rid': '1',
        }
        response = client.post('/manager_app/return/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

        request = {}
        response = client.post('/manager_app/return/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

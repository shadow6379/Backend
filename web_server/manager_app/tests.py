import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from manager_app import models

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

    def test_post(self):
        client = Client()

        request = {
            'username': 'test',
            'password': '123456',
        }
        client.post('/manager_app/login/', request)

        request = {
            'protocol': '2',
            'cid': '1',
        }
        response = client.post('/manager_app/report_info_box/', request)
        self.assertEqual(json.loads(response.content.decode())['status'], 'failure')

from django.test import TestCase
import json
from django.test import Client
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

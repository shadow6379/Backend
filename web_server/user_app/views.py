from django.shortcuts import render
from django.contrib.auth import login as login_confirm
from django.contrib.auth import logout as logout_confirm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from django.views import View

# Create your views here.


def registry(request):
    pass


def login(request):
    pass


def logout(request):
    pass


def category(request, cid, begin, end):
    pass


def detail(request, bid):
    pass


def collect_book(request):
    pass


def subscribe_book(request):
    pass


def star_book(request):
    pass


class CommentSection(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(CommentSection, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class UserProfile(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(UserProfile, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


def retrieve(request):
    pass

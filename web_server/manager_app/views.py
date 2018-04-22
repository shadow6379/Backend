from django.shortcuts import render
from django.views import View

# Create your views here.


def login(request):
    pass


def logout(request):
    pass


def manager_info(request):
    pass


class ReportInfoBox(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(ReportInfoBox, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class InventoryManagement(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(InventoryManagement, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Debit(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(Debit, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Return(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(Return, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


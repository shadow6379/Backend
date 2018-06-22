from django.conf.urls import url

from manager_app import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^manager_info/$', views.manager_info),
    url(r'^report_info_box/$', views.ReportInfoBox.as_view()),
    url(r'^type_management/$', views.TypeManagement.as_view()),
    url(r'^inventory_management/$', views.InventoryManagement.as_view()),
    url(r'^debit/$', views.Debit.as_view()),
    url(r'^return/$', views.Return.as_view()),
]

from django.conf.urls import url

from user_app import views

urlpatterns = [
    url(r'^registry/$', views.registry),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^category/(?P<cid>\d+)_(?P<begin>\d+)-(?P<end>\d+)/$', views.category),
    url(r'^detail/(?P<bid>\d+)/$', views.detail),
    url(r'^collect_book/$', views.collect_book),
    url(r'^subscribe_book/$', views.subscribe_book),
    url(r'^star_book/$', views.star_book),
    url(r'^comment_section/(?P<bid>\d+)/$', views.CommentSection.as_view()),
    url(r'^user_profile/(?P<uid>\d+)/$', views.UserProfile.as_view()),
    url(r'^retrieve/$', views.retrieve),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$',views.active_user),
]

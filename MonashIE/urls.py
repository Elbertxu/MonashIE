"""MonashIE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.landing, name='landing'),
    url(r'^quests/$', views.quest_list, name='quest_list'),
    url(r'^quest/(?P<pk>\d+)/$', views.quest_detail, name='quest_detail'),
    url(r'^quest/new/$', views.quest_new, name='quest_new'),
    url(r'^quest/(?P<pk>\d+)/create_event/$', views.create_event, name='create_event'),
    url(r'^quest/create_organizer/$', views.create_organizer, name='create_organizer'),
    url(r'^quest/(?P<pk>\d+)/edit/$', views.quest_edit, name='quest_edit'),
    url(r'^quest/(?P<pk>\d+)/edit_organizer/$', views.quest_organizer, name='quest_organizer'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='landing.html'), name='logour'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^notification/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$', views.notification, name='notification'),
    url(r'^activated/$', views.activated, name='activated'),
    url(r'^events/(?P<pk>\d+)/$', views.event_detail, name='event_detail'),
    url(r'^organizers/$', views.organizer_list, name='organizer_list'),
    url(r'^events/(?P<pk>\d+)/evaluation_new/$', views.evaluation_new, name='evaluation_new'),
    url(r'^quest/(?P<pk>\d+)/reviewed/$', views.set_reviewed, name='set_reviewed'),
    url(r'^quest/(?P<pk>\d+)/accepted/$', views.set_accepted, name='set_accepted'),
    url(r'^result/$', views.search, name='result'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag_view'),
    url(r'^password_reset/$', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_complete'),
]

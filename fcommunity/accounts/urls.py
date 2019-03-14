from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', LoginView.as_view(template_name="accounts/login.html"), name = "login"),
    url(r'^logout/$', LogoutView.as_view(template_name="accounts/logout.html"), name = "logout"),
    url(r'^register/$', views.register, name = 'register'),
    url(r'^new_ground/$', views.new_ground, name = 'new_ground'),
    url(r'^profile/$', views.profile, name = 'profile'),
    url(r'^all_teams/$', views.all_teams, name = 'all_teams'),
    url(r'^all_comps/$', views.all_comps, name = 'all_comps'),
    url(r'^all_grounds/$', views.all_grounds, name = 'all_grounds'),
    url(r'^all_usrs/$', views.all_usrs, name = 'all_usrs'),
    url(r'^team/(?P<pk>\d+)/$', views.team_profile, name = 'team_profile'),
    url(r'^team/(?P<pk>\d+)/history/$', views.team_history, name = 'team_history'),
    url(r'^comp/(?P<pk>\d+)/$', views.comp_profile, name = 'comp_profile'),
    url(r'^ground/(?P<pk>\d+)/$', views.ground_profile, name = 'ground_profile'),
    url(r'^profile/(?P<pk>\d+)/$', views.user_profile, name = 'user_profile'),
    url(r'ground/(?P<pk>\d+)/comment/$', views.add_comment_to_ground, name='add_comment_to_ground'),
]
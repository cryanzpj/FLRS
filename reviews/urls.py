from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /
    url(r'^$', views.review_list, name='review_list'),
    # ex: /review/5/
    url(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    # ex: /paper/
    url(r'^paper$', views.paper_list, name='paper_list'),
    # ex: /paper/5/
    url(r'^paper/(?P<paper_recid>[0-9]+)/$', views.paper_detail, name='paper_detail'),
    url(r'^paper/(?P<paper_recid>[0-9]+)/add_review/$', views.add_review, name='add_review'),
    url(r'^review/user/(?P<username>\w+)/$', views.user_review_list, name='user_review_list'),
    url(r'^review/user/$', views.user_review_list, name='user_review_list'),
    url(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),
    url(r'^paper/similar_(?P<paper_recid>[0-9]+)/$', views.show_similar_paper, name='show_similar_paper'),
    url(r'^search/$', views.search,name = 'search')
]
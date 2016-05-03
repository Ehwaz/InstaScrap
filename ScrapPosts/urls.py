from django.conf.urls import url

from . import views

app_name = 'ScrapPosts'
urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^crawl_posts/', views.crawl_posts, name='crawl'),
    url(r'^liked_posts/', views.liked_posts, name='liked'),
    url(r'^scrapped_posts/', views.scrapped_posts, name='scrapped'),
    url(r'^submit_access_token/', views.submit_access_token, name='submit_access_token'),
    url(r'^set_access_token/', views.set_access_token, name='set_access_token'),
    url(r'^get_post/', views.get_post, name='get_post'),
    url(r'^load_more_posts/', views.load_more_posts, name='load_more_posts'),
    url(r'^change_scrap_state/', views.change_scrap_state, name='change_scrap_state'),
]

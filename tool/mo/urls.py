from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.index, name='index'),
    path('scraping', views.start_scraping, name='scraper'),
    path('upload', views.upload, name='upload')
]
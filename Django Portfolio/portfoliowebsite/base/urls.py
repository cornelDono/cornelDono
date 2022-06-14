from django.urls import path
from . import views 

urlpatterns = [
    path('', views.homePage, name='home'),
    path('project/<uuid:pk>', views.projectPage, name='project'),
    path('pbiProject', views.pbiProjectPage, name='pbiProject'),
]

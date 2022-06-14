from xml.etree.ElementInclude import include
from django.urls import path


from . import views 

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("<int:id>", views.getid, name="getid"),
    path("create/", views.create, name="create"),
    path("list/", views.list, name="listview")
]
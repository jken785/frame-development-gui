from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    url(r'^$', views.main),
    url(r'^load/$', views.load),
    path('load/<int:id>/', views.loaded),
    path('run/<int:id>/', views.run),
    path('create/', views.create),
    path('createNew/', views.createNew),
    path('edit/<int:id>/', views.edit)
]

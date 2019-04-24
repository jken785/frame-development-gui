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
    path('editModel/<int:id>/', views.editModel),
    path('editLoadcases/<int:id>/', views.editLoadcases),
    path('save/<int:id>/', views.save),
    path('saveLoadcase/<int:id>/', views.saveLoadcase),
    path('deleteLoadcase/<int:id>/<str:name>/', views.deleteLoadcase),
    path('addNode/<int:id>/', views.addNode),
    path('addTube/<int:id>/', views.addTube),
    path('deleteNode/<int:id>/<str:name>/', views.removeNode),
    path('deleteTube/<int:id>/<str:nodeFrom>/<str:nodeTo>/', views.removeTube),
    path('listResults/<int:id>/', views.listResults),
    path('view/<int:id>', views.viewResults),
    path('createModelFromSim/<int:id>/', views.createModelFromSim),
    path('createModelFromSimBackend/<int:id>', views.createModelFromSimBackend),
    path('showCreateFrame/<int:id>/', views.showCreateFrame)
]

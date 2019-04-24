from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    path('', include('accounts.urls')),
    url(r'^sim/', include('sim.urls')),
    url(r'^admin/', admin.site.urls),
]

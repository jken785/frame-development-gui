from django.urls import path
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^', include('userAuth.urls')),
    url(r'^sim/', include('sim.urls')),
    url(r'^admin/', admin.site.urls),
]

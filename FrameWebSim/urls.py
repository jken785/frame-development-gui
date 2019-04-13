
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', include('sim.urls')),
    url(r'^sim/', include('sim.urls')),

    url(r'^admin/', admin.site.urls),
]

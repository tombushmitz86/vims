from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import views
from users.urls import urlpatterns as users_urls
from geography.urls import urlpatterns as geo_urls
from recipients.urls import urlpatterns as recipient_urls
from adoptions.urls import urlpatterns as adoption_urls
from activities.urls import urlpatterns as activity_urls


admin.site.site_header = _('VCMIS Administration')
admin.site.site_title = _('VCMIS Administration')


# Server namespaces are:
#   /health
#   /menahel
#   /api
# All other paths belong to the app.
urlpatterns = [
    url(r'^health/$', views.health),

    url(r'^menahel/', admin.site.urls),

    url(r'^api/users/', include(users_urls)),

    url(r'^api/geo/', include(geo_urls)),

    url(r'^api/recipients/', include(recipient_urls)),

    url(r'^api/adoptions/', include(adoption_urls)),

    url(r'^api/activities/', include(activity_urls)),
]

# For development only -- in prod the web server does this.
if settings.DEBUG:
    from django.contrib.staticfiles.views import serve
    from django.http import Http404

    def serve_or_index(request, path, insecure=False, **kwargs):
        try:
            return serve(request, path, insecure, **kwargs)
        except Http404:
            return serve(request, 'index.html', insecure, **kwargs)

    urlpatterns += [
        url(r'^(?P<path>.*)$', serve_or_index),
    ]

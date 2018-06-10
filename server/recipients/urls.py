from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'recipient', views.RecipientResource, 'recipient')

urlpatterns = router.urls

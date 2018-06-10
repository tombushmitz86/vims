from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'settlement', views.SettlementResource, 'settlement')
router.register(r'street', views.StreetResource, 'street')

urlpatterns = router.urls

from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'adoption', views.AdoptionResource, 'adoption')
router.register(r'package', views.PackageResource, 'package')
router.register(r'delivery', views.DeliveryResource, 'delivery')

urlpatterns = router.urls

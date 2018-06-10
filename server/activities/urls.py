from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'activityday', views.ActivityDayResource, 'activityday')
router.register(r'activityday-volunteer', views.ActivityDayVolunteerResource, 'activityday-volunteer')
router.register(r'activityday-delivery', views.ActivityDayDeliveryResource, 'activityday-delivery')
router.register(r'activitytype', views.ActivityTypeResource, 'activitytype')

urlpatterns = router.urls

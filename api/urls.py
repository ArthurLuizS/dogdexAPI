from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'dogs', views.DogViewSet)
router.register(r'owners', views.OwnerViewSet)
router.register(r'healths', views.HealthViewSet)
router.register(r'service-types', views.ServiceTypeViewSet, basename='service-type')
router.register(r'stays', views.StayViewSet, basename='stay')
router.register(r'services', views.ServiceRecordViewSet, basename='service-record')
urlpatterns = [
    path("onboarding/", views.OwnerFullCreateView.as_view(), name="owner-onboarding"),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
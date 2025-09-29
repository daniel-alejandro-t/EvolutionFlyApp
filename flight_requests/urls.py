from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.FlightRequestViewSet, basename='flightrequest')

app_name = 'flight_requests'

urlpatterns = [
    path('', include(router.urls)),
]
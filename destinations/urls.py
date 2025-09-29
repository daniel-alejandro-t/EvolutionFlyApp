from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'destinations', views.DestinationViewSet)

app_name = 'destinations'

urlpatterns = [
    path('', include(router.urls)),
]
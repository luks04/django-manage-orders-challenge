from django.urls import include, path
from rest_framework import routers
from .views import *


api_router = routers.DefaultRouter()
api_router.register('drivers', DriversViewSet)
api_router.register('orders', OrdersViewSet)

urlpatterns = [
    path('', include(api_router.urls)),
    path('schedule_order/', schedule_order),
    path('filter_orders/', filter_orders),
    path('filter_orders/<str:date>/', filter_orders),
    path('filter_orders/<str:date>/<int:driver_id>/', filter_orders),
    path('get_closest_driver/', get_closest_driver)
]
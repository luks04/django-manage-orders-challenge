from rest_framework import serializers
from core.models import Driver, Order

class DriverSerializer(serializers.ModelSerializer):
    # Datetime field format defined on main settings.
    class Meta:
        model = Driver
        fields = [
            "id", 
            "lat", 
            "lng", 
            "last_update"
        ]

class OrderSerializer(serializers.ModelSerializer):
    # Datetime field format defined on main settings.
    class Meta:
        model = Order
        fields = [
            "driver", 
            "pickup_datetime", 
            "pickup_lat", 
            "pickup_lng", 
            "delivery_lat", 
            "delivery_lng"
        ]

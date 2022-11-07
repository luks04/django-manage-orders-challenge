from django.db import models

class Driver(models.Model):
    id = models.AutoField(primary_key = True)
    lat = models.IntegerField()
    lng = models.IntegerField()
    last_update = models.DateTimeField()

    def __str__(self):
        return f"Driver ID: {self.id}"

class Order(models.Model):
    id = models.AutoField(primary_key = True)
    driver = models.ForeignKey(Driver, on_delete = models.PROTECT, related_name = 'assigned_driver')
    pickup_datetime = models.DateTimeField()
    pickup_lat = models.IntegerField()
    pickup_lng = models.IntegerField()
    delivery_lat = models.IntegerField()
    delivery_lng = models.IntegerField()

    def __str__(self):
        return f"Order: {self.id} - {self.pickup_datetime}"

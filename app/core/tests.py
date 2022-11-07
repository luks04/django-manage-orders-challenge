import json
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Driver
from core.models import Order
import datetime

class DriverTestCase(TestCase):
    def setUp(self):
        Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 15, lng = 25)
        Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 5, lng = 63)

    def test_drivers_exists(self):
        """Test drivers were created successfully"""
        qs_drivers = Driver.objects.all()
        self.assertEqual(len(qs_drivers), 2)
    
    def test_driver_fields(self):
        """Test tha Drivers object has lat, lng and last_update fields"""
        # Driver with ID = 1
        driver_1 = Driver.objects.get(id = 1)
        self.assertEqual(driver_1.lat, 15)
        self.assertEqual(driver_1.lng, 25)
        self.assertIsNotNone(driver_1.last_update)
        # Driver with ID = 2
        driver_2 = Driver.objects.get(id = 2)
        self.assertEqual(driver_2.lat, 5)
        self.assertEqual(driver_2.lng, 63)
        self.assertIsNotNone(driver_2.last_update)

class OrderTestCase(TestCase):
    def setUp(self):
        driver_1 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 15, lng = 25)
        driver_2 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 5, lng = 63)
        Order.objects.create(driver = driver_1, pickup_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), 
                             pickup_lat = 15, pickup_lng = 25, delivery_lat = 5, delivery_lng = 63)
        Order.objects.create(driver = driver_2, pickup_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), 
                             pickup_lat = 33, pickup_lng = 12, delivery_lat = 44, delivery_lng = 45)
        
    def test_orders_exists(self):
        """Test orders were created successfully"""
        qs_orders = Order.objects.all()
        self.assertEqual(len(qs_orders), 2)
    
    def test_orders_fields(self):
        """Test tha Order object has driver, pickup_datetime, pickup_lat, pickup_lng, delivery_lat and delivery_lng fields"""
        # Order with ID = 1
        order_1 = Order.objects.get(id = 1)
        self.assertEqual(order_1.driver.id, 1)
        self.assertIsNotNone(order_1.pickup_datetime)
        self.assertEqual(order_1.pickup_lat, 15)
        self.assertEqual(order_1.pickup_lng, 25)
        self.assertEqual(order_1.delivery_lat, 5)
        self.assertEqual(order_1.delivery_lng, 63)
        
        # Order with ID = 2
        order_2 = Order.objects.get(id = 2)
        self.assertEqual(order_2.driver.id, 2)
        self.assertIsNotNone(order_2.pickup_datetime)
        self.assertEqual(order_2.pickup_lat, 33)
        self.assertEqual(order_2.pickup_lng, 12)
        self.assertEqual(order_2.delivery_lat, 44)
        self.assertEqual(order_2.delivery_lng, 45)

class ScheduleOrderTestCaseRestframework(TestCase):
    def setUp(self):
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 2)
        driver_1 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 15, lng = 25)
        driver_2 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 5, lng = 63)
        Order.objects.create(driver = driver_1, pickup_datetime = test_datetime, 
                             pickup_lat = 15, pickup_lng = 25, delivery_lat = 5, delivery_lng = 63)
        Order.objects.create(driver = driver_2, pickup_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), 
                             pickup_lat = 33, pickup_lng = 12, delivery_lat = 44, delivery_lng = 45)
    
    def test_schedule_order_endpoint(self):
        """Test successfully order creation"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 3, minutes = 30)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": test_datetime_str,
            "pickup_lat": 33,
            "pickup_lng": 1,
            "delivery_lat": 98,
            "delivery_lng": 98
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_schedule_order_endpoint_bad_request_date_format(self):
        """Test that the order can not be scheduled because exception must be raised because of invalid date format."""
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": "wrong_date_format",
            "pickup_lat": 33,
            "pickup_lng": 1,
            "delivery_lat": 98,
            "delivery_lng": 98
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Datetime has wrong format", json.loads(response.content)["pickup_datetime"][0])
    
    def test_schedule_order_endpoint_bad_request_past_time(self):
        """Test that the order can not be scheduled because it is not possible to schedule an order for a past time."""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) - datetime.timedelta(hours = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": test_datetime_str,
            "pickup_lat": 33,
            "pickup_lng": 1,
            "delivery_lat": 98,
            "delivery_lng": 98
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("It is not possible to schedule an order for a past time", json.loads(response.content)["error"])
    
    def test_schedule_order_endpoint_invalid_model_structure(self):
        """Test that the order can not be scheduled because the model strucrure is invalid."""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": test_datetime_str,
            "pickup_lat": 33,
            "delivery_lng": 98
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required", json.loads(response.content)["pickup_lng"][0])
    
    def test_schedule_order_endpoint_wrong_data_type(self):
        """Test that the order can not be scheduled because the model strucrure has a wrong data type."""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": test_datetime_str,
            "pickup_lat": 33,
            "pickup_lng": 1,
            "delivery_lat": 98,
            "delivery_lng": "wrong_data_type"
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A valid integer is required", json.loads(response.content)["delivery_lng"][0])
    
    def test_schedule_order_endpoint_internal_error_busy_driver(self):
        """Test that if the requested driver is bussy at the requested date and time, raise an exception."""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 2, minutes = 30)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "driver": 1,
            "pickup_datetime": test_datetime_str,
            "pickup_lat": 33,
            "pickup_lng": 1,
            "delivery_lat": 98,
            "delivery_lng": 98
        }
        response = client.post('/api/schedule_order/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("The driver is busy", json.loads(response.content)["error"])

class FilterOrderTestCaseRestframework(TestCase):
    def setUp(self):
        driver_1 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 15, lng = 25)
        driver_2 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 5, lng = 63)
        Order.objects.create(driver = driver_1, pickup_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), 
                             pickup_lat = 15, pickup_lng = 25, delivery_lat = 5, delivery_lng = 63)
        Order.objects.create(driver = driver_2, pickup_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), 
                             pickup_lat = 33, pickup_lng = 12, delivery_lat = 44, delivery_lng = 45)
    
    def test_filter_order_endpoint_by_date(self):
        """Test successfully filter order by date"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ)
        test_date_str = test_datetime.strftime(settings.DEFAULT_DATE_FORMAT)
        client = APIClient()
        response = client.get(f'/api/filter_orders/{test_date_str}', {}, True, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The total orders of the requested date
        self.assertEqual(len(json.loads(response.content)), 2)
    
    def test_filter_order_endpoint_by_date_and_by_driver(self):
        """Test successfully filter order bydate and by driver"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ)
        test_date_str = test_datetime.strftime(settings.DEFAULT_DATE_FORMAT)
        driver_id = "2"
        client = APIClient()
        response = client.get(f'/api/filter_orders/{test_date_str}/{driver_id}', {}, True, format = 'json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The total orders of driver with ID = 2 for the requested date
        self.assertEqual(len(json.loads(response.content)), 1)
    
    def test_filter_order_endpoint_bad_request_date_format(self):
        """Test filter order raise an exception when the received date format is not valid."""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ)
        test_date_str = test_datetime.strftime('%d-%m-%Y')
        driver_id = "2"
        client = APIClient()
        response = client.get(f'/api/filter_orders/{test_date_str}/{driver_id}', {}, True, format = 'json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_order_endpoint_bad_request_missing_filter_fields(self):
        """Test filter order raise an exception when the received date format is not valid."""
        client = APIClient()
        response = client.get(f'/api/filter_orders/', {}, True, format = 'json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Missing parameters. Fields", json.loads(response.content)["error"])
        
class SearchClosestDriverTestCaseRestframework(TestCase):
    def setUp(self):
        test_datetime_3h = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 3)
        test_datetime_2d = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(days = 2)
        test_datetime_12h = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 12)
        test_datetime_30m = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(minutes = 30)
        driver_1 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 15, lng = 25)
        driver_2 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 5, lng = 63)
        driver_3 = Driver.objects.create(last_update = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ), lat = 98, lng = 98)
        Order.objects.create(driver = driver_1, pickup_datetime = test_datetime_3h, pickup_lat = 15, pickup_lng = 25, delivery_lat = 5, delivery_lng = 63)
        Order.objects.create(driver = driver_2, pickup_datetime = test_datetime_2d, pickup_lat = 33, pickup_lng = 12, delivery_lat = 44, delivery_lng = 45)
        Order.objects.create(driver = driver_2, pickup_datetime = test_datetime_12h, pickup_lat = 15, pickup_lng = 25, delivery_lat = 99, delivery_lng = 95)
        Order.objects.create(driver = driver_1, pickup_datetime = test_datetime_30m, pickup_lat = 33, pickup_lng = 12, delivery_lat = 1, delivery_lng = 5)
    
    def test_search_driver_endpoint_success(self):
        """Test successfully search and find a driver"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(days = 2, hours = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "target_datetime": test_datetime_str,
            "lat": 47,
            "lng": 47
        }
        response = client.post('/api/get_closest_driver/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)["id"], 2)
        
    def test_search_driver_endpoint_success_driver_start_zone(self):
        """Test successfully search and find a driver by start zone because the other near drivers are busy"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 12, minutes = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "target_datetime": test_datetime_str,
            "lat": 90,
            "lng": 93
        }
        response = client.post('/api/get_closest_driver/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)["id"], 3)
    
    def test_search_driver_endpoint_success_driver_start_zone_not_busy(self):
        """Test successfully search and find a not busy driver"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(hours = 13, minutes = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "target_datetime": test_datetime_str,
            "lat": 90,
            "lng": 93
        }
        response = client.post('/api/get_closest_driver/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)["id"], 2)

class SearchClosestDriverSpecialTestCaseRestframework(TestCase): 
    def test_search_driver_endpoint_no_active_drivers(self):
        """Test not active drivers found"""
        test_datetime = datetime.datetime.now().replace(tzinfo = settings.TIME_ZONE_PYTZ) + datetime.timedelta(days = 2, hours = 2)
        test_datetime_str = test_datetime.strftime(settings.DEFAULT_DATETIME_FORMAT)
        client = APIClient()
        data = {
            "target_datetime": test_datetime_str,
            "lat": 47,
            "lng": 47
        }
        response = client.post('/api/get_closest_driver/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Active drivers not found", json.loads(response.content)["error"])

from django.conf import settings
import requests
import datetime
from core.models import Driver


def fetch_drivers_location():
    """Fetch the Drivers data from external system. 
    Then save or update the Driver on Database.
    """
    response = requests.get(settings.DRIVERS_LOCATION_URL, verify = False)
    data = response.json()
    drivers_list: list = data['alfreds']
    print("Fetched at: ", datetime.datetime.now(), " - ", drivers_list)
    for driver in drivers_list:
        # Update or create the Driver object
        defaults = {
            "lat": driver['lat'], 
            "lng": driver['lng'], 
            "last_update": driver['lastUpdate']
        }
        driver, created = Driver.objects.update_or_create(id = driver['id'], defaults = defaults)

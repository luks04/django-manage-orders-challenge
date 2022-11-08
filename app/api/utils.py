import datetime
from typing import Union
from core.models import Driver, Order
from django.conf import settings


def get_error_dict(error_msg: Union[Exception, str]) -> dict[str, str]:
    """Returns a default error dict for a given error message or exception."""
    return {'error': str(error_msg)}

def get_closest_driver_by_orders_and_coordinates(target_datetime: datetime.datetime, 
                                                 lat: int, lng: int) -> Union[int, None]:
    """Search nearby drivers by orders coordinates and datetime.

    Args:
    -----
        target_datetime (datetime.datetime): The requested Order target datetime.
        lat (int): Latitude coordinates.
        lng (int): Longitude coordinates.

    Returns:
    --------
        Union[int, None]: The id of the found closest driver. None if no close driver is found.
    """
    # Get the nearest (in time) completed orders up to the requested time and order by pickup_datetime (asc)
    # This way the most recent order will be checked last.
    last_selectable_order_start_datetime = target_datetime - settings.DEFAULT_ORDER_DURATION
    qs_orders_completed_to_date = Order.objects.filter(
        pickup_datetime__lte = last_selectable_order_start_datetime,
        pickup_datetime__gte = datetime.datetime.now()
    ).order_by('pickup_datetime')
    # Define a positive infinity value to the shortest distance and initialize the selected_driver_id.
    closest_distance = float('inf')
    closest_timedelta = settings.MAX_TIMEDELTA_TO_SEARCH_CLOSEST_ORDER
    selected_driver_id = None
    # Iterate over the orders that n=must be completed to date and find the nearest (in distance) driver.
    for order in qs_orders_completed_to_date:
        driver_distance = abs(order.delivery_lat - lat) + abs(order.delivery_lng - lng)
        datetime_diff = target_datetime.replace(tzinfo = settings.TIME_ZONE_PYTZ) - order.pickup_datetime
        if driver_distance < closest_distance and datetime_diff < closest_timedelta:
            closest_distance = driver_distance
            closest_timedelta = datetime_diff
            selected_driver_id = order.driver.id
    return selected_driver_id

def get_closest_driver_by_driver_starting_zone(lat: int, lng: int, target_datetime: datetime.datetime) -> Union[int, None]:
    """Search for a driver by initial zone coordinates using target_datetime to exclude busy drivers.

    Args:
    -----
        lat (int): Latitude coordinates.
        lng (int): Longitude coordinates.
        target_datetime (datetime.datetime): The requested Order target datetime.

    Returns:
    --------
        Union[int, None]: The id of the found closest driver. None if no close driver is found.
    """
    # Gets the active orders at requested datetime.
    last_active_order_start_datetime = target_datetime - settings.DEFAULT_ORDER_DURATION
    last_active_order_end_datetime = target_datetime - datetime.timedelta(minutes = 1)
    qs_active_orders_to_date = Order.objects.filter(
        pickup_datetime__gte = last_active_order_start_datetime,
        pickup_datetime__lte = last_active_order_end_datetime
    )
    # Gets the busy drivers at requested datetime.
    busy_drivers = [order.driver.id for order in qs_active_orders_to_date]
    all_drivers = Driver.objects.all()
    # Define a positive infinity value to the shortest distance and initialize the selected_driver_id.
    closest_distance = float('inf')
    selected_driver_id = None
    # Iterate over the drivers and find the nearest (in distance).
    for driver in all_drivers:
        if driver.id not in busy_drivers:
            driver_distance = abs(driver.lat - lat) + abs(driver.lng - lng)
            if driver_distance < closest_distance:
                closest_distance = driver_distance
                selected_driver_id = driver.id
    return selected_driver_id

import datetime
from django.conf import settings
from urllib.request import Request
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.models import Driver, Order
from .serializers import DriverSerializer, OrderSerializer
from .utils import get_error_dict
from .utils import get_closest_driver_by_orders_and_coordinates
from .utils import get_closest_driver_by_driver_starting_zone


########## MODEL VIEW SETS ##########

class DriversViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = DriverSerializer

class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderSerializer

########## API VIEWS ##########

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def schedule_order(request: Request) -> Response:
    """Schedule an order to a driver on a date and time, and specify his place of 
    pickup (latitude and longitude) and destination.

    Args:
    -----
        request (Request): The API request object.

    Returns:
    --------
        Response: The created Order object.
    """
    order_serializer = OrderSerializer(data = request.data)
    if order_serializer.is_valid(raise_exception = True):
        try:
            # Once the request data has been validated, gets the 'pickup_datetime' Order attribute.
            new_order_pickup_datetime = datetime.datetime.strptime(request.data["pickup_datetime"], 
                                                                   settings.DEFAULT_DATETIME_FORMAT)
            # If the order's pickup_datetime is lower than current datetime, raise an exception. 
            if new_order_pickup_datetime < datetime.datetime.now():
                raise Exception("It is not possible to schedule an order for a past time.")
        except Exception as error:
            error_dict = get_error_dict(str(error))
            return Response(error_dict, status = status.HTTP_400_BAD_REQUEST)
        # Obtains the orders of the driver that, for the requested moment, intersect with other orders.
        lower_datetime_limit = new_order_pickup_datetime - settings.DEFAULT_ORDER_DURATION
        upper_datetime_limit = new_order_pickup_datetime + settings.DEFAULT_ORDER_DURATION
        qs_cross_orders = Order.objects.filter(
            driver_id = request.data["driver"],
            pickup_datetime__lte = upper_datetime_limit,
            pickup_datetime__gte = lower_datetime_limit
        )
        # If it finds that there are more orders that intersect with the orders previously 
        # scheduled for the requested driver, it raise an error.
        if len(qs_cross_orders) > 0:
            error_dict = get_error_dict("The driver is busy at the requested time. Please try another time.")
            return Response(error_dict, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Otherwise save it.
        order_serializer.save()
        return Response(order_serializer.data, status = status.HTTP_201_CREATED)
    return Response(order_serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def filter_orders(request: Request, *args, **kwargs) -> Response:
    """Consult all the orders assigned on a specific day ordered by time.
    Consult all the orders of a driver on a specific day ordered by time.

    Args:
    -----
        request (Request): The API request object.
    
    Raises:
    -------
        Exception: When the date filter is missing
            or when the received date does not match with a valid format.

    Returns:
    --------
        Response: The filtered orders.
    """
    date_str = kwargs.get("date")
    driver_id_int = kwargs.get("driver_id")
    try:
        if date_str is None:
            needed_fields = ['date']
            raise  Exception(f"Missing parameters. Fields {needed_fields} needed.")
        filter_date = datetime.datetime.strptime(date_str, settings.DEFAULT_DATE_FORMAT).date()
    except Exception as error:
        error_dict = get_error_dict(str(error))
        return Response(error_dict, status = status.HTTP_400_BAD_REQUEST)
    else:
        if driver_id_int is not None:
            # Filter by pickup_datetime and driver id.
            # Order By: Most recent first (desc).
            queryset = Order.objects.filter(pickup_datetime__date = filter_date, 
                                        driver_id = driver_id_int
                                        ).order_by('-pickup_datetime')
        else:
            # Filter by pickup_datetime.
            # Order By: Most recent first (desc).
            queryset = Order.objects.filter(pickup_datetime__date = filter_date).order_by('-pickup_datetime')
        serlalized_obj = OrderSerializer(queryset, many = True).data
    return Response(serlalized_obj, status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_closest_driver(request: Request) -> Response:
    """Search for the driver that is closest to a geographical point on a date and time. 
    Considering the orders already assigned to the driver

    Args:
    -----
        request (Request): The API request object.

    Returns:
    -------
        Response: The nearest (about distance and time) found driver.
    """
    target_datetime_str = request.data.get('target_datetime')
    lat_str = request.data.get('lat')
    lng_str = request.data.get('lng')
    try:
        if target_datetime_str is None or lat_str is None or lng_str is None:
            needed_fields = ['target_datetime', 'lat', 'lng']
            raise  Exception(f"Missing parameters. Fields {needed_fields} needed.")
        # Every exception parsing the target_datetime or the lat and lng will be catched. 
        target_datetime = datetime.datetime.strptime(target_datetime_str, settings.DEFAULT_DATETIME_FORMAT)
        lat = int(lat_str)
        lng = int(lng_str)
        # If the order's pickup_datetime is lower than current datetime, raise an exception. 
        if target_datetime < datetime.datetime.now():
            raise Exception("It is not possible to search a closest driver an order for a past time.")
    except Exception as error:
        error_dict = get_error_dict(str(error))
        return Response(error_dict, status = status.HTTP_400_BAD_REQUEST)
    else:
        # Search nearby drivers by orders coordinates and datetime.
        selected_driver_id = get_closest_driver_by_orders_and_coordinates(target_datetime, lat, lng)
        # If no nearby drivers are found by orders, search for a driver by initial zone coordinates.
        if selected_driver_id is None:
            selected_driver_id = get_closest_driver_by_driver_starting_zone(lat, lng)
            if selected_driver_id is None:
                error_dict = get_error_dict("Active drivers not found.")
                return Response(error_dict, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    selected_driver = Driver.objects.get(pk = selected_driver_id)
    response = DriverSerializer(selected_driver).data
    return Response(response, status = status.HTTP_200_OK)

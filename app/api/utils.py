import datetime
from typing import Union
from core.models import Driver, Order
from django.conf import settings


def get_error_dict(error_msg: Union[Exception, str]) -> dict[str, str]:
    """Returns a default error dict for a given error message or exception."""
    return {'error': str(error_msg)}

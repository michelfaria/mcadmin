# mcadmin/decorators.py
from functools import wraps

from flask import request, Response, abort


def json_route(f, method=None):
    """
    This will return a 400 HTTP/Bad Request if the request does not have JSON content.

    :param method: Optionally a list of the HTTP Methods that will require JSON. ['POST'] by default.
    """
    if method is None:
        method = ['POST']

    @wraps
    def wrapper(*args, **kwargs):
        if request.method in method:
            if not request.is_json:
                abort(400, 'Expected JSON')
            return f(args, kwargs)

    return wrapper

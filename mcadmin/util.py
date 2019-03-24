# mcadmin/util.py

from flask import request, abort


def require_json():
    """
    This will raise a 400 HTTP/Bad Request error if the request does not have JSON content.
    """
    if not request.is_json:
        abort(400, 'Expected JSON')

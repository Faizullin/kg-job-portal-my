from typing import List

from rest_framework import status


class BaseActionException(Exception):
    status = status.HTTP_400_BAD_REQUEST

    def __init__(self, *args):
        super().__init__(*args)


class ActionRequestException(BaseActionException):
    errors: List[dict]

    def __init__(self, message: dict | str, status_code=400, errors=None):
        super().__init__(message, status_code)
        if errors is None:
            errors = []
        self.status_code = status_code
        self.errors = errors


class BaseAction:
    name: str

    def apply(self, request):
        raise BaseActionException("Incorrect action")

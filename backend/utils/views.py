from typing import List

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


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


class BaseActionAPIView(APIView):
    available_actions: List[BaseAction] = []

    def post(self, request):
        """Perform action based on 'action' parameter in request data."""

        action_name = request.GET.get("action", None)
        action_index = -1
        for i, action in enumerate(self.available_actions):
            if action.name == action_name:
                action_index = i
                break
        if action_index == -1:
            return Response(
                {"success": 0, "message": f"action={action_name} is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            use_action = self.available_actions[action_index]
            response = use_action.apply(request)
            return Response(response, status=status.HTTP_200_OK)
        except ActionRequestException as err:
            return Response(
                {
                    "success": 0,
                    "errors": {
                        "message": str(err),
                        "errors": err.errors,
                    },
                }
            )
        except BaseActionException as err:
            return Response({"success": 0, "message": str(err)}, status=err.status)

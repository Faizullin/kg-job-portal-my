from django.contrib.auth import get_user_model
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_users.models import UserTypes
from lms.apps.core.utils.crud_base.views import BaseApiViewSet
from .serializers import (
    UserSerializer,
)

User = get_user_model()


class UserViewSet(BaseApiViewSet):
    search_fields = ["username", "email"]
    ordering_fields = [
        "id",
    ]

    class UserFilter(FilterSet):
        username = CharFilter(lookup_expr="icontains")
        email = CharFilter(lookup_expr="icontains")

        class Meta:
            model = User
            fields = ["id", "username", "email", "user_type"]

    filterset_class = UserFilter

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def get_serializer_class(self):
        return UserSerializer

    # action for ahcnge bulk user type
    @action(detail=False, methods=["post"], url_path="toggle-user-type")
    def toggle_user_type(self, request):
        user_ids = request.data.get("user_ids", [])
        user_type = request.data.get("user_type", None)
        types_list = [i[0] for i in UserTypes.choices()]
        if not user_ids or not user_type:
            return Response(
                {"error": "user_ids and user_type are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_type not in types_list:
            return Response(
                {"error": "user_type must be one of the following: " + str(types_list)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(user_ids, list):
            return Response(
                {"error": "user_ids must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not all(isinstance(user_id, int) for user_id in user_ids):
            return Response(
                {"error": "user_ids must be a list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # add logic to ehck all exitnace of user ids
        # and if user is not blocked
        try:
            not_existant_user_ids = []
            for id in user_ids:
                if not User.objects.filter(id=id).exists():
                    not_existant_user_ids.append(id)
            if not_existant_user_ids:
                return Response(
                    {
                        "error": "user_ids not exist",
                        "not_existant_user_ids": not_existant_user_ids,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            User.objects.filter(id__in=user_ids).update(user_type=user_type)
        except Exception as e:
            return Response(
                {"error": "Error while updating user_type", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "success"})

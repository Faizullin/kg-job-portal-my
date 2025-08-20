from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.request import Request

from api_users.cloud_messaging import send_friend_request_notification
from api_users.serializers import *
from api_users.models import *
from api_users.serializers.model_serializers import UserModelSerializer
from backend.global_function import success_with_text, error_with_text


class PaginationClass(PageNumberPagination):
    page_size = 40


class GetFriendsView(APIView):
    def get(self, request: Request):
        a = UserModelAsFriendSerializer(request.user.friends.all(), many=True, user=request.user).data
        b = UserModelAsFriendSerializer(request.user.friendship_requests.all(), many=True, user=request.user).data
        return success_with_text(
            {'friends': a, 'pending_requests': b}
        )


class SearchFriendsView(APIView):
    def post(self, request: Request):
        serializer = SearchUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        search = serializer.validated_data['search']
        users = UserModel.objects.filter(name__icontains=search).exclude(id=request.user.id).all()
        page = PaginationClass().paginate_queryset(users, request)
        return success_with_text(UserModelAsFriendSerializer(page, many=True, user=request.user).data)


class AddFriendView(APIView):
    def post(self, request: Request):
        serializer = GetUserByIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        this_user: UserModel = request.user
        other_user: UserModel = serializer.validated_data['user_id']
        this_user.send_friend_request(other_user)
        send_friend_request_notification(user=other_user, request_sender=this_user)
        return success_with_text('Friend request sent')


class AcceptFriendRequestView(APIView):
    def post(self, request: Request):
        serializer = GetUserByIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        this_user: UserModel = request.user
        other_user: UserModel = serializer.validated_data['user_id']
        this_user.accept_friend_request(other_user)
        return success_with_text('Friend request accepted')


class DeclineFriendRequestView(APIView):
    def post(self, request: Request):
        serializer = GetUserByIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        this_user: UserModel = request.user
        other_user: UserModel = serializer.validated_data['user_id']
        this_user.decline_friend_request(other_user)
        return success_with_text('Friend request declined')


class DeleteFromFriendsView(APIView):
    def post(self, request: Request):
        serializer = GetUserByIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        this_user: UserModel = request.user
        other_user: UserModel = serializer.validated_data['user_id']
        this_user.friends.remove(other_user)
        return success_with_text('Friend deleted')

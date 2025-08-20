from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import views as api_views

router = DefaultRouter()
router.register(r'api/v1/lms/resources/component/text-pro', api_views.ResourcesTextComponentViewSet,
                basename='text-pro-component')
router.register(r'api/v1/lms/resources/component/question',
                api_views.ResourcesQuestionComponentViewSet,
                basename='question-component')
router.register(r'api/v1/lms/resources/component/bluecard',
                api_views.ResourcesBlueCardComponentViewSet,
                basename='bluecard-component')
router.register(r'api/v1/lms/resources/component/audio', api_views.ResourcesAudioComponentViewSet,
                basename='audio-component')
router.register(r'api/v1/lms/resources/component/fill-text',
                api_views.ResourceFillTextComponentViewSet,
                basename='fill-text-component')
router.register(r'api/v1/lms/resources/component/video', api_views.ResourcesVideoComponentViewSet,
                basename='video-component')
router.register(r'api/v1/lms/resources/component/record-audio',
                api_views.ResourcesRecordAudioComponentViewSet, basename='record-audio-component')
router.register(r'api/v1/lms/resources/component/order', api_views.ResourcesOrderComponentViewSet,
                basename='order-component')
router.register(r'api/v1/lms/resources/component/image', api_views.ResourcesImageComponentViewSet,
                basename="image-component")
router.register(r'api/v1/lms/resources/component/matching', api_views.MatchingComponentViewSet,
                basename="matching-component")

urlpatterns = [
    path("", include(router.urls)),
]

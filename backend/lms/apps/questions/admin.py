from django.contrib import admin

from .models import (
    Question,
    MultipleChoiceOption,
    OrderingItem,
    FillGapBlank,
    MatchingElement,
    MatchingPair,
    RecordAudioSettings,
    UserAnswer,
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "created_at")
    search_fields = ("text",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(MultipleChoiceOption)
class MultipleChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "text", "is_correct", "created_at")
    search_fields = ("text",)
    list_filter = ("is_correct", "created_at")
    ordering = ("-created_at",)


@admin.register(OrderingItem)
class OrderingItemAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "text", "correct_order", "created_at")
    search_fields = ("text",)
    list_filter = ("correct_order", "created_at")
    ordering = ("-created_at",)


@admin.register(FillGapBlank)
class FillGapBlankAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "index", "created_at")
    search_fields = ("index",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(MatchingElement)
class MatchingElementAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "created_at")
    search_fields = ("text",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(MatchingPair)
class MatchingPairAdmin(admin.ModelAdmin):
    list_display = ("id", "left_element", "right_element", "created_at")
    search_fields = ("left_element__text", "right_element__text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(RecordAudioSettings)
class RecordAudioQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    search_fields = ("user__username", "question__text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    raw_id_fields = ("user", "question")
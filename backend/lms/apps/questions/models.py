from lms.apps.core.utils.abstract_models import (
    AbstractTimestampedModel,
    get_truncated_name,
)
from django.db import models
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class QuestionTypes(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", "Множественный выбор"
    ORDERING = "ordering", "Упорядочивание"
    FILL_IN_THE_BLANKS = "fill_in_the_blanks", "Заполните пропуски"
    MATCHING = "matching", "Сопоставление"
    RECORD_AUDIO = "record_audio", "Запись аудио"


class Question(AbstractTimestampedModel):
    text = models.CharField(max_length=2000, verbose_name="Текст вопроса")
    question_type = models.CharField(
        max_length=50,
        choices=QuestionTypes.choices,
        verbose_name="Тип вопроса",
        help_text="Тип вопроса, например, множественный выбор, заполнение пропусков и т.д.",
    )

    class Meta:
        verbose_name = "Вопрос компонент"
        verbose_name_plural = "Вопросы компоненты"
        ordering = ["id"]

    def __str__(self):
        return f'Question: "{get_truncated_name(self.text)}" [#{self.pk}]'


class MultipleChoiceOption(AbstractTimestampedModel):
    """Options for multiple choice"""

    question = models.ForeignKey(
        Question, related_name="mc_options", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=500, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Порядок ответа в вопросе. Меньшие числа идут первыми.",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{get_truncated_name(self.text)} ({'✓' if self.is_correct else '✗'}) [#{self.pk}]"


class OrderingItem(AbstractTimestampedModel):
    """Items to be ordered"""

    question = models.ForeignKey(
        Question, related_name="ordering_items", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=500, verbose_name="Текст элемента")
    correct_order = models.PositiveIntegerField(verbose_name="Правильный порядок")

    class Meta:
        ordering = ["correct_order"]

    def __str__(self):
        return f"{get_truncated_name(self.text)} (#{self.correct_order}) [#{self.pk}])"


class FillGapBlank(AbstractTimestampedModel):
    question = models.ForeignKey(
        Question,
        related_name="fill_gap_blanks",
        on_delete=models.CASCADE,
    )
    index = models.PositiveIntegerField(
        help_text="Index in the format {{index}} in the question text"
    )
    correct_answers = models.JSONField(
        default=list,
        help_text="Accepted answers for this gap (can include multiple variants)",
    )

    def __str__(self):
        return "Blank {{{}}} for question: {}".format(
            self.index, get_truncated_name(self.question.text)
        )


class MatchingElement(AbstractTimestampedModel):
    text = models.CharField(max_length=500, verbose_name="Текст элемента")
    image = models.ForeignKey(
        "attachments.Attachment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="matching_elements",
    )
    question = models.ForeignKey(
        Question, related_name="matching_elements", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{get_truncated_name(self.text)} [#{self.pk}]"


class MatchingPair(AbstractTimestampedModel):
    """Pairs of matching elements"""

    question = models.ForeignKey(
        Question, related_name="matching_pairs", on_delete=models.CASCADE
    )
    left_element = models.ForeignKey(
        MatchingElement,
        related_name="left_pairs",
        on_delete=models.CASCADE,
    )
    right_element = models.ForeignKey(
        MatchingElement,
        related_name="right_pairs",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("question", "left_element", "right_element")

    def __str__(self):
        return f"{self.left_element} ↔ {self.right_element} [#{self.pk}]"


class RecordAudioSettings(AbstractTimestampedModel):
    title = models.CharField(max_length=200, verbose_name="Название вопроса")
    question = models.OneToOneField(
        Question,
        related_name="record_audio_settings",
        on_delete=models.CASCADE,
    )
    instructions = models.TextField(
        verbose_name="Инструкции",
        help_text="Инструкции для пользователя по записи аудио",
    )


class UserAnswer(AbstractTimestampedModel):
    """Base model for user answers to questions"""

    user = models.ForeignKey(
        UserModel,
        related_name="user_answers",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        Question,
        related_name="user_answers",
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
    )
    is_correct = models.BooleanField(
        default=False, verbose_name="Правильный ответ", help_text="Является ли ответ правильным"
    )
    score = models.FloatField(
        default=0.0,
        verbose_name="Баллы",
        help_text="Количество баллов, полученных за этот ответ",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Комментарий к ответу, например, объяснение ошибки",
    )
    is_graded = models.BooleanField(
        default=False,
        verbose_name="Оценен",
        help_text="Был ли ответ оценен преподавателем или автоматически",
    )
    is_submitted = models.BooleanField(
        default=False,
        verbose_name="Отправлен",
        help_text="Был ли ответ отправлен на проверку",
    )
    data = models.CharField(
        max_length=2000,
        blank=True,
        null=True,
        verbose_name="Данные ответа",
        help_text="Дополнительные данные ответа, например, JSON с ответами на вопросы",
    )
    
    def __str__(self):
        return f"Answer by {self.user} to {self.question} [#{self.pk}]"
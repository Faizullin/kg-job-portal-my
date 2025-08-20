from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from lms.apps.questions.models import Question, QuestionTypes, MultipleChoiceOption
from django.contrib.auth import get_user_model

UserModel = get_user_model()

def user_submit(client, payload):
    """
    Helper function to submit a question answer as a user.
    """
    url = reverse("lms:question-public-user-submit-api")
    print("Payload being sent:", payload)
    response = client.post(url, payload, format="json")
    return response

class QuestionSubmissionApiTest(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Create a sample multiple choice question
        self.question = Question.objects.create(
            text="What is 2 + 2?",
            question_type=QuestionTypes.MULTIPLE_CHOICE,
        )
        self.option1 = MultipleChoiceOption.objects.create(
            question=self.question, text="3", is_correct=False, order=1
        )
        self.option2 = MultipleChoiceOption.objects.create(
            question=self.question, text="4", is_correct=True, order=2
        )
        self.url = reverse("lms:question-public-user-submit-api")

    def test_submit_multiple_choice_answer(self):
        payload = {
            "question_id": self.question.id,
            "answer_data": {
                "answers": [self.option2.id]  # Submitting the correct answer
                },  # Submitting the correct answer
            "form_data_type": "json",
        }
        response = user_submit(self.client, payload)
        print("Response status:", response.status_code)
        print("Response data:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Question submitted successfully.")

    def test_submit_invalid_question(self):
        payload = {
            "question_id": 9999,  # Non-existent question
            "answer_data": {
                "answers": [self.option2.id]  # Submitting the correct answer
            },
            "form_data_type": "json",
        }
        response = user_submit(self.client, payload)
        print("Response status:", response.status_code)
        print("Response data:", response.data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
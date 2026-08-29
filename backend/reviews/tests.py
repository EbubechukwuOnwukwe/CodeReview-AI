from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Review


class ReviewAPITestCase(APITestCase):

    def test_create_review(self):
        url = reverse("review-list")

        data = {
            "code": "print('Hello World')",
            "requirements": "Print a greeting to the user.",
            "language": "Python",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Review.objects.count(),
            1,
        )

        review = Review.objects.first()

        self.assertEqual(
            review.language,
            "Python",
        )

        self.assertEqual(
            review.status,
            Review.Status.PENDING,
        )


    def test_get_reviews(self):
        Review.objects.create(
            code="print('Hello')",
            requirements="Print a greeting.",
            language="Python",
        )

        url = reverse("review-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )
import io

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Song, Genre
from profiles.models import Profile
from profiles.tokens import VerifyToken, CustomRefreshToken

TEST_USERNAME = "test_username"
TEST_EMAIL = "test_email@mail.ru"
TEST_PASSWORD = "test_password_69"


class SongsListCreateTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD,
            is_artist=True
        )
        self.genre = Genre.objects.create(
            genre="test_genre"
        )
        self.song = Song.objects.create(
            title="test_song",
            audio="test_uri",
            cover="test_uri",
            genre=self.genre,
            artist=self.profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_songs_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "test_song")

    def test_songs_list_bad_page(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-list-create"), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_songs_list_unauthorized(self):
        response = self.client.get(reverse("songs-list-create"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_song(self):
        data = {
            "title": "new_test_song",
            "audio": io.BytesIO(b"some bytes"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

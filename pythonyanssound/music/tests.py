from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Song, Genre
from profiles.models import Profile
from profiles.tokens import CustomRefreshToken

TEST_USERNAME = "test_username"
TEST_EMAIL = "test_email@mail.ru"
TEST_PASSWORD = "test_password_69"


class SongsListCreateTestCase(APITestCase):

    def setUp(self) -> None:
        self.artist = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD,
            is_artist=True
        )
        self.profile = Profile.objects.create_user(
            "profile_test_mail@mail.ru",
            "profile_test_username",
            "profile_test_password"
        )
        self.genre = Genre.objects.create(
            genre="test_genre"
        )
        self.song = Song.objects.create(
            title="test_song",
            audio="test_uri",
            cover="test_uri",
            genre=self.genre,
            artist=self.artist
        )
        self.artist_refresh_token = CustomRefreshToken.for_user(self.artist)
        self.profile_refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_songs_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.get(reverse("songs-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "test_song")

    def test_songs_list_bad_page(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.get(reverse("songs-list-create"), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_songs_list_unauthorized(self):
        response = self.client.get(reverse("songs-list-create"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_song(self):
        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "new_test_song")

    def test_create_song_wrong_file_extension(self):
        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.wav", b"test_bytes", content_type="audio/wav"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_song_wrong_cover_extension(self):
        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3"),
            "cover": SimpleUploadedFile("cover.mp3", b"cover_bytes", content_type="audio/mp3"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_song_by_not_artist(self):

        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.profile_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_song_unauthorized(self):
        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3"),
            "genre": self.genre.pk
        }

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_song_no_title(self):
        data = {
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3"),
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_song_no_audio(self):
        data = {
            "title": "new_test_song",
            "genre": self.genre.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_song_no_genre(self):
        data = {
            "title": "new_test_song",
            "audio": SimpleUploadedFile("test.mp3", b"test_bytes", content_type="audio/mp3")
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.artist_refresh_token.access_token)}")

        response = self.client.post(reverse("songs-list-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SongDetailUpdateDeleteTestCase(APITestCase):
    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD,
            is_artist=True
        )
        other_profile = Profile.objects.create_user(
            "otheremail@mail.ru",
            "other_user",
            "other_password_1234",
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
        self.other_song = Song.objects.create(
            title="other_song",
            audio="other_uri",
            cover="other_uri",
            genre=self.genre,
            artist=other_profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_songs_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.song.title)

    def test_songs_detail_unauthorized(self):
        response = self.client.get(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_songs_detail_song_id_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-detail-update-delete", kwargs={"song_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_songs_update(self):
        data = {
            "title": "updated_title"
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "updated_title")

    def test_songs_update_read_only_fields(self):
        data = {
            "id": 69,
            "artist": 69
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        song = Song.objects.get(pk=self.song.pk)
        self.assertNotEqual(song.pk, 69)
        self.assertNotEqual(song.artist.pk, 69)

    def test_songs_update_not_own_song(self):
        data = {
            "title": "updated_title"
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(
            reverse("songs-detail-update-delete", kwargs={"song_id": self.other_song.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_songs_update_unauthorized(self):
        data = {
            "title": "updated_title"
        }

        response = self.client.put(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_songs_update_song_id_not_found(self):
        data = {
            "title": "updated_title"
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(reverse("songs-detail-update-delete", kwargs={"song_id": 69}), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_songs_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        song = Song.objects.filter(pk=self.song.pk).first()
        self.assertIsNone(song)

    def test_songs_delete_not_own_song(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("songs-detail-update-delete", kwargs={"song_id": self.other_song.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_songs_delete_unauthorized(self):
        response = self.client.delete(reverse("songs-detail-update-delete", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_songs_delete_not_found_song_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("songs-detail-update-delete", kwargs={"song_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikedSongsListTestCase(APITestCase):

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
        self.profile.liked_songs.add(self.song)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_liked_songs_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-likes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["song"]["title"], self.song.title)

    def test_liked_songs_list_bad_page(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("songs-likes"), data={"page": 69})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_liked_songs_list_unauthorized(self):
        response = self.client.get(reverse("songs-likes"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SongsLikeManagementTestCase(APITestCase):

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

        self.other_song = Song.objects.create(
            title="other_test_song",
            audio="other_test_uri",
            cover="other_test_uri",
            genre=self.genre,
            artist=self.profile
        )
        self.profile.liked_songs.add(self.other_song)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_like_song(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("songs-likes-management", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        liked_songs = self.profile.liked_songs.all()
        self.assertEqual(len(liked_songs), 2)

    def test_like_song_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("songs-likes-management", kwargs={"song_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_song_unauthorized(self):
        response = self.client.post(reverse("songs-likes-management", kwargs={"song_id": self.song.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unlike_song(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("songs-likes-management", kwargs={"song_id": self.other_song.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        liked_songs = self.profile.liked_songs.all()
        self.assertEqual(len(liked_songs), 0)

    def test_unlike_song_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("songs-likes-management", kwargs={"song_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_song_unauthorized(self):
        response = self.client.delete(reverse("songs-likes-management", kwargs={"song_id": self.other_song.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

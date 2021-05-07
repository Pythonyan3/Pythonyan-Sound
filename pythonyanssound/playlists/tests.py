from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Song, Genre
from playlists.models import Playlist
from profiles.models import Profile
from profiles.tokens import CustomRefreshToken

TEST_USERNAME = "test_username"
TEST_EMAIL = "test_email@mail.ru"
TEST_PASSWORD = "test_password_69"


class PlaylistCreateListTestCase(APITestCase):
    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_playlist_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("own-playlists"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.playlist.title)

    def test_playlist_list_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("own-playlists"), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_list_unauthorized(self):
        response = self.client.get(reverse("own-playlists"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_create(self):
        data = {
            "title": "new_test_title",
            "owner": self.profile.pk
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("own-playlists"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(reverse("own-playlists"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "new_test_title")

    def test_playlist_create_unauthorized(self):
        data = {
            "title": "new_test_title",
        }

        response = self.client.post(reverse("own-playlists"), data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_create_no_title(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("own-playlists"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ShortPlaylistListTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_playlist_short_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("short-playlists-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.playlist.title)

    def test_playlist_short_list_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("short-playlists-list"), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_short_list_unauthorized(self):
        response = self.client.get(reverse("short-playlists-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PlaylistDetailsUpdateDeleteTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_playlist_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.playlist.title)

    def test_playlist_details_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("playlist-management", kwargs={"playlist_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_details_unauthorized(self):
        response = self.client.get(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_update(self):
        data = {
            "title": "new_test_title"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "new_test_title")

    def test_playlist_update_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.put(reverse("playlist-management", kwargs={"playlist_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_update_unauthorized(self):
        response = self.client.put(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_playlist_delete_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("playlist-management", kwargs={"playlist_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_delete_unauthorized(self):
        response = self.client.delete(reverse("playlist-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SongAddRemovePlaylistTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD,
            is_artist=True
        )

        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )

        self.genre = Genre.objects.create(genre="test_genre")
        self.first_song = Song.objects.create(
            title="first_song",
            audio="test_uri",
            genre=self.genre,
            artist=self.profile
        )
        self.playlist.songs.add(self.first_song)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_song_add_to_playlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        new_song = Song.objects.create(
            title="second_song",
            audio="test_uri",
            genre=self.genre,
            artist=self.profile
        )

        response = self.client.post(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": new_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_song_add_to_playlist_unauthorized(self):

        new_song = Song.objects.create(
            title="second_song",
            audio="test_uri",
            genre=self.genre,
            artist=self.profile
        )

        response = self.client.post(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": new_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_song_add_to_playlist_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        new_song = Song.objects.create(
            title="second_song",
            audio="test_uri",
            genre=self.genre,
            artist=self.profile
        )

        response = self.client.post(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": 69, "song_id": new_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_song_add_to_playlist_song_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": 69}
        ))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_song_remove_from_playlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": self.first_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_song_remove_from_playlist_unauthorized(self):
        response = self.client.delete(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": self.first_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_song_remove_from_playlist_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": 69, "song_id": self.first_song.pk}
        ))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_song_remove_from_playlist_song_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse(
            "playlists-songs-management",
            kwargs={"playlist_id": self.playlist.pk, "song_id": 69}
        ))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikedPlaylistsListTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )

        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )

        self.profile.liked_playlists.add(self.playlist)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_liked_playlists_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("liked-playlists"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.playlist.title)

    def test_liked_playlists_list_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("liked-playlists"), data={"page": 69})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_liked_playlists_list_unauthorized(self):
        response = self.client.get(reverse("liked-playlists"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LikeUnlikePlaylistTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )

        self.playlist = Playlist.objects.create(
            title="test_playlist",
            owner=self.profile
        )

        self.liked_playlist = Playlist.objects.create(
            title="liked_playlist",
            owner=self.profile
        )

        self.profile.liked_playlists.add(self.liked_playlist)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_like_playlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("liked-playlists-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("liked-playlists"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][1]["title"], self.playlist.title)

    def test_like_playlist_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("liked-playlists-management", kwargs={"playlist_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_playlist_unauthorized(self):
        response = self.client.post(reverse("liked-playlists-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unlike_playlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("liked-playlists-management", kwargs={"playlist_id": self.liked_playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("liked-playlists"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data["results"])

    def test_unlike_playlist_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(reverse("liked-playlists-management", kwargs={"playlist_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_playlist_unauthorized(self):
        response = self.client.delete(reverse("liked-playlists-management", kwargs={"playlist_id": self.playlist.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

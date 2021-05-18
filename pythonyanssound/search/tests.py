from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Song, Genre
from playlists.models import Playlist
from profiles.models import Profile
from profiles.tokens import CustomRefreshToken


class SearchTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            "test_email@mail.ru",
            "test_profile",
            "test_password"
        )
        self.artist = Profile.objects.create_user(
            "test_artist_email@mail.ru",
            "test_artist",
            "test_artist_password",
            is_artist=True
        )
        genre = Genre.objects.create(genre="test_genre")
        self.song = Song.objects.create(
            title="test_song",
            audio="audio_uri",
            artist=self.artist,
            genre=genre
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["artists"][0]["username"], self.artist.username)
        self.assertEqual(response.data["profiles"][0]["username"], self.profile.username)
        self.assertEqual(response.data["songs"][0]["title"], self.song.title)

    def test_search_unauthorized(self):
        response = self.client.get(reverse("search", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchProfileTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            "test_email@mail.ru",
            "test_profile",
            "test_password"
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_search_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-profile", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["username"], self.profile.username)

    def test_search_profile_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-profile", kwargs={"search_string": "test"}), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_profile_unauthorized(self):
        response = self.client.get(reverse("search-profile", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchArtistTestCase(APITestCase):

    def setUp(self) -> None:
        self.artist = Profile.objects.create_user(
            "test_email@mail.ru",
            "test_profile",
            "test_password",
            is_artist=True
        )
        self.refresh_token = CustomRefreshToken.for_user(self.artist)

    def test_search_artist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-artist", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["username"], self.artist.username)

    def test_search_artist_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-artist", kwargs={"search_string": "test"}), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_artist_unauthorized(self):
        response = self.client.get(reverse("search-artist", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchPlaylistTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            "test_email@mail.ru",
            "test_profile",
            "test_password"
        )
        self.playlist = Playlist.objects.create(
            title="test_title",
            owner=self.profile
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_search_playlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-playlist", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.playlist.title)

    def test_search_playlist_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-playlist", kwargs={"search_string": "test"}), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_playlist_unauthorized(self):
        response = self.client.get(reverse("search-playlist", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchSongTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            "test_email@mail.ru",
            "test_profile",
            "test_password"
        )
        genre = Genre.objects.create(
            genre="test_genre"
        )
        self.song = Song.objects.create(
            title="test_title",
            audio="test_url",
            artist=self.profile,
            genre=genre
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_search_song(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-song", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], self.song.title)

    def test_search_song_page_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("search-song", kwargs={"search_string": "test"}), data={"page": 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_song_unauthorized(self):
        response = self.client.get(reverse("search-song", kwargs={"search_string": "test"}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

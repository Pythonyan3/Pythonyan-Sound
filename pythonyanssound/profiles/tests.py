from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles.models import Profile
from profiles.tokens import VerifyToken, CustomRefreshToken

TEST_USERNAME = "test_username"
TEST_EMAIL = "test_email@mail.ru"
TEST_PASSWORD = "test_password_69"


class RegistrationTestCase(APITestCase):

    def test_registration(self):
        data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], TEST_USERNAME)
        self.assertEqual(response.data["email"], TEST_EMAIL)

    def test_registration_bad_password(self):
        data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": "wrong_password"
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_bad_email(self):
        data = {
            "username": TEST_USERNAME,
            "email": "wrong_email",
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_no_username(self):
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_no_email(self):
        data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_no_password(self):
        data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "confirm_password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_no_confirm_password(self):
        data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        }
        response = self.client.post(reverse("profile-registration"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerificationEmailTestCase(APITestCase):

    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )

        self.verify_token = VerifyToken.for_user(profile)
        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_email_verify(self):
        response = self.client.post(reverse("email-verification"), data={'token': str(self.verify_token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], ["Email verified successful."])

        profile = Profile.objects.get(email=TEST_EMAIL)
        self.assertTrue(profile.is_verified)

    def test_email_verify_bad_token(self):
        response = self.client.post(reverse("email-verification"), data={'token': "bad_token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_verify_no_token(self):
        response = self.client.post(reverse("email-verification"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailTestCase(APITestCase):

    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )

        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_resend_verify_email(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("profile-resend-verify-email"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email has been sent.")

    def test_resend_verify_email_unauthorized(self):
        response = self.client.post(reverse("profile-resend-verify-email"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LoginTestCase(APITestCase):

    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_login_by_username(self):
        data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_by_email(self):
        data = {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_bad_password(self):
        data = {
            "username": TEST_EMAIL,
            "password": "bad_password"
        }
        response = self.client.post(reverse("profile-login"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_no_username(self):
        data = {
            "password": TEST_PASSWORD
        }
        response = self.client.post(reverse("profile-login"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_no_password(self):
        data = {
            "username": TEST_EMAIL
        }
        response = self.client.post(reverse("profile-login"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):

    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_logout(self):
        data = {
            "refresh": str(self.refresh_token)
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.delete(reverse("profile-logout"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_bad_token(self):
        data = {
            "refresh": "bad_token"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.delete(reverse("profile-logout"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_no_refresh_token(self):
        data = {}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.delete(reverse("profile-logout"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthorized(self):
        data = {
            "refresh": str(self.refresh_token)
        }
        response = self.client.delete(reverse("profile-logout"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OwnProfileTestCase(APITestCase):
    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_own_profile_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.get(reverse("own-profile-details-update"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], TEST_USERNAME)
        self.assertEqual(response.data['email'], TEST_EMAIL)

    def test_own_profile_details_unauthorized(self):
        response = self.client.get(reverse("own-profile-details-update"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update(self):
        data = {
            "username": "new_username"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.put(reverse("own-profile-details-update"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "new_username")
        self.assertEqual(response.data['email'], TEST_EMAIL)

    def test_profile_update_read_only_fields(self):
        data = {
            "id": 69,
            "is_artist": True,
            "is_verified": True
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.put(reverse("own-profile-details-update"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = Profile.objects.get(email=TEST_EMAIL)
        self.assertNotEqual(profile.pk, 69)
        self.assertFalse(profile.is_artist)
        self.assertFalse(profile.is_verified)

    def test_profile_update_unauthorized(self):
        data = {
            "username": "new_username"
        }
        response = self.client.put(reverse("own-profile-details-update"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OwnProfileShortDetailsTestCase(APITestCase):
    def setUp(self) -> None:
        profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(profile)

    def test_own_profile_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.get(reverse("own-profile-short-details"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], TEST_USERNAME)

    def test_own_profile_details_unauthorized(self):
        response = self.client.get(reverse("own-profile-short-details"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileDetailsTestCase(APITestCase):
    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_profile_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.get(reverse("profile-details", kwargs={"user_id": self.profile.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], TEST_USERNAME)

    def test_profile_details_unauthorized(self):
        response = self.client.get(reverse("profile-details", kwargs={"user_id": self.profile.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_details_bad_user_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.get(reverse("profile-details", kwargs={"user_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TokenRefreshTestCase(APITestCase):
    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def token_refresh(self):
        data = {
            "refresh": str(self.refresh_token)
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-token-refresh"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def token_refresh_bad_refresh_token(self):
        data = {
            "refresh": "bad_token"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-token-refresh"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def token_refresh_no_refresh_token(self):
        data = {}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-token-refresh"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def token_refresh_unauthorized(self):
        data = {
            "refresh": str(self.refresh_token)
        }
        response = self.client.post(reverse("profile-token-refresh"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_change_password(self):
        data = {
            "old_password": TEST_PASSWORD,
            "new_password": "new_password_1234",
            "confirm_new_password": "new_password_1234"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = Profile.objects.get(email=TEST_EMAIL)
        self.assertTrue(profile.check_password("new_password_1234"))

    def test_change_password_unauthorized(self):
        data = {
            "old_password": TEST_PASSWORD,
            "new_password": "new_password_1234",
            "confirm_new_password": "new_password_1234"
        }
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_no_old_password(self):
        data = {
            "new_password": "new_password_1234",
            "confirm_new_password": "new_password_1234"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_no_new_password(self):
        data = {
            "old_password": TEST_PASSWORD,
            "confirm_new_password": "new_password_1234"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_no_confirm_new_password(self):
        data = {
            "old_password": TEST_PASSWORD,
            "new_password": "new_password_1234"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_old_password_check_error(self):
        data = {
            "old_password": "wrong_old_password",
            "new_password": "new_password_1234",
            "confirm_new_password": "wrong_new_password"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_new_password_match_error(self):
        data = {
            "old_password": TEST_PASSWORD,
            "new_password": "new_password_1234",
            "confirm_new_password": "new_password"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")
        response = self.client.post(reverse("profile-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileFollowingsListTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.new_profile = Profile.objects.create_user(
            "second.mail@mail.ru",
            "second_user",
            "second_user_password"
        )
        self.profile.followings.add(self.new_profile)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_list_of_followings(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.get(reverse("profile-followings"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], self.new_profile.username)

    def test_list_of_followings_unauthorized(self):
        response = self.client.get(reverse("profile-followings"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfilesFollowingsManagementTestCase(APITestCase):

    def setUp(self) -> None:
        self.profile = Profile.objects.create_user(
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.second_profile = Profile.objects.create_user(
            "second.mail@mail.ru",
            "second_user",
            "second_user_password"
        )
        self.third_profile = Profile.objects.create_user(
            "third.mail@mail.ru",
            "third_user",
            "third_user_password"
        )
        self.profile.followings.add(self.second_profile)
        self.refresh_token = CustomRefreshToken.for_user(self.profile)

    def test_profiles_followings_add(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("profile-followings-management", kwargs={"profile_id": self.third_profile.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(self.profile.followings.all()), 2)

    def test_profiles_followings_add_bad_profile_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.post(reverse("profile-followings-management", kwargs={"profile_id": 69}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profiles_followings_add_unauthorized(self):
        response = self.client.post(reverse("profile-followings-management", kwargs={"profile_id": self.third_profile.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(reverse("profile-followings"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profiles_followings_remove(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(
            reverse("profile-followings-management", kwargs={"profile_id": self.second_profile.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(self.profile.followings.all()), 0)

    def test_profiles_followings_remove_bad_profile_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(self.refresh_token.access_token)}")

        response = self.client.delete(
            reverse("profile-followings-management", kwargs={"profile_id": 69})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profiles_followings_remove_unauthorized(self):
        response = self.client.delete(
            reverse("profile-followings-management", kwargs={"profile_id": self.second_profile.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

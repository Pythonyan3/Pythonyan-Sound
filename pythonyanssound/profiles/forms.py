from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    """Custom Django admin form for create new Profile."""

    class Meta(UserCreationForm):
        """
        Meta class to describe additional features.

        Describes additional info:
            - model class used for create new object;
            - model fields displayed on form.
        """
        model = Profile
        fields = ('username', 'email', 'photo', 'biography', )


class ProfileChangeForm(UserChangeForm):
    """Custom Django admin form for update Profile instance."""

    class Meta:
        """
        Meta class to describe additional features.

        Describes additional info:
            - model class used for create new object;
            - model fields displayed on form.
        """
        model = Profile
        fields = ('username', 'email', 'photo', 'biography', )

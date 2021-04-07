from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Profile
        fields = ('username', 'email', 'photo', 'biography', )


class ProfileChangeForm(UserChangeForm):
    class Meta:
        model = Profile
        fields = ('username', 'email', 'photo', 'biography', )

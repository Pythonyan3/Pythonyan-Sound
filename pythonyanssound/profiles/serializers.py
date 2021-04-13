from rest_framework import serializers
from rest_framework.fields import CharField

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'email', 'username', 'photo', 'biography', 'is_artist', 'is_verified']


class ProfileCreateSerializer(serializers.ModelSerializer):
    confirm_password = CharField(max_length=128)

    class Meta:
        model = Profile
        fields = ['email', 'username', 'password', 'confirm_password']

    def save(self, **kwargs):
        profile = Profile(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )

        if self.validated_data['password'] != self.validated_data['confirm_password']:
            raise serializers.ValidationError({'password': ["Passwords must match."]})

        profile.set_password(self.validated_data['password'])
        profile.save()
        return profile

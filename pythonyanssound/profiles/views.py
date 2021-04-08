from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .permissions import IsOwnProfile
from .serializers import ProfileDetailSerializer


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated & IsOwnProfile]

    def get(self, request, user_id):
        profile = Profile.objects.get(pk=user_id, is_active=True)
        serializer = ProfileDetailSerializer(profile)
        return Response(serializer.data)

    def put(self, request, user_id):
        profile = Profile.objects.get(pk=user_id, is_active=True)
        self.check_object_permissions(request, profile)
        serializer = ProfileDetailSerializer(instance=profile, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)



class ProfileCreateView(APIView):
    def post(self, request):
        pass

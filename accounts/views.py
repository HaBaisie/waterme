from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import build_token_pair, decode_token
from .serializers import AddressSerializer, LoginSerializer, ProfileUpdateSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token_pair = build_token_pair(user)
        return Response(
            {
                'refresh': token_pair['refresh'],
                'access': token_pair['access'],
                'user': UserSerializer(user).data,
            }
        )


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'refresh is required.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh)
        if payload.get('type') != 'refresh':
            return Response({'detail': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(pk=payload['sub'])
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(build_token_pair(user))


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Profile updated', 'user': UserSerializer(request.user).data})


class AddressListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)


class AddressDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, address_id):
        deleted, _ = request.user.addresses.filter(pk=address_id).delete()
        if not deleted:
            return Response({'detail': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Address removed'})
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer
from .authentication import CustomJWTAuthentication

class RegisterView(APIView):
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiTypes.OBJECT
        },
        description="Register a new user with the provided details."
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Username of the user'},
                    'password': {'type': 'string', 'format': 'password', 'description': 'Password of the user'},
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string', 'description': 'JWT refresh token'},
                    'access': {'type': 'string', 'description': 'JWT access token'},
                    'user': UserSerializer
                }
            },
            401: OpenApiTypes.OBJECT
        },
        description="Authenticate a user and return JWT tokens."
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        auth_result = CustomJWTAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    @extend_schema(
        responses={200: UserSerializer},
        description="Retrieve the authenticated user's profile."
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT
        },
        description="Update the authenticated user's profile."
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
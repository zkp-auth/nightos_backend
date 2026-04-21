from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomUserSerializer

class LoginView(APIView):
    """
    Session-based login endpoint for the API.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data("email")
        password = request.data("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)

        return Response(
            {
                    "detail": "Login successful.",
                    "user": CustomUserSerializer(user).data
                },
                status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    """
    Session-based logout endpoint for the API.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Logout successful."},
            status=status.HTTP_200_OK
        )

class CurrentUserView(APIView):
    """
    Return the currently authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)




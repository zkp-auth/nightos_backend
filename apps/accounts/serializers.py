from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Read serializer for the currently authenticated user.
    """

    full_name = serializers.CharField(read_only=True)
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        read_only_fields =fields
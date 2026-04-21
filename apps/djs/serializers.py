from rest_framework import serializers

from .models import DJ, Genre

class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for music genres.
    """

    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DJSerializer(serializers.ModelSerializer):
    """
    Read serializer or DJs.

    Genres are nested for better frontend display.
    """
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = DJ
        fields = [
            "id",
            "full_name",
            "stage_name",
            "phone",
            "email",
            "genres",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class DJWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for DJs.

    Genres are assigned by primary key for simpler creation/update.
    """
    genres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        required=False,
    )

    class Meta:
        model = DJ
        fields = [
            "id",
            "full_name",
            "stage_name",
            "phone",
            "email",
            "genres",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        genres = validated_data.pop("genres")
        dj = DJ.objects.create(**validated_data)
        if genres:
            dj.genres.set(genres)
        return dj

    def update(self, instance, validated_data):
        genres = validated_data.pop("genres", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if genres is not None:
            instance.genres.set(genres)

        return instance


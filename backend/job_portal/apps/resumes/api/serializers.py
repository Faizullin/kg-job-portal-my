from rest_framework import serializers

from ..models import MasterResume


class MasterResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterResume
        fields = [
            "id",
            "title",
            "content",
            "status",
            "master",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

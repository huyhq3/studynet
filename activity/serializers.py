from rest_framework import serializers

from activity.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'course', 'lesson', 'status')
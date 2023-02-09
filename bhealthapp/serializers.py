from rest_framework import serializers

from .models import Doctor, Appointment


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "name",
            "surname",
            "service"
        ]

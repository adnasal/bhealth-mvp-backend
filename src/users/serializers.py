from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Appointment, Lab, User, Type, City, Service, Result, UserRating, LabService


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "name",
            "country",
            "postal_code",
        ]


class CityViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "name",
            "country",
            "postal_code",
        ]
        depth = 1


class PatientLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]


class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
                                        validated_data['password'])
        return user

    class Meta:
        model = User
        fields = [
            "profile_picture",
            "profile_link",
            "username",
            "name",
            "surname",
            "password",
            "phone_number",
            "email",
            "dob",
            "address",
            "city",
            "joined_at",
            "is_blocked",
            "is_email_verified",
            "gender",
        ]


class PatientViewSerializer(serializers.ModelSerializer):
    gender = ChoiceField(choices=User.GENDER_CHOICES)

    class Meta:
        model = User
        fields = [
            "profile_picture",
            "profile_link",
            "name",
            "surname",
            "password",
            "phone_number",
            "email",
            "dob",
            "address",
            "city",
            "joined_at",
            "is_blocked",
            "is_email_verified",
            "gender",
        ]
        depth = 1


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = [
            "city",
            "name",
            "password",
            "address",
            "phone_number",
            "email",
            "website",
        ]


class LabViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = [
            "city",
            "name",
            "password",
            "address",
            "phone_number",
            "email",
            "website",
        ]
        depth = 1


class LabServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabService
        fields = [
            "lab_service",
            "service",
        ]


class LabServiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabService
        fields = [
            "lab_service",
            "service",
        ]
        depth = 1


class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = [
            "user",
            "lab",
            "rating",
        ]


class UserRatingViewSerializer(serializers.ModelSerializer):
    rating = ChoiceField(choices=UserRating.RATING_CHOICES)

    class Meta:
        model = UserRating
        fields = [
            "user",
            "lab",
            "rating",
        ]
        depth = 1


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = [
            "name",
            "description",
        ]


class TypeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = [
            "name",
            "description",
        ]
        depth = 1


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "name",
            "duration",
            "description",
            "type",
        ]


class ServiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "name",
            "duration",
            "description",
            "type",
        ]
        depth = 1


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "city_appointment",
            "lab_appointment",
            "service_appointment",
            "date",
            "patient",
            "status",
        ]


class AppointmentViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "city_appointment",
            "lab_appointment",
            "service_appointment",
            "date",
            "patient",
            "status",
        ]
        depth = 1


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "appointment",
            "patient",
            "pdf",
        ]


class ResultViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "appointment",
            "patient",
            "pdf",
        ]
        depth = 1

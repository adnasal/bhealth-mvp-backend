from distutils.command.upload import upload

from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Appointment, Lab, User, Type, City, Service, Result, UserRating, LabService, Notification
from src.files.models import File


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
            "rating",
        ]


class UserRatingViewSerializer(serializers.ModelSerializer):
    rating = ChoiceField(choices=UserRating.RATING_CHOICES)

    class Meta:
        model = UserRating
        fields = [
            "user",
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

        lab_appointment = serializers.SerializerMethodField()
        service_appointment = serializers.SerializerMethodField()
        patient = serializers.SerializerMethodField()
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

        def get_lab_appointment(self, obj):
            lab = obj.lab_appointment
            return {
                'id': lab.id,
                'name': lab.name,
                'password': lab.password,
                'address': lab.address,
                'phone_number': lab.phone_number,
                'email': lab.email,
                'website': lab.website,
                'city': {
                    'id': lab.city.id,
                    'name': lab.city.name,
                    # add more fields as needed
                },
            }

        def get_service_appointment(self, obj):
            service = obj.service_appointment
            return {
                'id': service.id,
                'name': service.name,
                'duration': service.duration.total_seconds(),
                'description': service.description,
                'type': {
                    'id': service.type.id,
                    'name': service.type.name,
                    # add more fields as needed
                },
            }

        def get_patient(self, obj):
            patient = obj.patient
            return {
                'id': patient.id,
                'name': patient.name,
                'surname': patient.surname,
                'profile_picture': patient.profile_picture.url,
                'profile_link': patient.profile_link,
                'phone_number': patient.phone_number,
                'email': patient.email,
                'dob': patient.dob,
                'address': patient.address,
                'city': {
                    'id': patient.city.id,
                    'name': patient.city.name,
                    # add more fields as needed
                },
                'joined_at': patient.joined_at,
                'is_blocked': patient.is_blocked,
                'is_email_verified': patient.is_email_verified,
                'gender': patient.gender,
            }



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
            "pdf",
        ]




class ResultViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "appointment",
            "pdf",
        ]
        depth = 1


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "notification_lab",
            "notification_user",
            "notification_appointment",
            "message",
            "is_confirmed",
            "is_declined"
        ]


class NotificationViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "notification_lab",
            "notification_user",
            "notification_appointment",
            "message",
            "is_confirmed",
            "is_declined"
        ]
        depth = 1

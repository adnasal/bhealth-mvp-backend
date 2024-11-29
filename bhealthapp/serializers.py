from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from bhealthapp.models import Appointment, Lab, User, Type, City, Service, Result, UserRating, LabService, Notification


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
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]


class PatientSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "profile_picture",
            "password",
            "phone_number",
            "email",
            "dob",
            "address",
            "city",
            "gender",
        ]


class PatientViewSerializer(serializers.ModelSerializer):
    gender = ChoiceField(choices=User.GENDER_CHOICES)

    class Meta:
        model = User
        fields = [
            "username",
            "profile_picture",
            "profile_link",
            "password",
            "phone_number",
            "email",
            "dob",
            "address",
            "city",
            "is_blocked",
            "is_email_verified",
            "gender",
        ]
        depth = 1


class LabSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Lab.objects.all())]
    )

    password = serializers.CharField(min_length=8)

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
            "working_days",
            "profile_picture",
            "average_rating"
        ]


class LabViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = [
            "pk",
            "city",
            "name",
            "password",
            "address",
            "phone_number",
            "email",
            "description",
            "website",
            "profile_picture",
            "average_rating",
            "working_days"
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
            "type",
        ]


class ServiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "name",
            "duration",
            "type",
        ]
        depth = 1


class AppointmentPatientSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()

    class Meta:
        model = User
        fields = [
            'username',
            'profile_picture'
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    lab_appointment = serializers.StringRelatedField()
    service_appointment = serializers.SerializerMethodField()
    patient = AppointmentPatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "lab_appointment",
            "service_appointment",
            "patient",
            "date",
            "status",
            "fee",
            "doctor"
        ]

    def get_service_appointment(self, obj):
        return obj.service_appointment.name


class AppointmentViewSerializer(serializers.ModelSerializer):
    lab_appointment = LabViewSerializer()

    class Meta:
        model = Appointment
        fields = [
            "lab_appointment",
            "service_appointment",
            "date",
            "patient",
            "status",
            "fee",
            "doctor"
        ]
        depth = 1


class AddRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = [
            "user",
            "rating"
        ]


class AppointmentCancelSerializer(serializers.Serializer):
    pk = serializers.IntegerField()

    def update(self, instance, validated_data):
        instance.status = 2
        instance.save()
        return instance


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
    notification_appointment = AppointmentViewSerializer()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_appointment",
            "message",
            "is_confirmed",
            "notification_date"
        ]


class NotificationViewSerializer(serializers.ModelSerializer):
    notification_appointment = AppointmentViewSerializer()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_appointment",
            "message",
            "is_confirmed",
            "notification_date"
        ]
        depth = 1


class RequestViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "patient",
            "service_appointment"
        ]
        depth = 1

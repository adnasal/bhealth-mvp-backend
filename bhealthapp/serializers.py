from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from bhealthapp.models import Appointment, Institution, User, City, Service, MedicalRecord, InstitutionService, \
    Notification, Country


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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "country_name",
            "country_code"
        ]


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = City
        fields = [
            "city_name",
            "country",
        ]


class CityViewSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = City
        fields = [
            "city_name",
             "country"
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
            "username",
            "password",
            "phone_number",
            "email",
            "dob",
            "gender",
        ]


class PatientViewSerializer(serializers.ModelSerializer):
    gender = ChoiceField(choices=User.GENDER_CHOICES)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "phone_number",
            "email",
            "dob",
            "is_blocked",
            "is_email_verified",
            "gender",
        ]
        depth = 1


class InstitutionSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Institution.objects.all())]
    )

    password = serializers.CharField(min_length=8)

    class Meta:
        model = Institution
        fields = [
            "city_id",
            "institution_name",
            "password",
            "address",
            "phone_numbers",
            "emails",
            "website",
            "description",
            "rating"
        ]


class InstitutionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            "pk",
            "city_id",
            "institution_name",
            "password",
            "address",
            "phone_numbers",
            "emails",
            "description",
            "website",
            "rating",
            "description"
        ]
        depth = 1


class InstitutionServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionService
        fields = [
            "institution_id",
            "service_id",
            "description",
            "price"
        ]


class InstitutionServiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionService
        fields = [
            "institution_id",
            "service_id",
            "description",
            "price"
        ]
        depth = 1




class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "service_name",
            "service_category",
            "description",
            "is_special_offer"
        ]


class ServiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "service_name",
            "service_category",
            "description",
            "is_special_offer"
        ]
        depth = 1


'''
class AppointmentPatientSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()

    class Meta:
        model = User
        fields = [
            'username',
            'profile_picture'
        ]

'''

class AppointmentSerializer(serializers.ModelSerializer):
    institution_appointment = serializers.StringRelatedField()
    service_appointment = serializers.SerializerMethodField()
   # patient = AppointmentPatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "institution_appointment",
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
    institution_appointment = InstitutionViewSerializer()

    class Meta:
        model = Appointment
        fields = [
            "doctor_id",
            "institution_service_id",
            "datetime",
            "patient_id",
            "appointment_status",
            "description",
            "is_completed"
        ]
        depth = 1



class AppointmentCancelSerializer(serializers.Serializer):
    pk = serializers.IntegerField()

    def update(self, instance, validated_data):
        instance.status = 2
        instance.save()
        return instance


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            "appointment_id",
            "user_id",
            "file"
        ]


class MedicalRecordViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            "appointment_id",
            "user_id",
            "file"
        ]
        depth = 1


class NotificationSerializer(serializers.ModelSerializer):
    notification_appointment = AppointmentViewSerializer()

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "notification_appointment",
            "user_id",
            "payload_data",
        ]



class NotificationViewSerializer(serializers.ModelSerializer):
    notification_appointment = AppointmentViewSerializer()

    class Meta:
        model = Notification
        fields = [
             "notification_id",
            "user_id",
            "payload_data",
            "notification_appointment"
        ]
        depth = 1


class RequestViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "patient_id",
            "appointment_id",
        ]
        depth = 1

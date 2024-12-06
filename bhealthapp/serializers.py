from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from bhealthapp.models import Appointment, Institution, User, City, Service, MedicalRecord, InstitutionService, \
    Notification, Country, Drug, Diagnosis, Treatment, Role


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

from rest_framework import serializers
from bhealthapp.models import InstitutionWorkingHours, Institution

class InstitutionWorkingHoursSerializer(serializers.ModelSerializer):
    institution_id = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())

    class Meta:
        model = InstitutionWorkingHours
        fields = [
            'institution_working_hour_id',
            'institution_id',
            'day_of_week',
            'open_time',
            'close_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['institution_working_hour_id', 'created_at', 'updated_at']


class PatientLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]

class InstitutionLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)

    class Meta:
        model = Institution
        fields = [
            "emails",
            "password",
        ]

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Password fields didn't match.")
        return data

    def save(self):
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        try:
            user = self.verify_reset_token(token)
            user.set_password(new_password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Token validation failed: {str(e)}")

    def verify_reset_token(self, token):
        try:
            uidb64, token = token.split('-')
            uid = urlsafe_base64_decode(uidb64).decode()

            user = User.objects.get(pk=uid)

            token_generator = PasswordResetTokenGenerator()
            if not token_generator.check_token(user, token):
                raise serializers.ValidationError("Invalid or expired token.")

            return user
        except (ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token.")

class PatientSerializer(serializers.ModelSerializer):
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
            "is_email_verified",
            "gender",
        ]
        depth = 1


class InstitutionSerializer(serializers.ModelSerializer):
    city_id = serializers.StringRelatedField()
    emails = serializers.EmailField(
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



class AppointmentPatientSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()

    class Meta:
        model = User
        fields = [
            'username',
            'profile_picture'
        ]



class AppointmentSerializer(serializers.ModelSerializer):
    institution_appointment = serializers.StringRelatedField()
    service_appointment = serializers.SerializerMethodField()
    patient = AppointmentPatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "institution_appointment",
            "service_appointment",
            "patient",
            "datetime",
            "status",
            "doctor_id"
        ]

    def get_service_appointment(self, obj):
        return obj.service_appointment.name


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = [
            "drug_name",
            "drug_code",
            "vendor",
            "drug_type",
            "dosage",
            "is_prescription_required",
            "side_effects"
        ]

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = [
            "diagnosis_name",
            "diagnosis_code",
            "diagnosis_type",
        ]

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = [
            "party_diagnosis_id",
            "drug_id",
            "description",
        ]

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "role_name",
            "description",
        ]


class AppointmentViewSerializer(serializers.ModelSerializer):
    institution_appointment = InstitutionViewSerializer()

    class Meta:
        model = Appointment
        fields = [
            "doctor_id",
            "institution_service_id",
            "datetime",
            "patient_id",
            "status",
            "description",
            "is_completed",
            "institution_appointment"
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

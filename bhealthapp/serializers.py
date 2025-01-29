from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from bhealthapp.models import Appointment, Institution, User, City, Service, MedicalRecord, InstitutionService, \
    Notification, Country, Drug, Diagnosis, Treatment, Role, Institution, InstitutionWorkingHours


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


class CountryViewSerializer(serializers.Serializer):
    country_id = serializers.IntegerField()
    country_name = serializers.CharField()
    country_code = serializers.CharField()
    is_eu = serializers.BooleanField()
    phone_code = serializers.CharField()


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = City
        fields = [
            "city_name",
            "country",
        ]


class CityViewSerializer(serializers.Serializer):
    city_id = serializers.IntegerField()
    city_name = serializers.CharField()
    country_id = serializers.IntegerField()
    country_name = serializers.CharField()
    country_code = serializers.CharField()
    is_eu = serializers.BooleanField()
    phone_code = serializers.CharField()


class SaveMedicalRecordTemplateSerializer(serializers.Serializer):
    medical_record_template_id = serializers.IntegerField()
    institution_id = serializers.IntegerField(required=False)
    template = serializers.JSONField(required=False)
    is_active = serializers.BooleanField(default=True)


class MedicalRecordTemplateViewSerializer(serializers.Serializer):
    medical_record_template_id = serializers.IntegerField()
    institution_id = serializers.IntegerField()
    template = serializers.JSONField()
    is_active = serializers.BooleanField()


class SaveInstitutionWorkingHoursSerializer(serializers.Serializer):
    institution_id = serializers.IntegerField()
    day_of_week = serializers.CharField()
    open_time = serializers.TimeField()
    close_time = serializers.TimeField()


class InstitutionWorkingHoursSerializer(serializers.Serializer):
    institution_working_hour_id = serializers.IntegerField()
    day_of_week = serializers.CharField()
    open_time = serializers.TimeField()
    close_time = serializers.TimeField()


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
        user_id = serializers.IntegerField()
        party_id = serializers.IntegerField()
        email = serializers.EmailField()
        username = serializers.CharField(max_length=255)
        phone_number = serializers.CharField(max_length=255)
        is_email_verified = serializers.BooleanField()
        is_phone_number_verified = serializers.BooleanField()
        status = serializers.CharField(max_length=50)
        registration_date = serializers.DateTimeField()

class UserSettingsViewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    notifications = serializers.JSONField()
    additional_data = serializers.JSONField()

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


class InstitutionUserViewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    party_id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()
    phone_number = serializers.CharField()
    is_email_verified = serializers.BooleanField()
    is_phone_number_verified = serializers.BooleanField()
    status = serializers.CharField()
    registration_date = serializers.DateTimeField()

class InstitutionViewSerializer(serializers.Serializer):
    institution_id = serializers.IntegerField()
    institution_name = serializers.CharField()
    city_id = serializers.IntegerField()
    phone_number = serializers.CharField()
    address = serializers.CharField()
    website = serializers.URLField()
    email = serializers.EmailField()
    latitude = serializers.DecimalField(max_digits=10, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=6)
    founded = serializers.DateTimeField()
    rating = serializers.FloatField()
    status = serializers.CharField()
    subsidiary_id = serializers.IntegerField()
    subsidiary_name = serializers.CharField()
    is_office = serializers.BooleanField()
    registration_date = serializers.DateTimeField()


class InstitutionServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionService
        fields = [
            "institution_id",
            "service_id",
            "description",
            "price"
        ]


class ServiceViewSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    service_category = serializers.CharField()
    description = serializers.CharField()




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

class SaveServiceSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    service_name = serializers.CharField(required=False, allow_null=True)
    service_category = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)


class InstitutionServiceViewSerializer(serializers.Serializer):
    institution_service = serializers.IntegerField()
    institution_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    service_category = serializers.CharField()
    service_description = serializers.CharField()
    institution_service_description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    duration = serializers.DurationField()
    is_active = serializers.BooleanField()


class SaveInstitutionServiceSerializer(serializers.Serializer):
    institution_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_active = serializers.BooleanField()
    duration = serializers.DurationField()

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

class RoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    role_code = serializers.CharField()
    role_name = serializers.CharField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()

class UserRoleViewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    institution_user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    role_code = serializers.CharField()
    role_name = serializers.CharField()

class InstitutionPartyViewSerializer(serializers.Serializer):
    party_id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    city_id = serializers.IntegerField()
    city_name = serializers.CharField()
    country_id = serializers.IntegerField()
    country_name = serializers.CharField()
    country_code = serializers.CharField()
    gender = serializers.CharField()
    address = serializers.CharField()
    descended_at = serializers.DateTimeField()
    description = serializers.CharField()
    first_visit_date = serializers.DateTimeField()
    notes = serializers.CharField()


class AppointmentViewSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
    institution_service_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    service_category = serializers.CharField()
    fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    institution_id = serializers.IntegerField()
    institution_name = serializers.CharField()
    patient_id = serializers.IntegerField()
    patient_user_id = serializers.IntegerField()
    patient_first_name = serializers.CharField()
    patient_last_name = serializers.CharField()
    patient_phone_number = serializers.CharField()
    patient_email = serializers.EmailField()
    doctor_id = serializers.IntegerField()
    doctor_user_id = serializers.IntegerField()
    doctor_first_name = serializers.CharField()
    doctor_last_name = serializers.CharField()
    doctor_phone_number = serializers.CharField()
    doctor_email = serializers.EmailField()
    date_time = serializers.DateTimeField()
    description = serializers.CharField()
    status = serializers.CharField()
    is_completed = serializers.BooleanField()
    scheduled_at = serializers.DateTimeField()



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

class PartyViewSerializer(serializers.Serializer):
    party_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    city_id = serializers.IntegerField()
    city_name = serializers.CharField(max_length=255)
    country_id = serializers.IntegerField()
    country_name = serializers.CharField(max_length=255)
    country_code = serializers.CharField(max_length=10)
    gender = serializers.CharField(max_length=10)
    address = serializers.CharField(max_length=255)
    descended_at = serializers.DateTimeField()
    description = serializers.CharField(max_length=500, required=False)
    first_visit_date = serializers.DateTimeField()
    notes = serializers.CharField(max_length=500, required=False)

class MedicalRecordViewSerializer(serializers.Serializer):
    medical_record_id = serializers.IntegerField()
    appointment_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    file = serializers.CharField()
    notes = serializers.CharField()
    reference_values = serializers.JSONField()


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

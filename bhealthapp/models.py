from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework_simplejwt.tokens import RefreshToken

from src.common.helpers import build_absolute_uri
from src.notifications.services import notify, ACTIVITY_USER_RESETS_PASS


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    reset_password_path = reverse('password_reset:reset-password-confirm')
    context = {'username': reset_password_token.user.username, 'email': reset_password_token.user.email,
        'reset_password_url': build_absolute_uri(f'{reset_password_path}?token={reset_password_token.key}'), }

    notify(ACTIVITY_USER_RESETS_PASS, context=context, email_to=[reset_password_token.user.email])


class GetOrNoneManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Country(models.Model):
    country_id = models.BigAutoField(primary_key=True, default=1)
    country_name = models.TextField(default='Bosnia and Herzegovina', max_length=255, null=False)
    country_code = models.TextField(default='BA', max_length=2, unique=True, null=False)
    phone_code = models.TextField(default='+387', max_length=2, unique=True, null=False)
    is_eu = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['country_name']


class City(models.Model):
    city_id = models.BigAutoField(primary_key=True, default=1)
    city_name = models.TextField(default='Sarajevo', max_length=255, null=False)
    country_id = models.ForeignKey(Country, related_name='cities', on_delete=models.DO_NOTHING, default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['city_name']


class User(AbstractUser):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = ((GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'),)
    USER_STATUS_ACTIVE = 'active'
    USER_STATUS_INACTIVE = 'inactive'
    USER_STATUS_BLOCKED = 'blocked'
    USER_STATUS_CHOICES = ((USER_STATUS_ACTIVE, 'Active'), (USER_STATUS_INACTIVE, 'Inactive'), (USER_STATUS_BLOCKED, 'Blocked'))
    user_id = models.BigAutoField(primary_key=True, default=1)
    username = models.TextField(max_length=150, null=True, blank=True, unique=True)
    password = models.TextField(max_length=255)
    phone_number = models.CharField(null=True, blank=True, max_length=255)
    email = models.TextField(null=False, max_length=255)
    google_id = models.TextField(null=True, max_length=255)
    apple_id = models.TextField(null=True, max_length=255)
    facebook_id = models.TextField(null=True, max_length=255)
    dob = models.DateField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    party_id = models.ForeignKey('Party', related_name='user_party', on_delete=models.DO_NOTHING, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, default=GENDER_FEMALE, )
    status = models.CharField(max_length=20, choices=USER_STATUS_CHOICES, default=USER_STATUS_ACTIVE, )

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)

        return {'refresh': str(refresh), 'access': str(refresh.access_token), }

    def __str__(self):
        return self.username


class Institution(models.Model):
    INSTITUTION_STATUS_ACTIVE = 'active'
    INSTITUTION_STATUS_INACTIVE = 'inactive'
    INSTITUTION_STATUS_CHOICES = ((INSTITUTION_STATUS_ACTIVE, 'Active'), (INSTITUTION_STATUS_INACTIVE, 'Inactive'),)
    institution_id = models.BigAutoField(primary_key=True)
    city_id = models.ForeignKey(City, related_name='institution_city', on_delete=models.DO_NOTHING, default=1)
    institution_name = models.TextField(null=False, max_length=255, default=None)
    password = models.CharField(max_length=100)
    address = models.TextField(null=False, max_length=350, default=None)
    latitude = models.DecimalField(null=False, max_digits=7, decimal_places=2, default=None)
    longitude = models.DecimalField(null=False, max_digits=7, decimal_places=2, default=None)
    phone_number = models.TextField(null=False, blank=False)
    email = models.TextField(null=False, max_length=255)
    description = models.TextField(null=False, default='Default description')
    website = models.TextField(max_length=255, blank=True, null=True, default='bhealth.ba')
    subsidiary = models.ForeignKey('self', related_name='subsidiaries', on_delete=models.DO_NOTHING, null=True, blank=True)
    logo = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    founded = models.DateField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_office = models.BooleanField(default=False)

    institution_status = models.CharField(max_length=20, choices=INSTITUTION_STATUS_CHOICES,
        default=INSTITUTION_STATUS_ACTIVE, )

    '''
    def get_phone_numbers(self):
        if self.phone_numbers:
            return self.phone_numbers.split(',')
        return []

    def set_phone_numbers(self, phone_list):
        self.phone_numbers = ','.join(phone_list)
        self.save()

    def get_emails(self):
        if self.emails:
            return self.emails.split(',')
        return []

    def set_emails(self, emails):
        self.emails = ','.join(emails)
        self.save()
    '''

    def __str__(self):
        return self.institution_name


class InstitutionUser(models.Model):
    institution_user_id = models.BigAutoField(primary_key=True, default=1)
    user_id = models.ForeignKey(User, related_name='institution_user', on_delete=models.DO_NOTHING)
    institution_id = models.ForeignKey(Institution, related_name='institution_user', on_delete=models.DO_NOTHING)
    roles = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_roles(self):
        if self.roles:
            return self.roles.split(',')
        return []

    def set_roles(self, roles):
        self.roles = ','.join(roles)
        self.save()


class Party(models.Model):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = ((GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'),)
    party_id = models.BigAutoField(primary_key=True)
    first_name = models.TextField(null=False, max_length=255, default=None)
    last_name = models.TextField(null=False, max_length=255, default=None)
    email = models.TextField(max_length=255, default=None)
    phone_code = models.TextField(max_length=255, default=None)
    phone_number = models.TextField(max_length=255, default=None)
    city_id = models.ForeignKey(City, related_name='party_city', on_delete=models.DO_NOTHING, default=1)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, default=GENDER_FEMALE, )
    birth_date = models.DateField(null=True)
    address = models.TextField(null=False, max_length=350, default=None)
    ssn = models.TextField(max_length=255, default=None) # to be checked
    descended_at = models.DateTimeField(auto_now=True)
    is_doctor = models.BooleanField(default=False)
    description = models.TextField(null=False, default='Default description')
    specialization = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationHistory(models.Model):
    notification_id = models.BigAutoField(primary_key=True, default=0)
    event_name = models.TextField(null=False, default=None)
    user_id = models.ForeignKey(User, related_name='notification_history_user', on_delete=models.DO_NOTHING, default=1)
    payload_data = models.JSONField(null=True, blank=True) # message
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class InstitutionParty(models.Model):
    institution_party_id = models.BigAutoField(primary_key=True, default=0)
    institution_id = models.ForeignKey(Institution, related_name='institution_party', on_delete=models.DO_NOTHING)
    party_id = models.ForeignKey(Party, related_name='institution_party', on_delete=models.DO_NOTHING)
    first_visit_date = models.DateTimeField(auto_created=True)
    notes = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


'''
class UserRating(models.Model):
    user = models.ForeignKey(User, related_name='user_rating', on_delete=models.DO_NOTHING)
    lab = models.ForeignKey(Lab, related_name='lab_rating', on_delete=models.DO_NOTHING)

    RATING_NULL = 0
    RATING_ONE = 1
    RATING_TWO = 2
    RATING_THREE = 3
    RATING_FOUR = 4
    RATING_FIVE = 5

    RATING_CHOICES = (
        (RATING_NULL, 'No Rating'),
        (RATING_ONE, '1 star'),
        (RATING_TWO, '2 stars'),
        (RATING_THREE, '3 stars'),
        (RATING_FOUR, '4 stars'),
        (RATING_FIVE, '5 stars'),
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=RATING_NULL,
    )


class Type(models.Model):
    name = models.TextField(null=False, max_length=255, default=None)
    description = models.TextField(null=False, max_length=1000, default='Type Description')
'''


class Service(models.Model):
    service_id = models.BigAutoField(primary_key=True, default=1)
    service_name = models.TextField(null=False, max_length=255, default=None)
    service_category = models.TextField(null=False, max_length=255, default=None)
    description = models.TextField(null=False, default='Default description')
    is_special_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class InstitutionService(models.Model):
    institution_service_id = models.BigAutoField(primary_key=True, default=1)
    service_id = models.ForeignKey(Service, related_name='institution_service', on_delete=models.DO_NOTHING, default=1)
    institution_id = models.ForeignKey(Institution, related_name='institution_service_name',
                                       on_delete=models.DO_NOTHING)
    description = models.TextField(null=False, default='Default description')
    price = models.DecimalField(null=False, max_digits=7, decimal_places=2, default=None)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Appointment(models.Model):
    appointment_id = models.BigAutoField(primary_key=True)
    institution_service_id = models.ForeignKey(InstitutionService, related_name='appointment_institution_service', on_delete=models.DO_NOTHING, blank=True, null=True)
    patient_id = models.ForeignKey(Party, related_name='appointment_patient_party', on_delete=models.DO_NOTHING, blank=True, null=True)
    patient_user_id = models.ForeignKey(User, related_name='appointment_patient', on_delete=models.DO_NOTHING,
                                        blank=True, null=True)
    doctor_id = models.ForeignKey(Party, related_name='appointment_doctor_party', on_delete=models.DO_NOTHING, blank=True,
                                  null=True)
    doctor_user_id = models.ForeignKey(User, related_name='appointment_doctor', on_delete=models.DO_NOTHING,
                                       blank=True, null=True)
    datetime = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=False, default='Default description')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_PENDING = 0
    STATUS_CONFIRMED = 1
    STATUS_CANCELED = 2

    STATUS_CHOICES = ((STATUS_PENDING, 'Pending Appointment'), (STATUS_CONFIRMED, 'Confirmed Appointment'),
                      (STATUS_CANCELED, 'Canceled Appointment'),)

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING, )


class MedicalRecord(models.Model):
    medical_record_id = models.BigAutoField(primary_key=True)
    appointment_id = models.ForeignKey(Appointment, related_name='appointment_result', on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(User, related_name='patient_medical_record', on_delete=models.DO_NOTHING, default=1)
    file = models.TextField(default='File')
    notes = models.TextField(default='Message')
    downloads = models.IntegerField(default=0)
    reference_values = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(
        auto_now=True)
    # pdf = models.FileField(upload_to='pdf', default='src/results/Patient Medical History Report.pdf')


class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True, default=0)
    user_id = models.ForeignKey(User, related_name='notification_user', on_delete=models.DO_NOTHING, default=1)
    event_name = models.TextField(default='Event')
    payload_data = models.JSONField(null=True, blank=True) # message
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class InstitutionWorkingHours(models.Model):
    institution_working_hour_id = models.BigAutoField(primary_key=True)
    institution_id = models.ForeignKey(Institution, related_name='institution_working_hours',
                                       on_delete=models.DO_NOTHING)

    DAY_1 = 1
    DAY_2 = 2
    DAY_3 = 3
    DAY_4 = 4
    DAY_5 = 5
    DAY_6 = 6
    DAY_7 = 7

    DAYS_CHOICES = ((DAY_1, 'Monday'), (DAY_2, 'Tuesday'), (DAY_3, 'Wednesday'), (DAY_4, 'Thursday'), (DAY_5, 'Friday'), (DAY_6, 'Saturday'), (DAY_7, 'Sunday'))
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS_CHOICES, default=DAY_1, )
    open_time = models.TimeField(null=False, default=None)
    close_time = models.TimeField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=1) # TBD
    notifications = models.JSONField(null=True, blank=True)
    additional_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Drug(models.Model):
    drug_id = models.BigAutoField(primary_key=True)
    drug_name = models.TextField(null=False, default=None)
    drug_code = models.TextField(null=False, default=None)
    vendor = models.TextField(null=False, default=None)
    drug_type = models.TextField(null=False, default=None)
    dosage = models.TextField(null=False, default=None)
    description = models.TextField(null=False, default=None)
    is_prescription_required = models.BooleanField(default=False)
    side_effects = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Diagnosis(models.Model):
    diagnosis_id = models.BigAutoField(primary_key=True)
    #parent_diagnosis_id = models.ForeignKey(Diagnosis, on_delete=models.DO_NOTHING, null=False, blank=False)
    diagnosis_name = models.TextField(null=False, default=None)
    diagnosis_code = models.TextField(null=False, default=None)
    diagnosis_type = models.TextField(null=False, default=None) # will be types
    description = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class PartyDiagnosis(models.Model):
    party_diagnosis_id = models.BigAutoField(primary_key=True)
    diagnosis_id = models.ForeignKey(Diagnosis, related_name='party_diagnosis', on_delete=models.DO_NOTHING)
    party_id = models.ForeignKey(Party, related_name='party_diagnosis', on_delete=models.DO_NOTHING)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
    description = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Treatment(models.Model):
    treatment_id = models.BigAutoField(primary_key=True)
    party_diagnosis_id = models.ForeignKey(PartyDiagnosis, related_name='treatment_party_diagnosis',
                                           on_delete=models.DO_NOTHING)
    drug_id = models.ForeignKey(Drug, related_name='treatment_drug', on_delete=models.DO_NOTHING)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
    description = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.TextField(null=False, default=None)
    description = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class ReferenceValue(models.Model):
    reference_value_id = models.BigAutoField(primary_key=True)
    institution_service_id = models.ForeignKey(InstitutionService, related_name='institution_service',
                                               on_delete=models.DO_NOTHING, default=1)
    reference_value_name = models.BigIntegerField(null=False, default=None)
    lower_limit = models.TextField(null=False, default=None)
    upper_limit = models.TextField(null=False, default=None)
    low_description = models.TextField(null=False, default=None)
    high_description = models.TextField(null=False, default=None)
    normal_description = models.TextField(null=False, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

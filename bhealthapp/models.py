from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from easy_thumbnails.signal_handlers import generate_aliases_global
from easy_thumbnails.signals import saved_file
from rest_framework_simplejwt.tokens import RefreshToken

from src.common.helpers import build_absolute_uri
from src.notifications.services import notify, ACTIVITY_USER_RESETS_PASS


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    reset_password_path = reverse('password_reset:reset-password-confirm')
    context = {
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': build_absolute_uri(f'{reset_password_path}?token={reset_password_token.key}'),
    }

    notify(ACTIVITY_USER_RESETS_PASS, context=context, email_to=[reset_password_token.user.email])


class GetOrNoneManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Country(models.Model):
    name = models.TextField(default='Bosnia and Herzegovina', max_length=255, null=False)


class City(models.Model):
    name = models.TextField(default='Sarajevo', max_length=255, null=False)
    country = models.ForeignKey(Country, related_name='city_country', on_delete=models.DO_NOTHING)
    postal_code = models.IntegerField()


class User(AbstractUser):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
    )
    username = models.CharField(null=True, blank=True, max_length=150)
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True)
    profile_link = models.CharField(max_length=255, blank=True, null=True, default=None)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(null=True, blank=True, max_length=255)
    email = models.TextField(null=False, max_length=255)
    dob = models.DateField(null=True)
    address = models.TextField(max_length=80, null=True, default=None)
    city = models.ForeignKey(City, related_name='user_city', on_delete=models.DO_NOTHING, default=1)
    is_blocked = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    gender = models.PositiveSmallIntegerField(
        choices=GENDER_CHOICES,
        default=GENDER_FEMALE,
    )

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def __str__(self):
        return self.username


class Lab(models.Model):
    city = models.ForeignKey(City, related_name='lab_city', on_delete=models.DO_NOTHING, default='1')
    name = models.TextField(null=False, max_length=255, default=None)
    password = models.CharField(max_length=100)
    address = models.TextField(null=False, max_length=350, default=None)
    phone_number = models.CharField(null=True, max_length=255)
    email = models.TextField(null=False, max_length=255)
    description = models.TextField(null=False, default='Default description')
    website = models.CharField(max_length=255, blank=True, null=True, default='mywebsite.com')
    working_days = models.TextField(null=True, max_length=255, default='All working days')
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True)
    average_rating = models.FloatField(default=0.0)


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


class Service(models.Model):
    name = models.TextField(null=False, max_length=255, default=None)
    duration = models.DurationField(default=30)
    type = models.ForeignKey(Type, related_name='service_type', on_delete=models.DO_NOTHING)


class LabService(models.Model):
    lab_service = models.ForeignKey(Lab, related_name='lab_name_service', on_delete=models.DO_NOTHING)
    service = models.ForeignKey(Service, related_name='service_name', on_delete=models.DO_NOTHING)


class Appointment(models.Model):
    lab_appointment = models.ForeignKey(Lab, related_name='lab_name_appointment', on_delete=models.DO_NOTHING)
    service_appointment = models.ForeignKey(Service, related_name='service_appointment', on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(User, related_name='patient', on_delete=models.DO_NOTHING)
    date = models.DateTimeField(null=True, blank=True)
    fee = models.FloatField(default=0.0)
    doctor = models.CharField(max_length=255, default='My Doctor')

    STATUS_PENDING = 0
    STATUS_CONFIRMED = 1
    STATUS_CANCELED = 2

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending Appointment'),
        (STATUS_CONFIRMED, 'Confirmed Appointment'),
        (STATUS_CANCELED, 'Canceled Appointment'),
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )


class Result(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='appointment_result', on_delete=models.DO_NOTHING)
    pdf = models.FileField(upload_to='pdf', default='src/results/Patient Medical History Report.pdf')


class Notification(models.Model):
    notification_appointment = models.ForeignKey(Appointment, related_name='notification_appointment', on_delete=models.DO_NOTHING)
    message = models.TextField(default='Notification!')
    is_confirmed = models.BooleanField(default=False)
    notification_date = models.DateTimeField(default=datetime.now())


saved_file.connect(generate_aliases_global)

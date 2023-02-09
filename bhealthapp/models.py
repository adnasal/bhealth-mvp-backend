from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class City(models.Model):
    name = models.TextField(default='Sarajevo', max_length=255, null=False)
    country = models.TextField(default='Bosnia and Herzegovina', max_length=255, null=False)  # choices on frontend
    postal_code = models.IntegerField()


class Patient(AbstractUser):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
    )
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    profile_link = models.CharField(max_length=255, blank=True, null=True, default=None)
    name = models.TextField(null=False, max_length=20)
    surname = models.TextField(null=False, max_length=30)
    password = models.CharField(max_length=100)  # add forms.py
    phone_number = models.TextField(null=True, max_length=20)  # check appropriate type
    email = models.TextField(null=False, max_length=80)  # check appropriate type
    dob = models.DateTimeField(null=False)
    address = models.TextField(max_length=80, null=False, default=None)
    city = models.ForeignKey(City, related_name='user_city', on_delete=models.DO_NOTHING)
    joined_at = models.DateTimeField(auto_now_add=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    gender = models.PositiveSmallIntegerField(
        choices=GENDER_CHOICES,
        default=GENDER_FEMALE,
    )

    # Override the save method of the model
    def save(self):
        super().save()

        img = Image.open(self.image.path) # Open image

        # resize image
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size) # Resize image
            img.save(self.image.path) # Save it again and override the larger image


class Lab(models.Model):
    city = models.ForeignKey(City, related_name='lab_city', on_delete=models.DO_NOTHING)
    name = models.TextField(null=False, max_length=255, default=None)
    password = models.CharField(max_length=100)  # add forms.py
    address = models.TextField(null=False, max_length=350, default=None)
    phone_number = models.TextField(null=True, max_length=20)  # check appropriate type
    email = models.TextField(null=False, max_length=80)  # check appropriate type
    website = models.CharField(max_length=255, blank=True, null=True, default=None)
    # rating calculated using function
    # working days and hours?


class UserRating(models.Model):
    user = models.ForeignKey(Patient, related_name='user_rating', on_delete=models.DO_NOTHING)
    lab = models.ForeignKey(Lab, related_name='lab_rating', on_delete=models.DO_NOTHING)

    # connection with frontend rating?
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


# class OpenHours(models.Model):

#   institution = models.ForeignKey(Institution, related_name='institution_open_hours', on_delete=models.DO_NOTHING)
#   day = models.ForeignKey(Day, related_name='day_open_hours', on_delete=models.DO_NOTHING)
#   start_time = models.TimeField(auto_now=False, auto_now_add=True, null=True)
#   end_time = models.TimeField(auto_now=False, auto_now_add=True, null=True)

class Type(models.Model):
    name = models.TextField(null=False, max_length=255, default=None)
    description = models.TextField(null=False, max_length=1000, default='Type Description')


class Service(models.Model):
    name = models.TextField(null=False, max_length=255, default=None)
    duration = models.DurationField(default=30)  # convert microseconds to minutes
    description = models.TextField(null=False, max_length=1000, default='Service Description')
    type = models.ForeignKey(Type, related_name='service_type', on_delete=models.DO_NOTHING)


class Appointment(models.Model):
    city = models.TextField(default='Sarajevo')
    lab = models.ForeignKey(Lab, related_name='lab_name', on_delete=models.DO_NOTHING)
    service = models.ForeignKey(Service, related_name='service_name', on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True, null=True)


class Result(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='appointment_result', on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, related_name='patient_result', on_delete=models.DO_NOTHING)
    # pdf_result
    # parameters (JSON)


class Doctor(models.Model):
    name = models.TextField(null=False, max_length=255, default=None)
    surname = models.TextField(null=False, max_length=255, default=None)
    service = models.ForeignKey(Service, related_name='doctor_service', on_delete=models.DO_NOTHING)
    # profile_picture ?


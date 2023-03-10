from datetime import datetime

import factory
from faker import Faker

from src.users.models import Country, City, User, Lab, UserRating, Type, Service, LabService, Result, Appointment, Notification

fake = Faker()


class CountryFactory(factory.django.DjangoModelFactory):

    def create_country(self):
        country = Country.objects.create(
            name="TestCountry"
        )

        return country


class CityFactory(factory.django.DjangoModelFactory):

    def create_city(self):
        city = City.objects.create(
            name="TestName",
            country=1,
            postal_code=71000
        )

        return city


class UserFactory(factory.django.DjangoModelFactory):

    def create_user(self):
        user = User.objects.create(
            username="TestUsername",
            profile_picture="TestPicture.jpg",
            profile_link="TestLink.com",
            name="TestName",
            surname="TestSurname",
            password="1234556",
            phone_number="003875352",
            email="test@email.com",
            dob=datetime.now(),
            address="TestAddress",
            city=1,
            joined_at=datetime.now(),
            is_blocked=False,
            is_email_verified=True,
            gender=0
        )

        return user


class LabFactory(factory.django.DjangoModelFactory):

    def create_lab(self):
        lab = Lab.objects.create(
            city=1,
            name="TestName",
            password="1243567",
            address="TestAddress",
            phone_number="3450606",
            email="test@email.com",
            website="TestWebsite.com"
        )

        return lab


class UserRatingFactory(factory.django.DjangoModelFactory):

    def create_user_rating(self):
        user_rating = UserRating.objects.create(
            user=3,
            lab=1,
            rating=0,
        )

        return user_rating


class TypeFactory(factory.django.DjangoModelFactory):

    def create_type(self):
        type = Type.objects.create(
            name="TestName",
            description="TestDescription"
        )

        return type


class LabServiceFactory(factory.django.DjangoModelFactory):

    def create_lab_service(self):
        lab_service = LabService.objects.create(
            lab_service=1,
            service=1
        )

        return lab_service


class ServiceFactory(factory.django.DjangoModelFactory):

    def create_service(self):
        service = Service.objects.create(
            name="TestName",
            duration=datetime.timedelta(days=-1, seconds=68400),
            description="TestDescription",
            type=1
        )

        return service


class AppointmentFactory(factory.django.DjangoModelFactory):

    def create_appointment(self):
        appointment = Appointment.objects.create(
            city_appointment="TestCity",
            lab_appointment=1,
            service_appointment=1,
            patient=3,
            date=datetime.now(),
            status=0
        )

        return appointment


class ResultFactory(factory.django.DjangoModelFactory):

    def create_result(self):
        result = Result.objects.create(
            appointment=1,
            patient=3,
            pdf="Test.pdf"
        )

        return result


class NotificationFactory(factory.django.DjangoModelFactory):

    def create_notification(self):
        notification = Notification.objects.create(
            notification_lab=1,
            notification_user=3,
            notification_appointment=1,
            message="Notification!",
            is_confirmed=False,
            is_declined=False,
        )

        return notification

import factory
from django.utils import timezone
from faker import Faker

from src.users.models import Country, City, User, Lab, UserRating, Type, Service, LabService, Result, Appointment

fake = Faker()


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    name = fake.name()


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = fake.name()
    country = CountryFactory()
    postal_code = "20103104adad9##"

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.username()
    profile_picture = 'fake.jpg'
    profile_link = 'http://profilelink.com'
    name = fake.name()
    surname = fake.surname()
    password = fake.password()
    phone_number = "0303030330"
    email = fake.email()
    dob = factory.Faker("date_time", tzinfo=timezone.utc)
    address = fake.text()
    city = CityFactory
    joined_at = factory.Faker("date_time", tzinfo=timezone.utc)
    is_blocked = False
    is_email_verified = False
    gender = 0



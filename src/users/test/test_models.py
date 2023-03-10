import warnings
from datetime import datetime

from django.core.cache import cache
from django.test import TestCase

from src.users.models import Country, City, User, Lab, UserRating, Type, Service, LabService, Result, Appointment, \
    Notification

from src.users.test.factories_meta import ServiceFactory, CityFactory, CountryFactory, LabFactory, LabServiceFactory, \
    ResultFactory, AppointmentFactory, UserFactory, UserRatingFactory, TypeFactory, NotificationFactory


class TestCountry(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.country = CountryFactory

    def test_country_creation(self):
        country_test = self.country
        self.assertTrue(isinstance(country_test, Country))
        """Test Models: Country creation -> Working"""

    def test_country_model_name(self):
        country_db = Country.objects.all()

        print(len(country_db))
        """Test Models: Country name -> Working"""


class TestCity(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.city = CityFactory

    def test_city_creation(self):
        city_test = self.city
        self.assertTrue(isinstance(city_test, City))
        """Test Models: City creation -> Working"""

    def test_city_model_name(self):
        city_db = City.objects.all()

        print(len(city_db))
        """Test Models: City name -> Working"""

    def test_city_model_country(self):
        city_test = self.city
        field_label = city_test._meta.get_field('country').verbose_name
        self.assertEqual(field_label, 'country')
        """Test Models: City country -> Working"""

    def test_city_model_postal_code(self):
        city_test = self.city

        postal_code_length = len(self.city_test.postal_code)
        self.assertGreater(postal_code_length, 0)
        """Test Models: City postal code -> Working"""


class TestUser(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.user = UserFactory()

    def test_user_creation(self):
        user_test = self.test
        self.assertTrue(isinstance(user_test, User))
        """Test Models: User creation -> Working"""

    def test_user_username(self):
        username_length = len(self.user.username)
        self.assertGreater(username_length, 0)
        """Test Models: User username -> Working"""

    def test_user_profile_picture(self):
        profile_picture_length = len(self.user.profile_picture)
        self.assertGreater(profile_picture_length, 0)
        """Test Models: User profile picture -> Working"""

    def test_user_profile_link_label(self):
        user = self.user
        field_label = user._meta.get_field('profile_link').verbose_name
        self.assertEqual(field_label, 'profile link')
        """Test Models: User profile link -> Working"""

    def test_user_name_label(self):
        user = self.user
        field_label = user._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        """Test Models: User name -> Working"""

    def test_user_surname_label(self):
        user = self.user
        field_label = user._meta.get_field('surname').verbose_name
        self.assertEqual(field_label, 'surname')
        """Test Models: User surname -> Working"""

    def test_password_max_length(self):
        user = self.user
        max_length = user._meta.get_field('password').max_length
        self.assertEqual(max_length, 255)
        """Test Models: User password max length -> Working"""

    def test_phone_number_max_length(self):
        user = self.user
        max_length = user._meta.get_field('phone_number').max_length
        self.assertEqual(max_length, 255)
        """Test Models: User phone number max length -> Working"""

    def test_email_label(self):
        field_label = self.user.email
        self.assertContains(field_label, "@")
        """Test Models: User email -> Working"""

    def test_dob_label(self):
        user = self.user
        field_label = user._meta.get_field('dob').verbose_name
        self.assertEqual(field_label, 'dob')
        """Test Models: User dob -> Working"""

    def test_address_label(self):
        user = self.user
        field_label = user._meta.get_field('address').verbose_name
        self.assertEqual(field_label, 'address')
        """Test Models: User address -> Working"""

    def test_city_label(self):
        user = self.user
        field_label = user._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')
        """Test Models: User city -> Working"""

    def test_joined_at_label(self):
        user = self.user
        field_label = user._meta.get_field('joined_at').verbose_name
        self.assertEqual(field_label, 'joined_at')
        """Test Models: User joined at -> Working"""

    def test_default_is_blocked_false(self):
        user = self.user
        field_label = user._meta.get_field('is_blocked').verbose_name
        self.assertFalse(field_label)
        """Test Models: User is blocked -> Working"""

    def test_default_is_email_verified_false(self):
        user = self.user
        field_label = user._meta.get_field('is_email_verified').verbose_name
        self.assertFalse(field_label)
        """Test Models: User is email verified -> Working"""

    def test_gender(self):
        gender = self.user.gender
        self.assertEqual(gender, 0)
        """Test Models: User gender -> Working"""


class TestLab(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.lab = LabFactory

    def test_lab_creation(self):
        lab_test = self.lab
        self.assertTrue(isinstance(lab_test, Lab))
        """Test Models: Lab creation -> Working"""

    def test_lab_city(self):
        city_length = len(self.lab.city)
        self.assertGreater(city_length, 0)
        """Test Models: Lab city -> Working"""

    def test_lab_name(self):
        name_length = len(self.lab.name)
        self.assertGreater(name_length, 0)
        """Test Models: Lab name -> Working"""

    def test_lab_password_max_length(self):
        lab = self.lab
        max_length = lab._meta.get_field('password').max_length
        self.assertEqual(max_length, 100)
        """Test Models: Lab password max length -> Working"""

    def test_lab_address_label(self):
        lab = self.lab
        field_label = lab._meta.get_field('address').verbose_name
        self.assertEqual(field_label, 'address')
        """Test Models: Lab address -> Working"""

    def test_lab_phone_number_max_length(self):
        lab = self.lab
        max_length = lab._meta.get_field('phone_number').max_length
        self.assertEqual(max_length, 255)
        """Test Models: Lab phone number max length -> Working"""

    def test_email_label(self):
        field_label = self.lab.email
        self.assertContains(field_label, "@")
        """Test Models: Lab email -> Working"""

    def test_lab_website(self):
        website_length = len(self.lab.website)
        self.assertGreater(website_length, 0)
        """Test Models: Lab website -> Working"""


class TestUserRating(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.user_rating = UserRatingFactory

    def test_user_rating_creation(self):
        rating_test = self.user_rating
        self.assertTrue(isinstance(rating_test, UserRating))
        """Test Models: User rating creation -> Working"""

    def test_rating_model_user(self):
        rating_test = self.user_rating
        field_label = rating_test._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')
        """Test Models: Rating user -> Working"""

    def test_rating_model_lab(self):
        rating_test = self.user_rating
        field_label = rating_test._meta.get_field('lab').verbose_name
        self.assertEqual(field_label, 'lab')
        """Test Models: Lab user -> Working"""

    def test_default_rating(self):
        rating_test = self.user_rating
        field_label = rating_test._meta.get_field('lab').verbose_name
        self.assertEqual(field_label, 0)

        """Test Models: User default rating -> Working"""


class TestType(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.type = TypeFactory

    def test_type_creation(self):
        type_test = self.type
        self.assertTrue(isinstance(type_test, Type))
        """Test Models: Type creation -> Working"""

    def test_type_model_name(self):
        type_test = self.type
        field_label = type_test._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        """Test Models: Type name -> Working"""

    def test_type_model_description(self):
        type_test = self.type
        field_label = type_test._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')
        """Test Models: Type description -> Working"""


class TestService(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.service = ServiceFactory

    def test_service_creation(self):
        service_test = self.service
        self.assertTrue(isinstance(service_test, Service))
        """Test Models: Service creation -> Working"""

    def test_service_model_name(self):
        service_test = self.service
        field_label = service_test._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        """Test Models: Service name -> Working"""

    def test_default_duration(self):
        service_test = self.service
        field_label = service_test._meta.get_field('duration').verbose_name
        self.assertEqual(field_label, datetime.timedelta(days=-1, seconds=68400))

        """Test Models: Service duration -> Working"""

    def test_service_model_description(self):
        service_test = self.service
        field_label = service_test._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')
        """Test Models: Service description -> Working"""

    def test_service_model_type(self):
        service_test = self.service
        field_label = service_test._meta.get_field('type').verbose_name
        self.assertEqual(field_label, 'type')

        """Test Models: Service type -> Working"""


class TestLabService(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.service = LabServiceFactory

    def test_service_creation(self):
        service_test = self.service
        self.assertTrue(isinstance(service_test, LabService))
        """Test Models: Lab service creation -> Working"""

    def test_service_model_lab(self):
        service_test = self.service
        field_label = service_test._meta.get_field('lab_service').verbose_name
        self.assertEqual(field_label, 'lab service')

        """Test Models: Lab service -> Working"""

    def test_service_model_service(self):
        service_test = self.service
        field_label = service_test._meta.get_field('service').verbose_name
        self.assertEqual(field_label, 'service')

        """Test Models: Lab service -> Working"""


class TestAppointment(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.appointment = AppointmentFactory

    def test_appointment_creation(self):
        appointment_test = self.appointment
        self.assertTrue(isinstance(appointment_test, Appointment))
        """Test Models: Appointment creation -> Working"""

    def test_city_appointment(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('city_appointment').verbose_name
        self.assertEqual(field_label, 'city appointment')

        """Test Models: City of appointment -> Working"""

    def test_lab_appointment(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('lab_appointment').verbose_name
        self.assertEqual(field_label, 'lab appointment')

        """Test Models: Lab of appointment -> Working"""

    def test_lab_appointment(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('service_appointment').verbose_name
        self.assertEqual(field_label, 'service appointment')

        """Test Models: Service of appointment -> Working"""

    def test_patient(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('patient').verbose_name
        self.assertEqual(field_label, 'patient')

        """Test Models: Patient of appointment -> Working"""

    def test_date(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')

        """"Test Models: Date of appointment -> Working"""

    def test_default_status(self):
        appointment_test = self.appointment
        field_label = appointment_test._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 0)

        """Test Models: Appointment default status -> Working"""


class TestResult(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.result = ResultFactory

    def test_result_creation(self):
        result_test = self.result
        self.assertTrue(isinstance(result_test, Result))
        """Test Models: Result creation -> Working"""

    def test_patient(self):
        result_test = self.result
        field_label = result_test._meta.get_field('patient').verbose_name
        self.assertEqual(field_label, 'patient')

        """"Test Models: Result patient -> Working"""

    def test_appointment(self):
        result_test = self.result
        field_label = result_test._meta.get_field('appointment').verbose_name
        self.assertEqual(field_label, 'appointment')

        """"Test Models: Result appointment -> Working"""

    def test_pdf(self):
        field_label = self.result.pdf
        self.assertEqual(field_label, "Result.pdf")


class TestNotification(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.notification = NotificationFactory

    def test_notification_creation(self):
        notification_test = self.notification
        self.assertTrue(isinstance(notification_test, Notification))
        """Test Models: Notification creation -> Working"""

    def test_notification_lab(self):
        notification_test = self.notification
        field_label = notification_test._meta.get_field('notification_lab').verbose_name
        self.assertEqual(field_label, 'notification lab')

        """"Test Models: Notification lab -> Working"""

    def test_notification_user(self):
        notification_test = self.notification
        field_label = notification_test._meta.get_field('notification_user').verbose_name
        self.assertEqual(field_label, 'notification user')

        """"Test Models: Notification user -> Working"""

    def test_notification_appointment(self):
        notification_test = self.notification
        field_label = notification_test._meta.get_field('notification_appointment').verbose_name
        self.assertEqual(field_label, 'notification appointment')

        """"Test Models: Notification appointment -> Working"""

    def test_notification_message(self):
        self.assertGreater(self.notification.message, "Notification!")
        """Test Models: Notification message -> Working"""

    def test_notification_is_confirmed(self):
        self.assertFalse(self.notification.is_confirmed)
        """Test Models: Notification confirmed -> Working"""

    def test_notification_is_confirmed(self):
        self.assertFalse(self.notification.is_declined)
        """Test Models: Notification declined -> Working"""

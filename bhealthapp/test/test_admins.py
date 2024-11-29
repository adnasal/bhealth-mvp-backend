import warnings

from django.contrib.admin.options import (
    ModelAdmin,
)
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from bhealthapp.models import Lab, Country, City, User, UserRating, Type, Appointment, Notification, Result, LabService, \
    Service
from bhealthapp.test.factories_meta import LabFactory, CityFactory, CountryFactory, UserFactory, UserRatingFactory, \
    NotificationFactory, ResultFactory, AppointmentFactory, ServiceFactory, TypeFactory, LabServiceFactory


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


request = MockRequest()
request.user = MockSuperUser()


class ModelAdminLabTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.lab = LabFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(Lab, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Lab, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Lab, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.lab)),
            ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Lab, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.lab),
            [
                (None, {
                    'fields': ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website']
                }),
            ]

        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminCountryTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.country = CountryFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(Country, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Country, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Country, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.country)),
            ['name']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Country, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['name']
                }),
            ]
        )
        self.assertEqual(
            ma.get_fieldsets(request, self.country),
            [
                (None, {
                    'fields': ['name']
                }),
            ]
        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminCityTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.country = CountryFactory()
        self.city = CityFactory(country=self.country)

    def test_modeladmin_str(self):
        ma = ModelAdmin(City, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(City, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(City, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.city)),
            ['name', 'country', 'postal_code']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(City, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['name', 'country', 'postal_code']
                }),
            ]
        )
        self.assertEqual(
            ma.get_fieldsets(request, self.city),
            [
                (None, {
                    'fields': ['name', 'country', 'postal_code']
                }),
            ]
        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminUserTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.user = UserFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(User, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")

    def test_default_attributes(self):
        ma = ModelAdmin(User, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])

    def test_default_fields(self):
        ma = ModelAdmin(User, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.user)),
            ['username', 'first_name', 'last_name', 'password', 'email', 'phone_number', 'profile_picture',
             'profile_link', 'dob', 'address', 'city', 'is_blocked', 'is_email_verified', 'gender']
        )

    def test_default_fieldsets(self):
        ma = ModelAdmin(User, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['username', 'password', 'email', 'phone_number', 'dob', 'address', 'city',
                               'is_blocked', 'is_email_verified', 'gender']
                }),
                ('Personal Info', {
                    'fields': ['first_name', 'last_name', 'profile_picture', 'profile_link']
                }),
            ]
        )
        self.assertEqual(
            ma.get_fieldsets(request, self.user),
            [
                (None, {
                    'fields': ['username', 'password', 'email', 'phone_number', 'dob', 'address', 'city',
                               'is_blocked', 'is_email_verified', 'gender']
                }),
                ('Personal Info', {
                    'fields': ['first_name', 'last_name', 'profile_picture', 'profile_link']
                }),
            ]
        )


class ModelAdminUserRatingTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.user_rating = UserRatingFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(UserRating, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")

    def test_default_attributes(self):
        ma = ModelAdmin(UserRating, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])

    def test_default_fields(self):
        ma = ModelAdmin(UserRating, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.user_rating)),
            ['user', 'lab', 'rating']
        )

    def test_default_fieldsets(self):
        ma = ModelAdmin(UserRating, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['user', 'lab', 'rating']
                }),
            ]
        )
        self.assertEqual(
            ma.get_fieldsets(request, self.user_rating),
            [
                (None, {
                    'fields': ['user', 'lab', 'rating']
                }),
            ]
        )


class ModelAdminTypeTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.type = TypeFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(Type, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Type, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Type, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.type)),
            ['name', 'description']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Type, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['name', 'description']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.type),
            [
                (None, {
                    'fields': ['name', 'description']
                }),
            ]

        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminServiceTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.service = ServiceFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(Service, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Service, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Service, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.service)),
            ['name', 'duration', 'type']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Service, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['name', 'duration', 'type']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.service),
            [
                (None, {
                    'fields': ['name', 'duration', 'type']
                }),
            ]

        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminLabServiceTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.lab_service = LabServiceFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(LabService, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")

    def test_default_attributes(self):
        ma = ModelAdmin(LabService, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])

    def test_default_fields(self):
        ma = ModelAdmin(LabService, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.lab_service)),
            ['lab_service', 'service']
        )

    def test_default_fieldsets(self):
        ma = ModelAdmin(LabService, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['lab_service', 'service']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.lab_service),
            [
                (None, {
                    'fields': ['lab_service', 'service']
                }),
            ]
        )


class ModelAdminAppointmentTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.appointment = AppointmentFactory()

    def test_modeladmin_str(self):
        ma = ModelAdmin(Appointment, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")

    def test_default_attributes(self):
        ma = ModelAdmin(Appointment, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])

    def test_default_fields(self):
        ma = ModelAdmin(Appointment, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.appointment)),
            ['lab_appointment', 'service_appointment', 'patient', 'date', 'status']
        )

    def test_default_fieldsets(self):
        ma = ModelAdmin(Appointment, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['lab_appointment', 'service_appointment', 'patient', 'date', 'status']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.appointment),
            [
                (None, {
                    'fields': ['lab_appointment', 'service_appointment', 'patient', 'date', 'status']
                }),
            ]
        )


class ModelAdminResultTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.appointment = AppointmentFactory()
        self.result = ResultFactory(appointment=self.appointment)

    def test_modeladmin_str(self):
        ma = ModelAdmin(Result, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Result, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Result, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.result)),
            ['appointment', 'pdf']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Result, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['appointment', 'pdf']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.result),
            [
                (None, {
                    'fields': ['appointment', 'pdf']
                }),
            ]

        )
        """Test Admins: Default fieldsets -> Working"""


class ModelAdminNotificationTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        warnings.simplefilter('ignore', category=ImportWarning)
        self.appointment = AppointmentFactory()
        self.notification = NotificationFactory(notification_appointment=self.appointment)

    def test_modeladmin_str(self):
        ma = ModelAdmin(Notification, self.site)
        self.assertEqual(str(ma), "bhealth.ModelAdmin")
        """Test Admins: Admin model -> Working"""

    def test_default_attributes(self):
        ma = ModelAdmin(Notification, self.site)
        self.assertEqual(ma.actions, [])
        self.assertEqual(ma.inlines, [])
        """Test Admins: Default attributes -> Working"""

    def test_default_fields(self):
        ma = ModelAdmin(Notification, self.site)

        self.assertEqual(
            list(ma.get_fields(request, self.notification)),
            ['notification_appointment', 'message', 'is_confirmed']
        )
        """Test Admins: Default fields -> Working"""

    def test_default_fieldsets(self):
        ma = ModelAdmin(Notification, self.site)
        self.assertEqual(
            ma.get_fieldsets(request),
            [
                (None, {
                    'fields': ['notification_appointment', 'message', 'is_confirmed']
                }),
            ]
        ),
        self.assertEqual(
            ma.get_fieldsets(request, self.notification),
            [
                (None, {
                    'fields': ['notification_appointment', 'message', 'is_confirmed']
                }),
            ]

        )
        """Test Admins: Default fieldsets -> Working"""

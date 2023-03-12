import warnings

from django.contrib.admin.options import (
    ModelAdmin,
)
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from bhealthapp.models import Lab
from bhealthapp.test.factories_meta import LabFactory


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

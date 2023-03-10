from django.apps import apps
from django.test import TestCase

from src.users.apps import UsersConfig, BhealthCaching


class BHealthAppsTest(TestCase):

    def test_bhealth_config(self):
        self.assertEqual(UsersConfig.name, 'src.users')
        self.assertEqual(apps.get_app_config('src.users').name, 'src.users')

    def test_bhealth_caching(self):
        self.assertEqual(BhealthCaching.name, 'bhealth_cache')

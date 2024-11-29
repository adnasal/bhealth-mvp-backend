from django.apps import apps
from django.test import TestCase

from bhealthapp.apps import BHealthConfig, BHealthCaching


class BHealthAppsTest(TestCase):

    def test_bhealth_config(self):
        self.assertEqual(BHealthConfig.name, 'bhealthapp')
        self.assertEqual(apps.get_app_config('bhealthapp').name, 'bhealthapp')

    def test_bhealth_caching(self):
        self.assertEqual(BHealthCaching.name, 'bhealth_cache')

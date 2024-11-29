from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bhealthapp.models import Lab, User, Appointment
from bhealthapp.models import Service
from bhealthapp.serializers import LabViewSerializer


class UserCreateTest(TestCase):
    """Test module for User creation"""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass',
        }
        self.invalid_payload = {
            'username': '',
            'email': 'testuser@example.com',
            'password': 'testpass',
        }

    def test_create_valid_user(self):
        response = self.client.post(
            reverse('account_create'),
            data=self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        response = self.client.post(
            reverse('account_create'),
            data=self.invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LabCreateTest(TestCase):
    """Test module for Lab creation"""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'name': 'Test Lab',
            'email': 'testlab@example.com',
            'password': 'testpass',
            'phone': '123-456-7890',
            'location': 'Test Location',
        }
        self.invalid_payload = {
            'name': '',
            'email': 'testlab@example.com',
            'password': 'testpass',
            'phone': '123-456-7890',
            'location': 'Test Location',
        }

    def test_create_valid_lab(self):
        response = self.client.post(
            reverse('lab_account_create'),
            data=self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_lab(self):
        response = self.client.post(
            reverse('lab_account_create'),
            data=self.invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(TestCase):
    """Test module for User Login"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.valid_credentials = {
            'username': 'testuser',
            'password': 'testpass',
        }
        self.invalid_credentials = {
            'username': 'testuser',
            'password': 'wrongpass',
        }

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse('login'),
            data=self.valid_credentials,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse('login'),
            data=self.invalid_credentials,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LabListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('labs')
        self.labs = [
            Lab.objects.create(name='Lab A', city='City A', address='Address A'),
            Lab.objects.create(name='Lab B', city='City B', address='Address B'),
            Lab.objects.create(name='Lab C', city='City C', address='Address C'),
        ]
        self.services = [
            Service.objects.create(name='Service A'),
            Service.objects.create(name='Service B'),
        ]
        self.labs[0].services.set([self.services[0]])
        self.labs[1].services.set([self.services[0], self.services[1]])

    def test_lab_list_view(self):
        response = self.client.get(self.url)
        serializer = LabViewSerializer(self.labs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_lab_list_view_with_search_param(self):
        response = self.client.get(self.url, {'search': 'Service B'})
        serializer = LabViewSerializer([self.labs[1]], many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_lab_list_view_with_city_param(self):
        response = self.client.get(self.url, {'city': 'City B'})
        serializer = LabViewSerializer([self.labs[1]], many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_lab_list_view_with_name_param(self):
        response = self.client.get(self.url, {'name': 'Lab C'})
        serializer = LabViewSerializer([self.labs[2]], many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_lab_list_view_with_address_param(self):
        response = self.client.get(self.url, {'address': 'Address A'})
        serializer = LabViewSerializer([self.labs[0]], many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)


class AppointmentUpdateViewTests(TestCase):
    def test_update_appointment_status_with_valid_data(self):
        appointment = Appointment.objects.create(status=0, date=None)
        url = reverse('appointment-update')
        data = {
            'status': 1,
        }
        response = self.client.put(f"{url}?pk={appointment.pk}", data=data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Appointment.objects.get(pk=appointment.pk).status, 1)

    def test_update_appointment_status_with_invalid_data(self):
        appointment = Appointment.objects.create(status=0, date='2023-03-17')
        url = reverse('appointment-update')
        data = {
            'status': 1,
        }
        response = self.client.put(f"{url}?pk={appointment.pk}", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.get(pk=appointment.pk).status, 0)

    def test_update_appointment_with_invalid_pk(self):
        url = reverse('appointment-update')
        data = {
            'status': 1,
        }
        response = self.client.put(f"{url}?pk=1234", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_notification_with_invalid_pk(self):
        url = reverse('notification-confirm')
        data = {}
        response = self.client.put(f"{url}?pk=1234", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from urllib.parse import urlencode

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from bhealthapp.models import Notification, Lab, Result, Appointment, User, UserRating
from bhealthapp.serializers import ResultViewSerializer, AppointmentViewSerializer
from bhealthapp.test.factories import LabFactory, LabServiceFactory, UserFactory, AppointmentFactory


class NotificationListViewPaginationTestCase(APITestCase):
    def setUp(self):
        for i in range(10):
            Notification.objects.create(notification_appointment=f'Appointment {i}')

    def test_pagination_first_page(self):
        url = reverse('notifications')
        response = self.client.get(url, {'page': 1, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['notification_appointment'], 'Appointment 9')

    def test_pagination_second_page(self):
        url = reverse('notifications')
        response = self.client.get(url, {'page': 2, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['notification_appointment'], 'Appointment 4')


class LabListViewTest(APITestCase):
    def setUp(self):

        self.lab1 = LabFactory
        self.lab2 = LabFactory
        self.lab3 = LabFactory

    def test_pagination(self):
        url = reverse('labs')
        response = self.client.get(url, {'page': 2, 'page_size': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['next'], None)
        self.assertIsNotNone(response.data['previous'])


class LabServiceListViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('lab_services')

        self.lab_service_1 = LabServiceFactory
        self.lab_service_2 = LabServiceFactory
        self.lab_service_3 = LabServiceFactory

    def test_lab_service_list_view_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

        # Test page 1
        response = self.client.get(self.url + '?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['results'][0]['lab'], self.lab_service_3.lab)

        # Test page 2
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class ResultListViewTest(APITestCase):
    def setUp(self):
        self.patient = User.objects.create(name="John Doe")
        self.appointment = Appointment.objects.create(
            patient=self.patient, date="2023-03-16")
        self.result = Result.objects.create(
            appointment=self.appointment, report="Some report")

    def test_list_results_by_patient(self):
        url = reverse('results')
        query_params = f"?patient={self.patient.id}"
        response = self.client.get(f"{url}{query_params}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = ResultViewSerializer(
            [self.result], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_list_results_by_appointment(self):
        url = reverse('results')
        query_params = f"?appointment={self.appointment.id}"
        response = self.client.get(f"{url}{query_params}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = ResultViewSerializer(
            [self.result], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_list_results_with_invalid_params(self):
        url = reverse('results')
        query_params = "?invalid=param"
        response = self.client.get(f"{url}{query_params}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpcomingAppointmentsUserViewTestCase(APITestCase):
    url = reverse('user_upcoming_appointments')

    def setUp(self):
        self.user = UserFactory
        self.appointment = AppointmentFactory
        self.lab = LabFactory

    def test_upcoming_appointments_user_view(self):
        self.client.force_authenticate(user=self.patient)

        # Test with valid patient id
        response = self.client.get(self.url, {'patient': self.patient.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PastAppointmentsUserViewTestCase(APITestCase):
    url = reverse('user_past_appointments')

    def setUp(self):
        self.patient_id = 1
        self.appointment1 = AppointmentFactory
        self.appointment2 = AppointmentFactory
        self.appointment3 = AppointmentFactory

    def test_get_past_appointments_user(self):
        data = {'patient': self.patient_id}
        response = self.client.get(self.url, data)
        appointments = Appointment.objects.filter(
            patient_id=self.patient_id,
            datetime__lte='2022-03-16'
        ).order_by('-datetime')
        serializer = AppointmentViewSerializer(appointments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class RequestsViewPaginationTestCase(APITestCase):
    def setUp(self):

        self.lab_1 = LabFactory
        self.lab_2 = LabFactory
        self.user_1 = UserFactory
        self.user_2 = UserFactory
        self.appointment_1 = AppointmentFactory
        self.appointment_2 = AppointmentFactory
        self.appointment_3 = AppointmentFactory

    def test_pagination(self):

        url = reverse('requests')
        query_params = {
            'lab_appointment': self.lab_1.id,
            'ordering': '-datetime',
            'page': 2,
            'page_size': 1,
        }
        url += '?' + urlencode(query_params)
        response = self.client.get(url)

        # check that the response is valid JSON and has the expected keys
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, dict))
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # check that the count and number of results match what we expect
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 1)

        # check that the results are sorted correctly
        self.assertEqual(response.data['results'][0]['id'], self.appointment_1.id)

        # check that the pagination links are correct
        base_url = reverse('requests') + '?' + urlencode({
            'lab_appointment': self.lab_1.id,
            'ordering': '-datetime',
            'page_size': 1,
        })
        expected_next_url = base_url + '&page=3'
        expected_previous_url = base_url + '&page=1'
        self.assertEqual(response.data['next'], expected_next_url)
        self.assertEqual(response.data['previous'], expected_previous_url)


class PatientsViewPaginationTestCase(APITestCase):
    def setUp(self):
        self.lab1 = LabFactory
        self.lab2 = LabFactory

        self.patient1 = User.objects.create(username='patient1', lab=self.lab1)
        self.patient2 = User.objects.create(username='patient2', lab=self.lab1)
        self.patient3 = User.objects.create(username='patient3', lab=self.lab2)
        self.patient4 = User.objects.create(username='patient4', lab=self.lab2)

        self.url = reverse('patients')

    def test_pagination(self):
        response = self.client.get(self.url, {'lab': self.lab1.pk, 'page': 1, 'page_size': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['id'], self.patient2.pk)
        self.assertEqual(response.data['results'][1]['id'], self.patient1.pk)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['next'], f'http://testserver{self.url}?lab={self.lab1.pk}&page=2&page_size=2')
        self.assertIsNone(response.data['previous'])


class TestWeRecommendViewPagination(APITestCase):
    def setUp(self):
        # Create 10 labs with 5 ratings each
        for i in range(10):
            lab = Lab.objects.create(name=f"Lab {i}")
            for j in range(5):
                UserRating.objects.create(user=User.objects.create(username=f"user{j}"), lab=lab, rating=5)

    def test_pagination(self):
        response = self.client.get(reverse('top_labs'), {'page': 2, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the number of items returned in the response
        self.assertEqual(len(response.data['results']), 1)

        # Check if the response contains the correct data
        self.assertEqual(response.data['results'][0][0], 'Lab 8')
        self.assertEqual(response.data['results'][0][1], 5)

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from bhealthapp.models import City, Lab
from bhealthapp.serializers import CitySerializer, CityViewSerializer, PatientSerializer, PatientLoginSerializer, \
    PatientViewSerializer, LabServiceSerializer, LabViewSerializer, LabSerializer
from .factories import CityFactory, UserFactory


class TestCitySerializer(TestCase):
    city = CityFactory()

    def test_serializer_with_valid_data(self):
        serializer = CitySerializer(instance=self.city)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], self.city.name)

    def test_serializer_with_empty_data(self):
        serializer = CitySerializer(data={})
        self.assertFalse(serializer.is_valid())


class TestCityViewSerializer(TestCase):
    city = CityFactory()

    def test_serializer_with_valid_data(self):
        serializer = CityViewSerializer(instance=self.city)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], self.city.name)

    def test_serializer_with_empty_data(self):
        serializer = CityViewSerializer(data={})
        self.assertFalse(serializer.is_valid())


class TestPatientLoginSerializer(TestCase):
    user = UserFactory()

    def test_serializer_with_valid_data(self):
        serializer = PatientLoginSerializer(data={"email": self.user.email, "password": "testpassword"})
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_invalid_email(self):
        with self.assertRaises(ValidationError):
            serializer = PatientLoginSerializer(data={"email": "invalidemail", "password": "testpassword"})
            serializer.is_valid(raise_exception=True)

    def test_serializer_with_invalid_password(self):
        with self.assertRaises(ValidationError):
            serializer = PatientLoginSerializer(data={"email": self.user.email, "password": "invalid"})
            serializer.is_valid(raise_exception=True)


class TestPatientSerializer(TestCase):
    def test_serializer_with_valid_data(self):
        data = {
            "email": "test@test.com",
            "username": "testuser",
            "password": "testpassword",
            "dob": "2000-01-01",
            "gender": "M",
        }
        serializer = PatientSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_existing_email(self):
        user = UserFactory()
        data = {
            "email": user.email,
            "username": "testuser",
            "password": "testpassword",
            "dob": "2000-01-01",
            "gender": "M",
        }
        serializer = PatientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_serializer_with_existing_username(self):
        user = UserFactory()
        data = {
            "email": "test@test.com",
            "username": user.username,
            "password": "testpassword",
            "dob": "2000-01-01",
            "gender": "M",
        }
        serializer = PatientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)


class TestPatientViewSerializer(TestCase):
    user = UserFactory()

    def test_serializer_with_valid_data(self):
        serializer = PatientViewSerializer(instance=self.user)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], self.user.email)

    def test_serializer_with_invalid_gender(self):
        with self.assertRaises(ValidationError):
            serializer = PatientViewSerializer(data={"gender": "invalidgender"})
            serializer.is_valid(raise_exception=True)


class LabSerializerTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name="Test City", country="Test Country", postal_code="12345")
        self.lab_data = {
            "name": "Test Lab",
            "password": "testpassword",
            "address": "123 Test St",
            "phone_number": "+1234567890",
            "email": "testlab@test.com",
            "website": "testlab.com",
            "city": self.city.pk
        }

    def test_valid_serializer(self):
        serializer = LabSerializer(data=self.lab_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer(self):
        # missing city field
        del self.lab_data["city"]
        serializer = LabSerializer(data=self.lab_data)
        self.assertFalse(serializer.is_valid())


class LabViewSerializerTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name="Test City", country="Test Country", postal_code="12345")
        self.lab = Lab.objects.create(
            name="Test Lab",
            password="testpassword",
            address="123 Test St",
            phone_number="+1234567890",
            email="testlab@test.com",
            website="testlab.com",
            city=self.city,
        )

    def test_serializer(self):
        serializer = LabViewSerializer(self.lab)
        expected_fields = [
            "city",
            "name",
            "password",
            "address",
            "phone_number",
            "email",
            "website",
            "services",
        ]
        self.assertEqual(set(serializer.data.keys()), set(expected_fields))


class LabServiceSerializerTest(TestCase):
    def setUp(self):
        self.lab_service_data = {
            "lab_service": 1,
            "service": 1,
        }

    def test_valid_serializer(self):
        serializer = LabServiceSerializer(data=self.lab_service_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer(self):
        # missing lab_service field
        del self.lab_service_data["lab_service"]
        serializer = LabServiceSerializer(data=self.lab_service_data)
        self.assertFalse(serializer.is_valid())


class TestCitySerializer(TestCase):
    def test_city_serializer(self):
        city = CityFactory()
        serializer = CitySerializer(city)
        data = serializer.data
        self.assertEqual(data['name'], city.name)
        self.assertEqual(data['country'], city.country)
        self.assertEqual(data['postal_code'], city.postal_code)

    def test_city_serializer_with_empty_data(self):
        serializer = CitySerializer(data={})
        self.assertFalse(serializer.is_valid())


class TestCityViewSerializer(TestCase):
    def test_city_view_serializer(self):
        city = CityFactory()
        serializer = CityViewSerializer(city)
        data = serializer.data
        self.assertEqual(data['name'], city.name)
        self.assertEqual(data['country'], city.country)
        self.assertEqual(data['postal_code'], city.postal_code)

    def test_city_view_serializer_with_empty_data(self):
        serializer = CityViewSerializer(data={})
        self.assertFalse(serializer.is_valid())


class TestPatientLoginSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_patient_login_serializer(self):
        data = {
            'email': self.user.email,
            'password': 'test_password'
        }
        serializer = PatientLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_patient_login_serializer_with_invalid_data(self):
        data = {
            'email': 'invalid_email',
            'password': 'short'
        }
        serializer = PatientLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class TestPatientSerializer(TestCase):
    def test_patient_serializer(self):
        city = CityFactory()
        data = {
            'email': 'test_email@test.com',
            'username': 'test_user',
            'password': 'test_password',
            'phone_number': '1234567890',
            'dob': '2000-01-01',
            'address': 'test address',
            'city': city.id,
            'gender': '1'
        }
        serializer = PatientSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_patient_serializer_with_invalid_data(self):
        data = {
            'email': 'invalid_email',
            'username': 'test_user',
            'password': 'short',
            'phone_number': '1234567890',
            'dob': '2000-01-01',
            'address': 'test address',
            'city': 'invalid_city',
            'gender': 'invalid_gender'
        }
        serializer = PatientSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class TestPatientViewSerializer(TestCase):
    def test_patient_view_serializer(self):
        patient = UserFactory()
        serializer = PatientViewSerializer(patient)
        data = serializer.data
        self.assertEqual(data['email'], patient.email)
        self.assertEqual(data['username'], patient.username)
        self.assertEqual(data['phone_number'], patient.phone_number)
        self.assertEqual(data['dob'], str(patient.dob))
        self.assertEqual(data['address'], patient.address)
        self.assertEqual(data['city']['id'], patient.city.id)
        self.assertEqual(data['city']['name'], patient.city.name)
        self.assertEqual(data['gender'], patient.gender)

    def test_patient_view_serializer_with_empty_data(self):
        serializer = PatientViewSerializer(data={})
        self.assertFalse(serializer.is_valid())

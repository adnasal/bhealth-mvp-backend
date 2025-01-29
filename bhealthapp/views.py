import os
from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode
from rest_framework import pagination
from rest_framework import status, filters, serializers, fields
from rest_framework.authtoken.models import Token
from rest_framework.generics import (CreateAPIView, GenericAPIView, DestroyAPIView, ListAPIView, get_object_or_404,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from bhealthapp.models import Institution, InstitutionService, MedicalRecord, Appointment, User, Notification, Party, \
    InstitutionWorkingHours, Drug, Diagnosis, Treatment, Role, City, Country
from src.config import common
from .serializers import InstitutionSerializer, InstitutionUserViewSerializer, UserSettingsViewSerializer, PartyViewSerializer, InstitutionPartyViewSerializer, InstitutionServiceViewSerializer, MedicalRecordViewSerializer, MedicalRecordTemplateViewSerializer, \
    PatientSerializer, PatientViewSerializer, InstitutionViewSerializer, AppointmentViewSerializer, \
    MedicalRecordSerializer, AppointmentSerializer, NotificationViewSerializer, NotificationSerializer, \
    RequestViewSerializer, PatientLoginSerializer, InstitutionLoginSerializer, PasswordResetRequestSerializer, \
    PasswordResetSerializer, InstitutionWorkingHoursSerializer, DrugSerializer, UserRoleViewSerializer, DiagnosisSerializer, SaveMedicalRecordTemplateSerializer, \
    TreatmentSerializer, RoleSerializer, CityViewSerializer, CountryViewSerializer, InstitutionLoginSerializer, ServiceViewSerializer, SaveServiceSerializer, InstitutionServiceViewSerializer, SaveInstitutionServiceSerializer
from .tasks import send_appointment_canceled_message, send_appointment_message, download_file, request_updated, \
    upload_pdf, send_request_notification

today = datetime.now()


class CustomPagination(pagination.PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 12


class ValidateQueryParams(serializers.Serializer):
    search = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 a-zA-Z0-9]{3,30}$", required=False)

    city = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False)
    institution = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False)
    service = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False)
    patient = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 a-zA-Z0-9]{3,30}$", required=False)
    pk = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 0-9]{3,30}$", required=False)
    day = fields.IntegerField(min_value=1, max_value=30, required=False)
    year = fields.IntegerField(min_value=1990, max_value=today.year, required=False)


class UserCreate(GenericAPIView):
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():

            password = serializer.validated_data['password']
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password

            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                # resize_profile_picture.delay(user.pk)
                return Response({'Success': 'New user has been successfully added.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientLoginSerializer

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response({'Error': 'Please provide both email and password.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                user_id = user.pk
            except User.DoesNotExist:
                return Response({'Error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            # if user.is_blocked:
            # return Response({'Error': 'Your account has been blocked.'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'User Id': user_id})

        except Exception as e:
            return Response({'Error': 'An error occurred during login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstitutionLogin(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionLoginSerializer

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response({'Error': 'Please provide both email and password.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                institution = Institution.objects.get(emails=email)
                institution_id = institution.pk
            except Institution.DoesNotExist:
                return Response({'Error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(institution)

            return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'User Id': institution_id})

        except Exception as e:
            return Response({'Error': 'An error occurred during login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadMedicalRecord(GenericAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            medical_record = MedicalRecord.objects.get(pk=param)
        except MedicalRecord.DoesNotExist:
            return Response({'Failure': 'MedicalRecord does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(common.MEDIA_ROOT, medical_record.pdf.name)
        if os.path.exists(file_path):

            download_file.delay(file_path, medical_record.pdf.name)
            return Response({'File download has started asynchronously.'}, status=status.HTTP_201_CREATED)
        else:
            return Response("Cannot download the file.", status=status.HTTP_404_NOT_FOUND)


class InstitutionCreate(GenericAPIView):
    serializer_class = InstitutionSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InstitutionSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password

            institution = serializer.save()
            return Response({'Success': 'New institution has been successfully added.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def create(self, request, **kwargs):
        try:
            institution_service_id = request.data.get('institution_service_id')
            patient_id = request.data.get('patient_id')
            doctor_id = request.data.get('doctor_id')
            datetime = request.data.get('datetime')

            institution_service = InstitutionService.objects.get(pk=institution_service_id)
            patient = User.objects.get(pk=patient_id)
            doctor = Party.objects.get(pk=doctor_id)

            appointment = Appointment.objects.create(institution_service_id=institution_service, patient_id=patient,
                doctor_id=doctor, datetime=datetime, status=Appointment.STATUS_PENDING, )

            send_request_notification(appointment_id=appointment.id)

            return Response({'message': 'Appointment added successfully.'}, status=status.HTTP_201_CREATED)

        except (InstitutionService.DoesNotExist, User.DoesNotExist, Party.DoesNotExist):
            return Response({'error': 'One or more related objects do not exist.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            User.objects.get(pk=param)
        except User.DoesNotExist:
            return Response({'Failure': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(instance=get_object_or_404(User, pk=param), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)


class NotificationListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NotificationViewSerializer
    ordering = ['-notification_id']
    pagination_class = CustomPagination
    search_fields = ['notification_appointment']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        queryset = Notification.objects.all().order_by('notification_id')

        if param.get('notification_appointment') is not None:
            queryset = queryset.filter(notification_appointment=param.get('notification_appointment'))

        elif param.get('patient') is not None:
            patient_id = int(param.get('patient'))
            queryset = queryset.filter(notification_appointment__patient=patient_id)

        elif param.get('institution') is not None:
            institution_id = int(param.get('institution'))
            queryset = queryset.filter(notification_appointment__institution_appointment=institution_id)

        return queryset


class InstitutionUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            Institution.objects.get(pk=param)
        except Institution.DoesNotExist:
            return Response({'Failure': 'Institution does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InstitutionSerializer(instance=get_object_or_404(Institution, pk=param), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.validated_data, content_type="application/json",
                        status=status.HTTP_202_ACCEPTED)

class SaveMedicalRecordTemplateView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SaveMedicalRecordTemplateSerializer(data=request.data)
        if serializer.is_valid():
            medical_record_template_id = serializer.validated_data.get('medical_record_template_id')
            institution_id = serializer.validated_data.get('institution_id')
            template = serializer.validated_data.get('template')
            is_active = serializer.validated_data.get('is_active')

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT save_medical_record_template(%s, %s, %s, %s)",
                    [medical_record_template_id, institution_id, template, is_active]
                )
                new_id = cursor.fetchone()[0]

            return Response({"medical_record_template_id": new_id}, status=200)

        return Response(serializer.errors, status=400)

class InstitutionUserListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionUserViewSerializer
    pagination_class = CustomPagination
    search_fields = ['email', 'username', 'status']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['registration_date']

    def get(self, request, *args, **kwargs):
        institution_id = self.request.query_params.get('institution_id')
        role_id = self.request.query_params.get('role_id', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_institution_users(%s, %s)",
                [institution_id, role_id]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class InstitutionListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionViewSerializer
    pagination_class = CustomPagination
    search_fields = ['institution_name', 'city_id', 'status']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['institution_name']

    def get(self, request, *args, **kwargs):
        institution_id = self.request.query_params.get('institution_id', None)
        institution_name = self.request.query_params.get('institution_name', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_institutions(%s, %s)",
                [institution_id, institution_name]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class InstitutionView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            institution = Institution.objects.get(pk=param)
        except Institution.DoesNotExist:
            return Response({'Failure': 'Institution does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InstitutionViewSerializer(institution)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")


class SaveServiceView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SaveServiceSerializer(data=request.data)
        if serializer.is_valid():
            service_id = serializer.validated_data.get('service_id')
            service_name = serializer.validated_data.get('service_name')
            service_category = serializer.validated_data.get('service_category')
            description = serializer.validated_data.get('description')

            with connection.cursor() as cursor:
                cursor.execute("SELECT save_service(%s, %s, %s, %s)", [service_id, service_name, service_category, description])
                new_service_id = cursor.fetchone()[0]

            return Response({"service_id": new_service_id}, status=200)

        return Response(serializer.errors, status=400)


class ServiceListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceViewSerializer
    pagination_class = CustomPagination
    search_fields = ['service_name', 'service_category']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['service_name']

    def get_queryset(self):
        service_id = self.request.query_params.get('service_id', None)
        service_name = self.request.query_params.get('service_name', None)
        service_category = self.request.query_params.get('service_category', None)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_services(%s, %s, %s)", [service_id, service_name, service_category])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return results


class InstitutionServiceView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionServiceViewSerializer
    pagination_class = CustomPagination
    search_fields = ['service_name', 'service_category']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['service_name', 'price']

    def get_queryset(self):
        institution_service_id = self.request.query_params.get('institution_service_id', None)
        institution_id = self.request.query_params.get('institution_id', None)
        is_active = self.request.query_params.get('is_active', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_institution_services(%s, %s, %s)",
                [institution_service_id, institution_id, is_active]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return results

class InstitutionAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionSerializer

    def create(self, request, **kwargs):
        param = self.request.query_params.get('pk', default=None)
        institution = Institution.objects.get(pk=param)

        if institution.exists():
            return Response({'Failure': 'Institution already exists.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = InstitutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class InstitutionRemoveView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Institution.objects.all()

    def delete(self, request, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            institution = Institution.objects.get(pk=param)
        except Institution.DoesNotExist:
            return Response({'Failure': 'Article does not exist or has been already removed.'},
                            status=status.HTTP_404_NOT_FOUND)
        response = institution
        response.delete()
        return Response({"You have successfully deleted desired institution."}, status=status.HTTP_200_OK)


class MedicalRecordListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = MedicalRecordViewSerializer
    pagination_class = CustomPagination
    search_fields = ['file', 'notes']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['appointment_id']

    def get(self, request, *args, **kwargs):
        appointment_id = self.request.query_params.get('appointment_id', None)
        user_id = self.request.query_params.get('user_id', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_medical_records(%s, %s)",
                [appointment_id, user_id]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class MedicalRecordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = MedicalRecordViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            medical_record = MedicalRecord.objects.get(pk=param)
        except MedicalRecord.DoesNotExist:
            return Response({'Failure': 'MedicalRecord does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicalRecordViewSerializer(medical_record)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")


class AppointmentView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            appointment = Appointment.objects.get(pk=param)
        except Appointment.DoesNotExist:
            return Response({'Failure': 'Appointment does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentViewSerializer(appointment)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")



class AppointmentsListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    pagination_class = CustomPagination
    search_fields = ['patient_first_name', 'patient_last_name', 'doctor_first_name', 'doctor_last_name']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['date_time']

    def get(self, request, *args, **kwargs):
        appointment_id = self.request.query_params.get('appointment_id', None)
        patient_user_id = self.request.query_params.get('patient_user_id', None)
        doctor_user_id = self.request.query_params.get('doctor_user_id', None)
        patient_id = self.request.query_params.get('patient_id', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_appointments(%s, %s, %s, %s)",
                [appointment_id, patient_user_id, doctor_user_id, patient_id]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class InstitutionPartiesListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionPartyViewSerializer
    pagination_class = CustomPagination
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['last_name']

    def get(self, request, *args, **kwargs):
        institution_id = self.request.query_params.get('institution_id', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_institution_parties(%s)",
                [institution_id]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class UpcomingAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-appointment_id']
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params.get('patient', default=None)

        if param is not None:

            patient = User.objects.get(pk=param)
            date_from = today
            date_to = today + relativedelta(years=5)
            query_set = Appointment.objects.filter(patient_id=patient, datetime__gte=date_from, datetime__lte=date_to,
                                                   status=1)

        else:
            query_set = Appointment.objects.none()

        return query_set


class PastAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-appointment_id']
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        patient_id = self.request.query_params.get('patient', default=None)

        if patient_id is not None:
            patient = User.objects.get(pk=patient_id)
            date_from = today - relativedelta(years=5)
            date_to = today
            query_set = Appointment.objects.filter(patient_id=patient, datetime__gte=date_from, datetime__lte=date_to,
                                                   status=1)

            return query_set

        return Appointment.objects.none()


class UpcomingAppointmentsInstitutionView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-datetime']

    def get_queryset(self):
        institution_id = self.request.query_params.get('institution', default=None)

        if institution_id is not None:
            institution = Institution.objects.get(pk=institution_id)
            today = date.today()
            future_date = today + relativedelta(years=5)
            queryset = Appointment.objects.filter(institution_service_id=institution, datetime__gte=today,
                datetime__lte=future_date, status=Appointment.STATUS_CONFIRMED).order_by('-date')

            return queryset

        return Appointment.objects.none()


class PastAppointmentsInstitutionView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-datetime']

    def get_queryset(self, *args, **kwargs):
        institution_id = self.request.query_params.get('institution', default=None)

        if institution_id is not None:
            institution = Institution.objects.get(pk=institution_id)
            today = datetime.now().date()
            past_date = today - relativedelta(years=5)
            query_set = Appointment.objects.filter(institution_service_id=institution, datetime__gte=past_date,
                datetime__lte=today, status=Appointment.STATUS_CONFIRMED).order_by('-date')

            return query_set

        return Appointment.objects.none()


class RequestsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestViewSerializer
    ordering = ['-appointment_id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('institution_service_id') is not None:
            institution = param.get('institution_service_id')

            query_set = Appointment.objects.filter(institution_service_id=institution, status=0)

            return query_set

        return Appointment.objects.none()


class PatientsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientViewSerializer
    ordering = ['-user_id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params.get('institution')

        if param is not None:
            institution = Institution.objects.get(pk=param)
            appointments = Appointment.objects.filter(institution_service_id=institution)
            query_set = User.objects.filter(patient__in=appointments)

            return query_set

        return User.objects.none()


class WeRecommendView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionViewSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self):
        institutions = Institution.objects.order_by('rating')[:6]
        return institutions


class CitiesListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CityViewSerializer
    pagination_class = CustomPagination
    search_fields = ['city_name']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['city_name']

    def list(self, request, *args, **kwargs):
        city_id = request.query_params.get('city_id', None)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_cities(%s)", [city_id])
            columns = [col[0] for col in cursor.description]
            cities = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(cities)


class CountriesListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CountryViewSerializer

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_countries(NULL, NULL)")
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

class DrugListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DrugSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self):
        drugs = Drug.objects.order_by('drug_name')
        return drugs


class DiagnosisListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DiagnosisSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self):
        diagnosis = Diagnosis.objects.order_by('diagnosis_name')
        return diagnosis


class TreatmentListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TreatmentSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self):
        treatments = Treatment.objects.order_by('drug_id')
        return treatments



class RoleListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RoleSerializer
    pagination_class = CustomPagination
    search_fields = ['role_code']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['role_name']

    def get(self, request, *args, **kwargs):
        role_id = self.request.query_params.get('role_id', None)
        role_code = self.request.query_params.get('role_code', None)
        is_active = self.request.query_params.get('is_active', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_roles(%s, %s, %s)",
                [role_id, role_code, is_active]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class GetUserSettingsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSettingsViewSerializer

    def get(self, request, *args, **kwargs):
        p_user_id = request.query_params.get('p_user_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM get_user_settings(%s)
            """, [p_user_id])
            columns = [col[0] for col in cursor.description]
            user_settings = dict(zip(columns, cursor.fetchone()))

        return Response(user_settings)

class ProfileView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientViewSerializer

    def get(self, request, *args, **kwargs):
             p_user_id = request.query_params.get('p_user_id')

             with connection.cursor() as cursor:
                 cursor.execute("""
                     SELECT * FROM get_user_info(%s)
                 """, [p_user_id])
                 columns = [col[0] for col in cursor.description]
                 user_info = dict(zip(columns, cursor.fetchone()))

             return Response(user_info)


'''
class RatingAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AddRatingSerializer

    def create(self, request, *args, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            institution = Institution.objects.get(pk=param)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_id = request.data.get('user')
            user = User.objects.get(pk=user_id)
            rating_value = request.data.get('rating')

            user_rating = UserRating.objects.create(user=user, institution=institution, rating=rating_value)

            new_average_rating = UserRating.objects.filter(institution=institution).aggregate(average_rating=Avg('rating'))[
                'average_rating']
            institution.average_rating = new_average_rating if new_average_rating is not None else 0.0
            institution.save()

            return Response("Rating added successfully.", status=status.HTTP_201_CREATED)
        except Institution.DoesNotExist:
            return Response({'Failure': 'Institution you are trying to rate does not exist.'}, status=status.HTTP_404_NOT_FOUND)
'''
class UserRolesListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRoleViewSerializer
    pagination_class = CustomPagination
    search_fields = ['role_code']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['role_name']

    def get(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id', None)
        institution_id = self.request.query_params.get('institution_id', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_user_roles(%s, %s)",
                [user_id, institution_id]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class GetPartyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PartyViewSerializer

    def get(self, request, *args, **kwargs):
        p_party_id = request.query_params.get('p_party_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM get_party(%s)
            """, [p_party_id])
            columns = [col[0] for col in cursor.description]
            party = dict(zip(columns, cursor.fetchone()))

        return Response(party)

class MedicalRecordAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = MedicalRecordViewSerializer

    def post(self, request, *args, **kwargs):
        p_medical_record_id = request.data.get('p_medical_record_id')
        p_appointment_id = request.data.get('p_appointment_id', None)
        p_user_id = request.data.get('p_user_id', None)
        p_file = request.data.get('p_file', None)
        p_notes = request.data.get('p_notes', None)
        p_reference_values = request.data.get('p_reference_values', None)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT save_medical_record(
                    %s, %s, %s, %s, %s, %s
                )""", [
                p_medical_record_id, p_appointment_id, p_user_id,
                p_file, p_notes, p_reference_values
            ])
            result = cursor.fetchone()

        return Response({"medical_record_id": result[0]}, status=status.HTTP_201_CREATED)

class AppointmentUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            appointment = Appointment.objects.get(pk=param)
        except Appointment.DoesNotExist:
            return Response({'Failure': 'Appointment does not exist.'}, status.HTTP_404_NOT_FOUND)

        if 'status' in request.data and request.data['status'] == 1 and appointment.date is not None:
            return Response(
                {'Failure': 'You cannot confirm an appointment that has not been confirmed by institution.'},
                status.HTTP_400_BAD_REQUEST)
        else:
            serializer = AppointmentSerializer(instance=appointment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            request_updated(appointment_id=param)

            return Response(data={"Appointment updated successfully."}, content_type="application/json",
                            status=status.HTTP_202_ACCEPTED)


class NotificationConfirmView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')

            notification = Notification.objects.get(pk=param)

        except Notification.DoesNotExist:
            return Response({'Failure': 'Notification you are trying to confirm does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)

        notification.is_confirmed = True
        notification.notification_appointment.status = Appointment.STATUS_CONFIRMED
        notification.notification_appointment.save(update_fields=['status'])
        notification.save(update_fields=['is_confirmed'])

        send_appointment_message(appointment_id=notification.notification_appointment.id)

        return Response('Notification confirmed successfully.', status=status.HTTP_200_OK)


class AppointmentCancelView(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')

            appointment = Appointment.objects.get(pk=param)

        except Appointment.DoesNotExist:
            return Response({'Failure': 'Appointment you are trying to cancel does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)

        appointment.status = Appointment.STATUS_CANCELED
        appointment.save(update_fields=['status'])

        send_appointment_canceled_message(appointment_id=param)

        return Response('Appointment canceled successfully.', status=status.HTTP_200_OK)


class CanceledAppointmentsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-datetime']

    def get_queryset(self, *args, **kwargs):
        query_set = Appointment.objects.filter(status=Appointment.STATUS_CANCELED).order_by('-datetime')
        return query_set

class SaveInstitutionServiceView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SaveInstitutionServiceSerializer(data=request.data)
        if serializer.is_valid():
            institution_id = serializer.validated_data.get('institution_id')
            service_id = serializer.validated_data.get('service_id')
            description = serializer.validated_data.get('description')
            price = serializer.validated_data.get('price')
            is_active = serializer.validated_data.get('is_active')
            duration = serializer.validated_data.get('duration')

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT save_institution_service(%s, %s, %s, %s, %s, %s)",
                    [institution_id, service_id, description, price, is_active, duration]
                )
                new_id = cursor.fetchone()[0]

            return Response({"institution_service_id": new_id}, status=200)

        return Response(serializer.errors, status=400)



class MedicalRecordTemplatesListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = MedicalRecordTemplateViewSerializer
    pagination_class = CustomPagination
    search_fields = ['institution_id']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['institution_id']

    def get(self, request, *args, **kwargs):
        medical_record_template_id = self.request.query_params.get('medical_record_template_id', None)
        institution_id = self.request.query_params.get('institution_id', None)
        is_active = self.request.query_params.get('is_active', None)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM get_medical_record_templates(%s, %s, %s)",
                [institution_id, medical_record_template_id, is_active]
            )
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class SaveInstitutionWorkingHoursView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SaveInstitutionWorkingHoursSerializer(data=request.data)
        if serializer.is_valid():
            institution_id = serializer.validated_data.get('institution_id')
            day_of_week = serializer.validated_data.get('day_of_week')
            open_time = serializer.validated_data.get('open_time')
            close_time = serializer.validated_data.get('close_time')

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT save_institution_working_hours(%s, %s, %s, %s)",
                    [institution_id, day_of_week, open_time, close_time]
                )
                new_id = cursor.fetchone()[0]

            return Response({"institution_working_hour_id": new_id}, status=200)

        return Response(serializer.errors, status=400)

class InstitutionWorkingHoursListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = InstitutionWorkingHoursSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        institution_id = self.request.query_params.get('institution_id', None)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_institution_working_hours(%s)", [institution_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)



class PasswordResetView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "No user found with this email address."}, status=status.HTTP_404_NOT_FOUND)

            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(str(user.pk).encode()).decode()

            reset_link = f"http://localhost:8000/reset-password/{uidb64}-{token}/"

            # send_mail(
            #   'Password Reset',
            #    f'Click the link to reset your password: {reset_link}',
            #   'from@example.com',  # Replace with your email address
            #    [email],
            # )
            return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return "OK"

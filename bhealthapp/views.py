import os
from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from rest_framework import pagination
from rest_framework import status, filters, serializers, fields
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    CreateAPIView, GenericAPIView, DestroyAPIView, ListAPIView, get_object_or_404, UpdateAPIView
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from bhealthapp.models import Lab, LabService, Result, Appointment, User, Notification, UserRating, Service
from src.config import common
from .serializers import LabSerializer, LabServiceViewSerializer, ResultViewSerializer, \
    PatientSerializer, PatientViewSerializer, LabViewSerializer, AppointmentViewSerializer, ResultSerializer, \
    AppointmentSerializer, NotificationViewSerializer, NotificationSerializer, \
    AddRatingSerializer, RequestViewSerializer
from .tasks import send_appointment_canceled_message, send_appointment_message, download_file, request_updated, \
    upload_pdf, send_request_notification

today = datetime.now()


class CustomPagination(pagination.PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 12


class ValidateQueryParams(serializers.Serializer):
    search = fields.RegexField(
        "^[\u0621-\u064A\u0660-\u0669 a-zA-Z0-9]{3,30}$", required=False
    )

    city = fields.RegexField(
        "^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False
    )
    lab = fields.RegexField(
        "^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False
    )
    service = fields.RegexField(
        "^[\u0621-\u064A\u0660-\u0669 a-zA-Z]{3,30}$", required=False
    )
    patient = fields.RegexField(
        "^[\u0621-\u064A\u0660-\u0669 a-zA-Z0-9]{3,30}$", required=False
    )
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
                user_type = 'Patient'
            except User.DoesNotExist:
                try:
                    lab = Lab.objects.get(email=email)
                    user_id = lab.pk
                    user_type = 'Lab'
                    user = lab
                except Lab.DoesNotExist:
                    return Response({'Error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

            if user_type is 'Patient':
                if user.is_blocked:
                    return Response({'Error': 'Your account has been blocked.'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'User Type': user_type,
                'User Id': user_id
            })

        except Exception as e:
            return Response({'Error': 'An error occurred during login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadResult(GenericAPIView):
    serializer_class = ResultSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            result = Result.objects.get(pk=param)
        except Result.DoesNotExist:
            return Response({'Failure': 'Result does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(common.MEDIA_ROOT, result.pdf.name)
        if os.path.exists(file_path):

            download_file.delay(file_path, result.pdf.name)
            return Response({'File download has started asynchronously.'}, status=status.HTTP_201_CREATED)
        else:
            return Response("Cannot download the file.", status=status.HTTP_404_NOT_FOUND)


class LabCreate(GenericAPIView):
    serializer_class = LabSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LabSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password

            lab = serializer.save()
            return Response({'Success': 'New laboratory has been successfully added.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def create(self, request, **kwargs):
        try:
            lab_id = request.data.get('lab_appointment')
            service_id = request.data.get('service_appointment')
            patient_id = request.data.get('patient')
            date = request.data.get('date')

            lab = Lab.objects.get(pk=lab_id)
            service = Service.objects.get(pk=service_id)
            patient = User.objects.get(pk=patient_id)

            appointment = Appointment.objects.create(
                lab_appointment=lab,
                service_appointment=service,
                patient=patient,
                date=date,
                status=Appointment.STATUS_PENDING
            )
            send_request_notification(appointment_id=appointment.id)

            return Response({'Appointment added successfully.'}, status=status.HTTP_201_CREATED)

        except (Lab.DoesNotExist, Service.DoesNotExist, User.DoesNotExist):
            return Response({'Failure': 'One or more related objects do not exist.'}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({'Failure': 'User does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(instance=get_object_or_404(User, pk=param), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)


class NotificationListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NotificationViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    search_fields = ['notification_appointment']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        queryset = Notification.objects.all().order_by('id')

        if param.get('notification_appointment') is not None:
            queryset = queryset.filter(notification_appointment=param.get('notification_appointment'))

        elif param.get('patient') is not None:
            patient_id = int(param.get('patient'))
            queryset = queryset.filter(notification_appointment__patient=patient_id)

        elif param.get('lab') is not None:
            lab_id = int(param.get('lab'))
            queryset = queryset.filter(notification_appointment__lab_appointment=lab_id)

        return queryset


class LabUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabSerializer

    def put(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            Lab.objects.get(pk=param)
        except Lab.DoesNotExist:
            return Response({'Failure': 'Lab does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LabSerializer(instance=get_object_or_404(Lab, pk=param), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.validated_data, content_type="application/json",
                        status=status.HTTP_202_ACCEPTED)


class LabListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    search_fields = ['name', 'city', 'address']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        queryset = Lab.objects.all().order_by('id')

        if param.get('search') is not None:

            search = param.get('search')
            query_set = queryset.filter(Q(lab__name__contains=search) | Q(service__name__contains=search))

        elif param.get('city') is not None:
            query_set = queryset.filter(city=param.get('city'))

        elif param.get('name') is not None:
            query_set = queryset.filter(name__contains=param.get('name'))

        elif param.get('address') is not None:
            query_set = queryset.filter(address__contains=param.get('address'))

        else:
            query_set = queryset

        return query_set


class LabView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = Lab.objects.get(pk=param)
        except Lab.DoesNotExist:
            return Response({'Failure': 'Lab does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LabViewSerializer(lab)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")


class LabServiceListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabServiceViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        queryset = LabService.objects.all().order_by('id')

        if param.get('search') is not None:

            search = param.get('search')
            query_set = queryset.filter(Q(lab__name__contains=search) | Q(service__name__contains=search))

        elif param.get('city') is not None:
            query_set = queryset.filter(lab_service__city=param.get('city'))

        elif param.get('lab') is not None:
            query_set = queryset.filter(lab_service__pk=param.get('lab'))

        elif param.get('service') is not None:
            query_set = queryset.filter(lab_service__city__contains=param.get('service'))

        else:
            query_set = queryset

        return query_set


class LabServiceView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabServiceViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = LabService.objects.get(pk=param)
        except LabService.DoesNotExist:
            return Response({'Failure': 'Service does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LabServiceViewSerializer(lab)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")


class LabAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabSerializer

    def create(self, request, **kwargs):
        param = self.request.query_params.get('pk', default=None)
        lab = Lab.objects.get(pk=param)

        if lab.exists():
            return Response({'Failure': 'Lab already exists.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = LabSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class LabRemoveView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Lab.objects.all()

    def delete(self, request, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = Lab.objects.get(pk=param)
        except Lab.DoesNotExist:
            return Response({'Failure': 'Article does not exist or has been already removed.'},
                            status=status.HTTP_404_NOT_FOUND)
        response = lab
        response.delete()
        return Response({"You have successfully deleted desired lab."}, status=status.HTTP_200_OK)


class ResultListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResultViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        if param.get('patient') is not None:

            patient = param.get('patient')
            query_set = Result.objects.filter(appointment__patient=patient)

        elif param.get('appointment') is not None:

            appointment = param.get('appointment')
            query_set = Result.objects.filter(appointment=appointment)

        else:
            query_set = Result.objects.none()

        return query_set


class ResultView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResultViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            result = Result.objects.get(pk=param)
        except Result.DoesNotExist:
            return Response({'Failure': 'Result does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResultViewSerializer(result)
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


class UpcomingAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params.get('patient', default=None)

        if param is not None:

            patient = User.objects.get(pk=param)
            date_from = today
            date_to = today + relativedelta(years=5)
            query_set = Appointment.objects.filter(patient=patient, date__gte=date_from, date__lte=date_to,
                                                   status=1)

        else:
            query_set = Appointment.objects.none()

        return query_set


class PastAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        patient_id = self.request.query_params.get('patient', default=None)

        if patient_id is not None:
            patient = User.objects.get(pk=patient_id)
            date_from = today - relativedelta(years=5)
            date_to = today
            query_set = Appointment.objects.filter(patient=patient, date__gte=date_from, date__lte=date_to,
                                                   status=1)

            return query_set

        return Appointment.objects.none()


class UpcomingAppointmentsLabView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-date']

    def get_queryset(self):
        lab_id = self.request.query_params.get('lab', default=None)

        if lab_id is not None:
            lab = Lab.objects.get(pk=lab_id)
            today = date.today()
            future_date = today + relativedelta(years=5)
            queryset = Appointment.objects.filter(
                lab_appointment=lab,
                date__gte=today,
                date__lte=future_date,
                status=Appointment.STATUS_CONFIRMED
            ).order_by('-date')

            return queryset

        return Appointment.objects.none()


class PastAppointmentsLabView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
    pagination_class = CustomPagination
    search_fields = ['patient']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-date']

    def get_queryset(self, *args, **kwargs):
        lab_id = self.request.query_params.get('lab', default=None)

        if lab_id is not None:
            lab = Lab.objects.get(pk=lab_id)
            today = datetime.now().date()
            past_date = today - relativedelta(years=5)
            query_set = Appointment.objects.filter(
                lab_appointment=lab,
                date__gte=past_date,
                date__lte=today,
                status=Appointment.STATUS_CONFIRMED
            ).order_by('-date')

            return query_set

        return Appointment.objects.none()


class RequestsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('lab_appointment') is not None:
            lab = param.get('lab_appointment')

            query_set = Appointment.objects.filter(lab_appointment=lab, status=0)

            return query_set

        return Appointment.objects.none()


class PatientsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params.get('lab')

        if param is not None:
            lab = Lab.objects.get(pk=param)
            appointments = Appointment.objects.filter(lab_appointment=lab)
            query_set = User.objects.filter(patient__in=appointments)

            return query_set

        return User.objects.none()


class WeRecommendView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabViewSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self):
        labs = Lab.objects.order_by('-average_rating')[:6]
        return labs


class ProfileView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            user = User.objects.get(pk=param)
        except User.DoesNotExist:
            return Response({'Failure': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientViewSerializer(user)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")


class RatingAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AddRatingSerializer

    def create(self, request, *args, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = Lab.objects.get(pk=param)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_id = request.data.get('user')
            user = User.objects.get(pk=user_id)
            rating_value = request.data.get('rating')

            user_rating = UserRating.objects.create(user=user, lab=lab, rating=rating_value)

            new_average_rating = UserRating.objects.filter(lab=lab).aggregate(average_rating=Avg('rating'))[
                'average_rating']
            lab.average_rating = new_average_rating if new_average_rating is not None else 0.0
            lab.save()

            return Response("Rating added successfully.", status=status.HTTP_201_CREATED)
        except Lab.DoesNotExist:
            return Response({'Failure': 'Lab you are trying to rate does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class ResultAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResultSerializer

    def create(self, request, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')

            app = Appointment.objects.get(pk=param)

            serializer = ResultSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            result = Result.objects.last()
            result.appointment = app
            result.save(update_fields=['appointment'])

        except Appointment.DoesNotExist:
            return Response({'Failure': 'Appointment you are trying to add result for does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)

        upload_pdf(appointment_id=param)
        return Response("Result added successfully.", status=status.HTTP_200_OK)


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
            return Response({'Failure': 'Appointment does not exist.'},
                            status.HTTP_404_NOT_FOUND)

        if 'status' in request.data and request.data['status'] == 1 and appointment.date is not None:
            return Response({'Failure': 'You cannot confirm an appointment that has not been confirmed by lab.'},
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
    ordering_fields = ['-date']

    def get_queryset(self, *args, **kwargs):
        query_set = Appointment.objects.filter(status=Appointment.STATUS_CANCELED).order_by('-date')
        return query_set

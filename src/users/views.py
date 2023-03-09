import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework import pagination
from rest_framework import status, filters, serializers, fields
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    CreateAPIView, GenericAPIView, DestroyAPIView, ListAPIView, get_object_or_404
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Lab, LabService, Result, Appointment, User, UserRating
from .serializers import LabSerializer, LabServiceViewSerializer, UserRatingViewSerializer, ResultViewSerializer, \
    PatientSerializer, PatientViewSerializer, LabViewSerializer, \
    AppointmentViewSerializer, PatientLoginSerializer, UserRatingSerializer, ResultSerializer, AppointmentSerializer

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

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

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabCreate(GenericAPIView):
    serializer_class = LabSerializer

    def post(self, request):
        serializer = LabSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddAppointmentView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def create(self, request, **kwargs):
        serializer = AppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status.HTTP_201_CREATED)


class UserLogin(GenericAPIView):
    serializer_class = PatientLoginSerializer

    def post(self, request):
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("main:homepage")
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")
        form = AuthenticationForm()
        return render(request=request, template_name="src/users/login.html", context={"login_form": form})


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
                            status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(instance=get_object_or_404(User, pk=param), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status.HTTP_202_ACCEPTED)


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
            return Response({'Failure': 'Lab does not exist.'},
                            status.HTTP_404_NOT_FOUND)

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
            return Response({'Failure': 'Lab does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = LabViewSerializer(lab)
        data = serializer.data

        return Response(data, content_type="application/json")


class LabServiceListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabServiceViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    search_fields = ['lab__name', 'city', 'service']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        queryset = LabService.objects.all().order_by('id')

        if param.get('search') is not None:

            search = param.get('search')
            query_set = queryset.filter(Q(lab__name__contains=search) | Q(service__name__contains=search))

        elif param.get('city') is not None:
            query_set = queryset.filter(lab_service__city=param.get('city'))

        elif param.get('lab') is not None:
            query_set = queryset.filter(lab_service__contains=param.get('lab'))

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
            return Response({'Failure': 'Service does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = LabServiceViewSerializer(lab)
        data = serializer.data

        return Response(data, content_type="application/json")


class LabAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabSerializer

    def create(self, request, **kwargs):
        param = self.request.query_params.get('pk', default=None)
        lab = Lab.objects.get(pk=param)

        if lab.exists():
            return Response({'Failure': 'Lab already exists.'}, status.HTTP_200_OK)

        serializer = LabSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.validated_data, status.HTTP_201_CREATED)


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
        return Response(
            data={
                "message": "You have successfully deleted desired lab."
            },
            status=status.HTTP_200_OK
        )


class ResultListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResultViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('patient') is not None:

            patient = param.get('patient')
            query_set = Result.objects.filter(patient=patient)

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
            return Response({'Failure': 'Result does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = ResultViewSerializer(result)
        data = serializer.data

        return Response(data, content_type="application/json")
    # add options for patient id search
    # add to get per appointment id


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
            return Response({'Failure': 'Appointment does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = AppointmentViewSerializer(appointment)
        data = serializer.data

        return Response(data, content_type="application/json")


class UpcomingAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('patient') is not None:

            patient = param.get('patient')
            date_from = today
            date_to = today + relativedelta(years=5)
            query_set = Appointment.objects.filter(patient=patient, datetime__gte=date_from, datetime__lte=date_to)

        else:
            query_set = Appointment.objects.none()

        return query_set


class PastAppointmentsUserView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('patient') is not None:

            patient = param.get('patient')
            date_from = today - relativedelta(years=5)
            date_to = today
            query_set = Appointment.objects.filter(patient=patient, datetime__gte=date_from, datetime__lte=date_to)

        else:
            query_set = Appointment.objects.none()

        return query_set


class UpcomingAppointmentsLabView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('lab') is not None:

            lab = param.get('lab')
            date_from = today
            date_to = today + relativedelta(years=5)
            query_set = Appointment.objects.filter(lab_appointment=lab, datetime__gte=date_from,
                                                   datetime__lte=date_to)
            if param.get('today') is True:
                query_set = Appointment.objects.filter(lab_appointment=lab, datetime__gte=today,
                                                       datetime__lte=today)

        else:
            query_set = Appointment.objects.all()

        return query_set


class PastAppointmentsLabView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('lab') is not None:

            lab = param.get('lab')
            date_from = today - relativedelta(years=5)
            date_to = today
            query_set = Appointment.objects.filter(lab_appointment=lab, datetime__gte=date_from, datetime__lte=date_to)

        else:
            query_set = Appointment.objects.all()

        return query_set


class RequestsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentViewSerializer
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
            # date is null

        else:
            query_set = Appointment.objects.none()

        return query_set


class PatientsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get_queryset(self, *args, **kwargs):
        param = self.request.query_params

        query_params = ValidateQueryParams(data=param)
        query_params.is_valid(raise_exception=True)

        if param.get('lab') is not None:

            lab = param.get('lab')

            query_set = User.objects.filter(lab=lab)

        else:
            query_set = User.objects.none()

        return query_set


class WeRecommendView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRatingViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    def get(self, *args, **kwargs):
        labs = Lab.objects.all()
        my_dict = {}

        for lab in labs:
            my_dict[lab.name] = UserRating.objects.filter(rating=5, lab=lab).count()

        top_6_labs = sorted(my_dict.items(), key=lambda x: x[1])[:6]
        return Response(top_6_labs, content_type="application/json")


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
            return Response({'Failure': 'User does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = PatientViewSerializer(user)
        data = serializer.data

        return Response(data, content_type="application/json")


class RatingAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRatingSerializer

    def create(self, request, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')

            lab = Lab.objects.get(pk=param)

        except Lab.DoesNotExist:
            return Response({'Failure': 'Lab you are willing to rate does not exist.'},
                            status.HTTP_404_NOT_FOUND)

        serializer = UserRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        rating = UserRating.objects.last()
        rating.lab = lab
        rating.save(update_fields=['lab'])

        return Response(serializer.data, content_type="application/json")


class ResultAddView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResultSerializer

    def create(self, request, **kwargs):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')

            appointment = Appointment.objects.get(pk=param)

        except Appointment.DoesNotExist:
            return Response({'Failure': 'Appointment you are trying to add result for does not exist.'},
                            status.HTTP_404_NOT_FOUND)

        serializer = ResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        result = Result.objects.last()
        result.appointment = appointment
        result.save(update_fields=['appointment'])

        return Response(serializer.data, content_type="application/json")

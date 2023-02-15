import logging
from datetime import datetime

from django.db.models import Q
from rest_framework import pagination
from rest_framework import status, filters, serializers, fields
from rest_framework.generics import (
    CreateAPIView, GenericAPIView, DestroyAPIView, ListAPIView
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Lab, LabService, Result, Appointment
from .serializers import LabSerializer, LabServiceViewSerializer, ResultViewSerializer, AppointmentSerializer, AppointmentViewSerializer

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

    date = fields.DateField(format='%Y-%m-%d', required=False)
    date_from = fields.DateField(format='%Y-%m-%d', required=False)
    date_to = fields.DateField(format='%Y-%m-%d', required=False)
    pk = fields.RegexField("^[\u0621-\u064A\u0660-\u0669 0-9]{3,30}$", required=False)
    day = fields.IntegerField(min_value=1, max_value=30, required=False)
    year = fields.IntegerField(min_value=1990, max_value=today.year, required=False)


class LabListView(ListAPIView):
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

        queryset = LabService.objects.all().order_by('lab_id')

        if param.get('search') is not None:

            search = param.get('search')
            query_set = queryset.filter(Q(lab__name__contains=search) | Q(service__name__contains=search))

        elif param.get('city') is not None:
            query_set = queryset.filter(city=param.get('city'))

        elif param.get('lab') is not None:
            query_set = queryset.filter(lab=param.get('lab'))

        elif param.get('service') is not None:
            query_set = queryset.filter(city=param.get('service'))

        else:
            query_set = queryset

        return query_set


class LabView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabServiceViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = LabService.objects.get(pk=param)
        except LabService.DoesNotExist:
            return Response({'Failure': 'Lab does not exist.'}, status.HTTP_404_NOT_FOUND)

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

        serializer = LabServiceViewSerializer(result)
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
            query_set = Appointment.objects.filter(patient=patient, datetime=#svi veci od now)

        else:
            query_set = Appointment.objects.none()

        return query_set

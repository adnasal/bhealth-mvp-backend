
import calendar
import logging
from datetime import datetime, timedelta
from time import strptime

from django.core.cache import cache
from django.db.models import Q, Count
from rest_framework import pagination
from rest_framework import status, filters, serializers, fields
from rest_framework.generics import (
    CreateAPIView, GenericAPIView, DestroyAPIView, ListAPIView, get_object_or_404
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import City, Appointment, User, Lab
from .serializers import LabSerializer, LabViewSerializer, PatientSerializer, PatientViewSerializer, AppointmentSerializer, AppointmentViewSerializer


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
    serializer_class = LabViewSerializer
    ordering = ['-id']
    pagination_class = CustomPagination

    def get_queryset(self, *args, **kwargs):
        labs = Lab.objects.all()
        return labs


class LabView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LabViewSerializer

    def get(self, request):
        try:
            param = self.request.query_params.get('pk', default=None)
            if param is None:
                return Response('Please add primary key.')
            lab = Lab.objects.get(pk=param, is_archived=False, is_deleted=False).defer('external_id')
        except Lab.DoesNotExist:
            return Response({'Failure': 'Lab does not exist.'}, status.HTTP_404_NOT_FOUND)

        serializer = LabViewSerializer(lab)
        data = serializer.data

        return Response(data, content_type="application/json")


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


from .models import City, Appointment, Patient, Lab, Doctor
from .serializers import DoctorSerializer


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

today = datetime.now()


class DoctorListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DoctorSerializer

    def get_queryset(self, *args, **kwargs):
        doctors = Doctor.objects.all()

        return doctors


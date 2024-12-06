from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from bhealthapp.models import InstitutionWorkingHours
from bhealthapp.views import UserCreate, InstitutionView, UpcomingAppointmentsUserView, \
    PastAppointmentsUserView, ProfileView, PatientsView, MedicalRecordView, RequestsView, UserLogin, InstitutionCreate, \
    UserUpdateView, \
    AppointmentAddView, AppointmentView, NotificationListView, AppointmentUpdateView, NotificationConfirmView, \
    AppointmentCancelView, CanceledAppointmentsView, WeRecommendView, InstitutionListView, InstitutionServiceListView, \
    MedicalRecordListView, MedicalRecordAddView, InstitutionRemoveView, PastAppointmentsInstitutionView, \
    UpcomingAppointmentsInstitutionView, InstitutionUpdateView, InstitutionLogin, DownloadMedicalRecord, \
    InstitutionAddView, PasswordResetRequestView, PasswordResetView, InstitutionWorkingHoursListView, DrugListView, \
    DiagnosisListView, TreatmentListView, RoleListView
from src.common.constants import API_PREFIX

schema_view = get_schema_view(
    openapi.Info(title="Pastebin API", default_version='v1'),
    public=True,
)

urlpatterns = [
    # Admin panel
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('admin/', admin.site.urls),

    # API Endpoints
    path(f'{API_PREFIX}register_user', UserCreate.as_view(), name='account_create'),
    path(f'{API_PREFIX}register_institution', InstitutionCreate.as_view(), name='institution_account_create'),
    path(f'{API_PREFIX}login', UserLogin.as_view(), name='login'),
    path(f'{API_PREFIX}password_reset_request', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path(f'{API_PREFIX}password_reset', PasswordResetView.as_view(), name='password_reset'),
    path(f'{API_PREFIX}institution_login', InstitutionLogin.as_view(), name='institution_login'),
    path(f'{API_PREFIX}institutions', InstitutionListView.as_view(), name='labs'),
    path(f'{API_PREFIX}notifications', NotificationListView.as_view(), name='notifications'),
    path(f'{API_PREFIX}drugs', DrugListView.as_view(), name='drugs'),
    path(f'{API_PREFIX}diagnosis', DiagnosisListView.as_view(), name='diagnosis'),
    path(f'{API_PREFIX}treatments', TreatmentListView.as_view(), name='treatments'),
    path(f'{API_PREFIX}roles', RoleListView.as_view(), name='roles'),
    path(f'{API_PREFIX}confirm_notification', NotificationConfirmView.as_view(), name='confirm_notification'),
    path(f'{API_PREFIX}working_hours', InstitutionWorkingHoursListView.as_view(), name='working_hours'),
    path(f'{API_PREFIX}institution_services', InstitutionServiceListView.as_view(), name='lab_services'),
    path(f'{API_PREFIX}edit_profile_user', UserUpdateView.as_view(), name='edit_profile_user'),
    path(f'{API_PREFIX}edit_profile_institution', InstitutionUpdateView.as_view(), name='edit_profile_institution'),
    path(f'{API_PREFIX}add_appointment', AppointmentAddView.as_view(), name='add_appointment'),
    path(f'{API_PREFIX}update_appointment', AppointmentUpdateView.as_view(), name='update_appointment'),
    path(f'{API_PREFIX}cancel_appointment', AppointmentCancelView.as_view(), name='cancel_appointment'),
    path(f'{API_PREFIX}medical_records', MedicalRecordListView.as_view(), name='medical_records'),
    path(f'{API_PREFIX}download_medical_record', DownloadMedicalRecord.as_view(), name='download_medical_record'),
    path(f'{API_PREFIX}appointment', AppointmentView.as_view(), name='get_appointment'),
    path(f'{API_PREFIX}canceled_appointments', CanceledAppointmentsView.as_view(), name='canceled_appointments'),
    path(f'{API_PREFIX}upcoming_appointments', UpcomingAppointmentsUserView.as_view(), name='user_upcoming_appointments'),
    path(f'{API_PREFIX}past_appointments', PastAppointmentsUserView.as_view(), name='user_past_appointments'),
    path(f'{API_PREFIX}u_appointments', UpcomingAppointmentsInstitutionView.as_view(), name='institution_upcoming_appointments'),
    path(f'{API_PREFIX}p_appointments', PastAppointmentsInstitutionView.as_view(), name='institution_past_appointments'),
    path(f'{API_PREFIX}requests', RequestsView.as_view(), name='requests'),
    path(f'{API_PREFIX}patients', PatientsView.as_view(), name='patients'),
    path(f'{API_PREFIX}institution', InstitutionView.as_view(), name='get_lab'),
    path(f'{API_PREFIX}add_institution', InstitutionAddView.as_view(), name='add_institution'),
    path(f'{API_PREFIX}remove_institution', InstitutionRemoveView.as_view(), name='remove_institution'),
    path(f'{API_PREFIX}we_recommend', WeRecommendView.as_view(), name='top_institutions'),
    path(f'{API_PREFIX}medical_record', MedicalRecordView.as_view(), name='get_medical_record'),
    path(f'{API_PREFIX}profile', ProfileView.as_view(), name='get_profile'),
    #path(f'{API_PREFIX}add_rating', RatingAddView.as_view(), name='add_rating'),
    path(f'{API_PREFIX}add_medical_record', MedicalRecordAddView.as_view(), name='add_medical_record'),
    path(f'{API_PREFIX}password_reset_dj/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    # Auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(f'{API_PREFIX}token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f'{API_PREFIX}token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger Docs
    path('swagger/', get_schema_view(
        openapi.Info(title="Pastebin API", default_version='v1', description="API for Pastebin"),
        public=True
    ).with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('redoc/', get_schema_view(
        openapi.Info(title="Pastebin API", default_version='v1', description="API for Pastebin"),
        public=True
    ).with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('swagger.json', get_schema_view(
        openapi.Info(title="Pastebin API", default_version='v1', description="API for Pastebin"),
        public=True
    ).without_ui(cache_timeout=0), name='schema-json'),

    # Health check
    #path('health/', include('health_check.urls')),

    # Root API
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

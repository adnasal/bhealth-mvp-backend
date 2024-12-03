from django.contrib import admin

from bhealthapp.models import City, User, Service, MedicalRecord, Appointment, Institution, Notification


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'

    fieldsets = (
        (None, {
            'fields': ['city_name', 'country_id']
        }),
    )

    list_display = ['city_name', 'country_id']
    classes = ['wide', 'extrapretty']
    list_filter = ['country_id']
    search_fields = ('city_name__startswith',)



# admin.site.register(City, CityAdmin)


@admin.register(User)
class PatientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': [
                'username', 'party', 'password', 'phone_number', 'email', 'dob',
                'is_blocked', 'is_email_verified', 'gender']
        }),
    )

    list_display = ['username', 'party', 'password', 'phone_number', 'email', 'dob',
                    'is_blocked', 'is_email_verified', 'gender']

    empty_value_display = '-empty-'
    list_filter = ['party', 'gender']

# admin.site.register(Patient, PatientAdmin)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['city_id', 'institution_name', 'password', 'address', 'phone_numbers', 'emails', 'website', 'rating']
        }),
    )

    list_display = ['city_id', 'institution_name', 'password', 'address', 'phone_numbers', 'emails', 'website']

    empty_value_display = '-empty-'
    list_filter = ['institution_name', 'city_id', 'rating']
    search_fields = ("institution_name__startswith",)


# admin.site.register(Lab, LabAdmin)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['service_name', 'service_category', 'description']
        }),
    )

    list_display = ['service_name', 'service_category', 'description']
    empty_value_display = '-empty-'
    list_filter = ['service_name', 'service_category']


# admin.site.register(Service, ServiceAdmin)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['institution_service_id', 'doctor_id', 'datetime', 'patient_id', 'appointment_status']
        }),
    )

    list_display = ['institution_service_appointment', 'doctor_id', 'datetime', 'patient_id', 'appointment_status']
    date_hierarchy = 'datetime'
    empty_value_display = '-empty-'
    list_filter = ['institution_service_appointment', 'doctor_id', 'appointment_status', 'patient_id']


# admin.site.register(Appointment, AppointmentAdmin)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['appointment_id', 'user_id', 'file']
        }),
    )

    list_display = ['appointment_id','user_id', 'file']
    empty_value_display = '-empty-'
    list_filter = ['appointment_id', 'user_id']


# admin.site.register(Result, ResultAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['user_id', 'payload_data', 'is_confirmed',
                       ]
        }),
    )

    list_display = ['user_id', 'payload_data', 'is_confirmed',
                    ]
    empty_value_display = '-empty-'
    list_filter = ['user_id', 'is_confirmed']

# admin.site.register(Notification, NotificationAdmin)

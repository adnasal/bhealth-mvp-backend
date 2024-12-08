from django.contrib import admin

from bhealthapp.models import City, User, Service, MedicalRecord, Appointment, Institution, Notification, Country


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

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'

    fieldsets = (
        (None, {
            'fields': ['country_name', 'country_code']
        }),
    )

    list_display = ['country_name', 'country_code']
    classes = ['wide', 'extrapretty']
    list_filter = ['country_code']
    search_fields = ('country_name__startswith',)



# admin.site.register(City, CityAdmin)

@admin.register(User)
class PatientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': [
                'username', 'party_id', 'password', 'phone_number', 'email', 'dob',
                'is_email_verified', 'gender']
        }),
    )

    list_display = ['username', 'party_id', 'password', 'phone_number', 'email', 'dob',
                    'is_email_verified', 'gender']

    empty_value_display = '-empty-'
    list_filter = ['party_id', 'gender']

# admin.site.register(Patient, PatientAdmin)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['city_id', 'institution_name', 'password', 'address', 'phone_number', 'email', 'website', 'rating']
        }),
    )

    list_display = ['city_id', 'institution_name', 'password', 'address', 'phone_number', 'email', 'website']

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
            'fields': ['institution_service_id', 'datetime', 'patient_id', 'status']
        }),
    )

    list_display = ['institution_service_appointment', 'datetime', 'patient_id', 'status']
    date_hierarchy = 'datetime'
    empty_value_display = '-empty-'
    list_filter = ['institution_service_id', 'status', 'patient_id']

    def institution_service_appointment(self, obj):
        return obj.institution_service_id.service_name

    institution_service_appointment.admin_order_field = 'institution_service_id'
    institution_service_appointment.short_description = 'Institution Service'

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
            'fields': ['user_id', 'payload_data'
                       ]
        }),
    )

    list_display = ['user_id', 'payload_data'
                    ]
    empty_value_display = '-empty-'
    list_filter = ['user_id']

# admin.site.register(Notification, NotificationAdmin)

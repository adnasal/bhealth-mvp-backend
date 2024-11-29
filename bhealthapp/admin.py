from django.contrib import admin

from bhealthapp.models import City, User, Type, Service, Result, Appointment, Lab, UserRating, Notification


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'

    fieldsets = (
        (None, {
            'fields': ['name', 'country']
        }),
        ('Further information:', {
            'fields': ['postal_code']
        }),
    )

    list_display = ['name', 'country', 'postal_code']
    classes = ['wide', 'extrapretty']
    list_filter = ['country']
    search_fields = ("name__startswith",)


# admin.site.register(City, CityAdmin)


@admin.register(User)
class PatientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': [
                'profile_picture', 'profile_link', 'password', 'phone_number', 'email', 'dob',
                'address', 'city', 'is_blocked', 'is_email_verified', 'gender']
        }),
    )

    list_display = ['profile_picture', 'profile_link', 'password', 'phone_number', 'email', 'dob',
                    'address', 'city', 'is_blocked', 'is_email_verified', 'gender']

    empty_value_display = '-empty-'
    list_filter = ['city', 'gender']

# admin.site.register(Patient, PatientAdmin)


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website', 'working_days']
        }),
    )

    list_display = ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website']

    empty_value_display = '-empty-'
    list_filter = ['name', 'city']
    search_fields = ("name__startswith",)


# admin.site.register(Lab, LabAdmin)


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['user', 'rating', 'lab']
        }),
    )

    list_display = ['user', 'rating', 'lab']
    empty_value_display = '-empty-'
    list_filter = ['lab']
    search_fields = ("lab__startswith",)


# admin.site.register(UserRating, UserRatingAdmin)


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['name', 'description']
        }),
    )

    list_display = ['name', 'description']
    empty_value_display = '-empty-'
    list_filter = ['name']
    search_fields = ("name__startswith",)


# admin.site.register(Type, TypeAdmin)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['name', 'duration', 'type']
        }),
    )

    list_display = ['name', 'duration', 'type']
    empty_value_display = '-empty-'
    list_filter = ['name', 'type']


# admin.site.register(Service, ServiceAdmin)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['lab_appointment', 'service_appointment', 'date', 'patient', 'status']
        }),
    )

    list_display = ['lab_appointment', 'service_appointment', 'date', 'patient', 'status']
    date_hierarchy = 'date'
    empty_value_display = '-empty-'
    list_filter = ['lab_appointment', 'service_appointment', 'status', 'patient']


# admin.site.register(Appointment, AppointmentAdmin)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['appointment', 'pdf']
        }),
    )

    list_display = ['appointment', 'pdf']
    empty_value_display = '-empty-'
    list_filter = ['appointment']


# admin.site.register(Result, ResultAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['notification_appointment', 'message', 'is_confirmed',
                       ]
        }),
    )

    list_display = ['notification_appointment', 'message', 'is_confirmed',
                    ]
    empty_value_display = '-empty-'
    list_filter = ['notification_appointment', 'is_confirmed',
                   ]

# admin.site.register(Notification, NotificationAdmin)

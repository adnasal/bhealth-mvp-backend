from django.contrib import admin

from .models import City, User, Type, Service, Result, Appointment, Lab, UserRating, Notification


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
                'profile_picture', 'profile_link', 'name', 'surname', 'password', 'phone_number', 'email', 'dob',
                'address', 'city', 'joined_at', 'is_blocked', 'is_email_verified', 'gender']
        }),
    )

    list_display = ['profile_picture', 'profile_link', 'name', 'surname', 'password', 'phone_number', 'email', 'dob',
                    'address', 'city', 'joined_at', 'is_blocked', 'is_email_verified', 'gender']

    date_hierarchy = 'joined_at'
    empty_value_display = '-empty-'
    list_filter = ['name', 'surname', 'city', 'gender']
    search_fields = ("name__startswith",)


# admin.site.register(Patient, PatientAdmin)


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['city', 'name', 'password', 'address', 'phone_number', 'email', 'website']
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
            'fields': ['name', 'duration', 'description', 'type']
        }),
    )

    list_display = ['name', 'duration', 'description', 'type']
    empty_value_display = '-empty-'
    list_filter = ['name', 'type']


# admin.site.register(Service, ServiceAdmin)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['city_appointment', 'lab_appointment', 'service_appointment', 'date', 'patient', 'status']
        }),
    )

    list_display = ['city_appointment', 'lab_appointment', 'service_appointment', 'date', 'patient', 'status']
    date_hierarchy = 'date'
    empty_value_display = '-empty-'
    list_filter = ['lab_appointment', 'service_appointment', 'status', 'patient']


# admin.site.register(Appointment, AppointmentAdmin)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['appointment', 'patient', 'pdf']
        }),
    )

    list_display = ['appointment', 'patient', 'pdf']
    empty_value_display = '-empty-'
    list_filter = ['appointment', 'patient']


# admin.site.register(Result, ResultAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['notification_lab', 'notification_user', 'notification_appointment', 'message', 'is_confirmed',
                       'is_declined']
        }),
    )

    list_display = ['notification_lab', 'notification_user', 'notification_appointment', 'message', 'is_confirmed',
                    'is_declined']
    empty_value_display = '-empty-'
    list_filter = ['notification_lab', 'notification_user', 'notification_appointment', 'is_confirmed',
                   'is_declined']

# admin.site.register(Notification, NotificationAdmin)

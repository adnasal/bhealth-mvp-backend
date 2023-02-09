from django.db.models.signals import post_save #Import a post_save signal when a user is created
from django.contrib.auth.models import User # Import the built-in User model, which is a sender
from django.dispatch import receiver # Import the receiver
from .models import Patient


@receiver(post_save, sender=Patient)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Patient.objects.create(user=instance)


@receiver(post_save, sender=Patient)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
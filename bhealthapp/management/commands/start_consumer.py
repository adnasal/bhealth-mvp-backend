from django.core.management.base import BaseCommand
from bhealthapp.consumer import Consumer


class Command(BaseCommand):
    help = "Start the consumer"

    def handle(self, **options):
        apt_consumer = Consumer()
        apt_consumer.start()


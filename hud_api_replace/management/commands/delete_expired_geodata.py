from django.core.management.base import BaseCommand, CommandError
import time

from hud_api_replace.models import CachedGeodata


class Command(BaseCommand):
    help = 'Deletes geodata records that are expired.'

    def handle(self, *args, **options):
        CachedGeodata.objects.all().filter(expires__lte=time.time()).delete()

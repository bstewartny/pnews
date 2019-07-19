from django.core.management.base import BaseCommand, CommandError

from portal.models import *
from portal.tasks import *

class Command(BaseCommand):
    help='Process feeds'
    def handle(self,*args,**options):
        print('start loading feeds...')
        Feed.objects.all().delete()
        load_feeds()
        print('loading feeds done.')	


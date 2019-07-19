from django.core.management.base import BaseCommand, CommandError

from portal.models import *
from portal.tasks import *

class Command(BaseCommand):
	help='Process feeds'
	def handle(self,*args,**options):
		print('start processing feeds...')
		process_feeds()
		print('processing feeds done.')	


from django.core.management.base import BaseCommand, CommandError

from portal.models import *
from portal.tasks import *

class Command(BaseCommand):
	help='Process entities'
	def handle(self,*args,**options):
		print('start processing entities...')
		process_entities()
		print('processing entities done.')	


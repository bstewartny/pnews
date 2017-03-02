from django.core.management.base import NoArgsCommand, CommandError

from portal.models import *
from portal.tasks import *

class Command(NoArgsCommand):
	help='Process feeds'
	def handle_noargs(self,**options):
		print 'start loading feeds...'
		load_feeds()
		print 'loading feeds done.'	


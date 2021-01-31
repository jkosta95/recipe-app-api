
import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    """ Django command to pause execution until db is available """

    def handle(self, *args, **options):
        """
            - allow for passing in custom arguments and options to our
            management commands just in case we want to customize the wait time
            for example

        """
        self.stdout.write('Waiting for database. . .')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
        

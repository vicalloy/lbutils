from django.core.management.base import BaseCommand
from lbutils import as_callable


class Command(BaseCommand):
    help = "Call function"

    def add_arguments(self, parser):
        parser.add_argument('func')

    def handle(self, *args, **options):
        func = options['func']
        func = as_callable(func)
        func()

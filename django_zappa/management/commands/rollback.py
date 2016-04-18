
from django.core.management.base import BaseCommand
from zappa.zappa import Zappa

from .zappa_command import ZappaCommand


class Command(ZappaCommand):
    help = '''Rollback to specific version of a Zappa deploy.
              python manage.py rollback dev 3'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)
        parser.add_argument('revision', nargs='+', type=int)

    def handle(self, *args, **options):

        # Load the settings
        self.require_settings(args, options)

        # Load your AWS credentials from ~/.aws/credentials
        self.load_credentials()

        #Get the Django settings file
        self.get_django_settings_file()

        revision = options['revision'][0]

        print("Rolling back..")

        self.zappa.rollback_lambda_function_version(
            self.lambda_name, versions_back=revision)
        print("Done!")

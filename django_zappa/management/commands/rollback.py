from django.core.management.base import BaseCommand
from zappa.zappa import Zappa

class Command(BaseCommand):
    help = '''Rollback to specific version of a Zappa deploy.
              python manage.py rollback dev 3'''

    def add_arguments(self, parser):
        parser.add_argument('rollback_values', nargs='+', type=str)

    def handle(self, *args, **options):
        if len(options['rollback_values']) != 2:
            self.stdout.write("You need to pass in both a function name and number of version to go back")
            return

        function_name, revision = options['rollback_values']

        try:
            int(revision)
        except ValueError:
            self.stdout.write("2nd argument needs to be an integer")
            return

        # Make your Zappa object
        zappa = Zappa()
        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        response = zappa.rollback_lambda_function_version(function_name, versions_back=revision)

        if response:
            self.stdout.write('Rollback Successful')
        else:
            self.stdout.write('Rollback Failed')
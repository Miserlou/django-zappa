import os

from django.core.management.base import BaseCommand
from zappa.zappa import Zappa

class Command(BaseCommand):
    help = '''Rollback to specific version of a Zappa deploy.
              python manage.py rollback dev 3'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)
        parser.add_argument('revision', nargs='+', type=int)

    def handle(self, *args, **options):

        if not options.has_key('environment'):
            print("You must call rollback with an environment name. \n python manage.py rollback <environment> <revisions>")
            return

        from django.conf import settings
        if not 'ZAPPA_SETTINGS' in dir(settings):
            print("Please define your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        zappa_settings = settings.ZAPPA_SETTINGS

        # Set your configuration
        project_name = settings.BASE_DIR.split(os.sep)[-1]
        api_stage = options['environment'][0]
        if api_stage not in zappa_settings.keys():
            print("Please make sure that the environment '" + api_stage + "' is defined in your ZAPPA_SETTINGS in your settings file before deploying.")
            return
        lambda_name = project_name + '-' + api_stage

        revision = options['revision'][0]

        # Make your Zappa object
        zappa = Zappa()
        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        print("Rolling back..")
        response = zappa.rollback_lambda_function_version(lambda_name, versions_back=revision)
        print("Done!")
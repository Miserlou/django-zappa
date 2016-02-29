from django.core.management.base import BaseCommand
from django_zappa.management.utils import load_zappa_settings
from zappa.zappa import Zappa


class Command(BaseCommand):
    can_import_settings = True
    requires_system_checks = False

    help = '''Rollback to specific version of a Zappa deploy.
              python manage.py rollback dev 3'''

    def add_arguments(self, parser):
        parser.add_argument('environment', type=str)
        parser.add_argument('revision', type=int)

    def handle(self, *args, **options):
        zappa_settings, project_name, api_stage = load_zappa_settings(options)
        lambda_name = project_name + '-' + api_stage

        revision = options['revision']

        # Make your Zappa object
        zappa = Zappa(options.get("session"))

        print("Rolling back..")
        zappa.rollback_lambda_function_version(lambda_name, versions_back=revision)
        print("Done!")

from __future__ import absolute_import

import base64
import json
import os

from django.core.management.base import BaseCommand
from zappa.zappa import Zappa


class Command(BaseCommand):
    can_import_settings = True
    requires_system_checks = False

    help = '''Invoke a management command in a remote Zappa environment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Execute the command.

        """

        if 'environment' not in options or len(options['environment']) < 2:
            print("You must call deploy with an environment name and command.\n"
                  "python manage.py invoke <environment> <command>")
            return

        from django.conf import settings
        if 'ZAPPA_SETTINGS' not in dir(settings):
            print("Please define your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        zappa_settings = settings.ZAPPA_SETTINGS

        # Set your configuration
        project_name = settings.BASE_DIR.split(os.sep)[-1]
        api_stage = options['environment'][0]
        if api_stage not in zappa_settings.keys():
            print("Please make sure that the environment '%s'"
                  " is defined in your ZAPPA_SETTINGS in your"
                  " settings file before deploying." % api_stage)
            return

        lambda_name = project_name + '-' + api_stage

        # Make your Zappa object
        zappa = Zappa()

        # Invoke it!
        command = {"command": ' '.join(options['environment'][1:])}
        response = zappa.invoke_lambda_function(lambda_name, json.dumps(command),
                                                invocation_type='RequestResponse')

        if 'LogResult' in response:
            print(base64.b64decode(response['LogResult']))
        else:
            print(response)
            import pdb
            pdb.set_trace()

        return

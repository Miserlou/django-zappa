from __future__ import absolute_import

from django.core.management.base import BaseCommand

import base64
import inspect
import json
import os
import sys
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

        if not options.has_key('environment') or len(options['environment']) < 2:
            print("You must call deploy with an environment name and command. \n python manage.py invoke <environment> <command>")
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

        # Make your Zappa object
        zappa = Zappa()

        # Invoke it!
        command = {"command": ' '.join(options['environment'][1:])}
        response = zappa.invoke_lambda_function(lambda_name, json.dumps(command), invocation_type='RequestResponse')

        if response.has_key('LogResult'):
            print(base64.b64decode(response['LogResult']))
        else:
            print(response)
            import pdb
            pdb.set_trace()

        return
from __future__ import absolute_import

import base64
import json
from django.core.management.base import BaseCommand
from django_zappa.management.utils import load_zappa_settings
from zappa.zappa import Zappa


class Command(BaseCommand):
    can_import_settings = True
    requires_system_checks = False

    help = '''Invoke a management command in a remote Zappa environment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', type=str)
        parser.add_argument('command', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Execute the command.

        """
        zappa_settings, project_name, api_stage = load_zappa_settings(options)
        lambda_name = project_name + '-' + api_stage
        # Make your Zappa object
        zappa = Zappa(options.get("session"))

        # Invoke it!
        command = {"command": ' '.join(options['command'])}
        response = zappa.invoke_lambda_function(
            lambda_name, json.dumps(command), invocation_type='RequestResponse')

        if 'LogResult' in response:
            print(base64.b64decode(response['LogResult']))
        else:
            print(response)
            import pdb
            pdb.set_trace()

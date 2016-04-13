from __future__ import absolute_import

import base64
import json

from zappa.zappa import Zappa

from .zappa_command import ZappaCommand


class Command(ZappaCommand):

    can_import_settings = True
    requires_system_checks = False

    help = '''Invoke a management command in a remote Zappa environment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Execute the command.

        """

        # Load the settings
        self.require_settings(args, options)

        # Load your AWS credentials from ~/.aws/credentials
        self.load_credentials()

        # Invoke it!
        command = {"command": ' '.join(options['environment'][1:])}

        response = self.zappa.invoke_lambda_function(
            self.lambda_name, json.dumps(command), invocation_type='RequestResponse')

        if 'LogResult' in response:
            print(base64.b64decode(response['LogResult']))
        else:
            print(response)
            import pdb
            pdb.set_trace()

        return

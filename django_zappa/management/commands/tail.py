from __future__ import absolute_import

from django.core.management.base import BaseCommand

import inspect
import os
import sys
import zipfile

from zappa.zappa import Zappa

class Command(BaseCommand):

    can_import_settings = True
    requires_system_checks = False

    help = '''Tail the logs of this Zappa deployment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def print_logs(self, logs):

        for log in logs:
            timestamp = log['timestamp']
            message = log['message']
            if "START RequestId" in message:
                continue
            if "REPORT RequestId" in message:
                continue
            if "END RequestId" in message:
                continue

            print("[" + str(timestamp) + "] " + message.strip())

    def handle(self, *args, **options):
        """
        Execute the command.

        """
        if not options.has_key('environment'):
            print("You must call deploy with an environment name. \n python manage.py deploy <environment>")
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

        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        try:
            # Tail the available logs
            all_logs = zappa.fetch_logs(lambda_name)
            self.print_logs(all_logs)

        # Keep polling, and print any new logs.
            while True:
                all_logs_again = zappa.fetch_logs(lambda_name)
                new_logs = []
                for log in all_logs_again:
                    if log not in all_logs:
                        new_logs.append(log)

                self.print_logs(new_logs)
                all_logs = all_logs + new_logs
        except KeyboardInterrupt:
            # Die gracefully
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

        return
from __future__ import absolute_import

import os
import sys

from django.core.management.base import BaseCommand
from django_zappa.management.utils import load_zappa_settings
from zappa.zappa import Zappa


class Command(BaseCommand):
    can_import_settings = True
    requires_system_checks = False

    help = '''Tail the logs of this Zappa deployment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', type=str)
        parser.add_argument(
            '--follow', '-f', action='store_true', default=False)

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

    def handle(self, *args, **options):  # NoQA
        """
        Execute the command.

        """
        zappa_settings, project_name, api_stage = load_zappa_settings(options)
        lambda_name = project_name + '-' + api_stage

        # Make your Zappa object
        zappa = Zappa(options.get("session"))

        try:
            # Tail the available logs
            all_logs = zappa.fetch_logs(lambda_name)
            self.print_logs(all_logs)

            # Keep polling, and print any new logs.
            while True and options['follow']:
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

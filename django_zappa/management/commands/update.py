from __future__ import absolute_import
from django.core.management.base import BaseCommand
import os
from zappa.zappa import Zappa
from .zappa_command import ZappaCommand


class Command(ZappaCommand):

    can_import_settings = True
    requires_system_checks = False

    help = '''Update the the lambda package for a given Zappa deployment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)
        parser.add_argument('--zip',
            dest='zip',
            default=None,
            help='Use a supplied zip file')
        parser.add_argument('--schedule',
            dest='schedule',
            action='store_true',
            default=False,
            help='Schedule Lambda Events'
        )
        parser.add_argument('--unschedule',
            dest='unschedule',
            action='store_true',
            default=False,
            help='UnSchedule(Remove) Lambda Events'
        )

    def handle(self, *args, **options):  # NoQA
        """
        Execute the command.

        """

        # Load the settings
        self.require_settings(args, options)

        # Load your AWS credentials from ~/.aws/credentials
        self.load_credentials()

        #Get the Django settings file
        self.get_django_settings_file()

        # Create the Lambda Zip,
        # or used the supplied zip file.
        if not options['zip']:
            self.create_package()
        else:
            self.zip_path = options['zip']

        # Upload it to S3
        self.zappa.upload_to_s3(self.zip_path, self.s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = self.zappa.update_lambda_function(
            self.s3_bucket_name, self.zip_path, self.lambda_name)

        # Remove the uploaded zip from S3, because it is now registered..
        self.zappa.remove_from_s3(self.zip_path, self.s3_bucket_name)

        # Finally, delete the local copy our zip package
        if self.zappa_settings[self.api_stage].get('delete_zip', True) and not options['zip']:
            os.remove(self.zip_path)

        #Remove the local settings
        self.remove_s3_local_settings()

        print("Your updated Zappa deployment is live!")

        events = self.zappa_settings[self.api_stage].get('events')

        iam = self.zappa.boto_session.resource('iam')
        self.zappa.credentials_arn = iam.Role(self.zappa.role_name).arn

        if options['unschedule'] and events:
            self.zappa.unschedule_events(lambda_arn, self.lambda_name, events)
        elif options['unschedule'] and not events:
            print("No Events to Unschedule")

        if options['schedule'] and events:
            self.zappa.schedule_events(lambda_arn, self.lambda_name, events)
        elif options['schedule'] and not events:
            print("No Events to Schedule")

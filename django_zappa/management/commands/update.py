from __future__ import absolute_import

from django.core.management.base import BaseCommand

import inspect
import os
import sys
import zipfile

from zappa.zappa import Zappa
from .zappa_command import ZappaCommand

class Command(ZappaCommand):

    can_import_settings = True
    requires_system_checks = False

    help = '''Deploy this project to AWS with Zappa.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Execute the command.

        """

        # Load the settings
        self.require_settings()

        custom_settings = [
            'http_methods', 
            'parameter_depth',
            'integration_response_codes',
            'method_response_codes',
            'role_name',
            'aws_region'
        ]
        for setting in custom_settings:
            if self.zappa_settings[self.api_stage].has_key(setting):
                setattr(zappa, setting, self.zappa_settings[self.api_stage][setting])

        # Load your AWS credentials from ~/.aws/credentials
        self.zappa.load_credentials()

        # Create the Lambda Zip
        self.create_package()

        # Upload it to S3
        zip_arn = self.zappa.upload_to_s3(zip_path, s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = self.zappa.update_lambda_function(s3_bucket_name, zip_path, lambda_name)

        print("Your updated Zappa deployment is live!")

        return
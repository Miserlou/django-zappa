from __future__ import absolute_import

from django.core.management.base import BaseCommand
from zappa.zappa import Zappa

from .zappa_command import ZappaCommand


class Command(ZappaCommand):

    can_import_settings = True
    requires_system_checks = False

    help = '''Update the the lambda package for a given Zappa deployment.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def handle(self, *args, **options):  # NoQA
        """
        Execute the command.

        """

        # Load the settings
        self.require_settings(args, options)

        # Load your AWS credentials from ~/.aws/credentials
        self.zappa.load_credentials()

        # Create the Lambda Zip
        self.create_package()

        # Upload it to S3
        self.zappa.upload_to_s3(self.zip_path, self.s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = self.zappa.update_lambda_function(
            self.s3_bucket_name, self.zip_path, self.lambda_name)

        # Remove the uploaded zip from S3, because it is now registered..
        self.zappa.remove_from_s3(self.zip_path, self.s3_bucket_name)

        print("Your updated Zappa deployment is live!")

        return

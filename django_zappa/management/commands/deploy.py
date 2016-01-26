from __future__ import absolute_import

from django.core.management.base import BaseCommand

import os
import sys
from zappa.zappa import Zappa

class Command(BaseCommand):

    can_import_settings = True
    help = '''Deploy this project to AWS with Zappa.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

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
        api_stage = options['environment']
        s3_bucket_name = 'lmbda'

        SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

        # Make your Zappa object
        zappa = Zappa()

        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        # Make sure the necessary IAM execution roles are available
        zappa.create_iam_roles()

        # Create the Lambda zip package (includes project and virtualenvironment)
        zip_path = zappa.create_lambda_zip(project_name)

        # Upload it to S3
        zip_arn = zappa.upload_to_s3(zip_path, s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = zappa.create_lambda_function(s3_bucket_name, zip_path, project_name, 'zappa.handler.lambda_handler')

        # Create and configure the API Gateway
        api_id = zappa.create_api_gateway_routes(lambda_arn)

        # Deploy the API!
        endpoint_url = zappa.deploy_api_gateway(api_id, api_stage)

        print("Your Zappa deployment is live!: " + endpoint_url)

        return
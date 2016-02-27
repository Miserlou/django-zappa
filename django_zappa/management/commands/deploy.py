from __future__ import absolute_import

from django.core.management.base import BaseCommand

import inspect
import os
import requests
import sys
import zipfile

from zappa.zappa import Zappa

class Command(BaseCommand):

    can_import_settings = True
    requires_system_checks = False

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
        api_stage = options['environment'][0]
        if api_stage not in zappa_settings.keys():
            print("Please make sure that the environment '" + api_stage + "' is defined in your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        # Make your Zappa object
        zappa = Zappa()

        custom_settings = [
            'http_methods', 
            'parameter_depth',
            'integration_response_codes',
            'method_response_codes',
            'role_name',
            'aws_region'
        ]
        for setting in custom_settings:
            if zappa_settings[api_stage].has_key(setting):
                setattr(zappa, setting, zappa_settings[api_stage][setting])

        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        # Make sure the necessary IAM execution roles are available
        zappa.create_iam_roles()

        # Create the Lambda Zip
        self.create_package()

        # Upload it to S3
        zip_arn = zappa.upload_to_s3(zip_path, s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = zappa.create_lambda_function(bucket=s3_bucket_name,
                                                  s3_key=zip_path,
                                                  function_name=lambda_name,
                                                  handler='handler.lambda_handler',
                                                  vpc_config=vpc_config,
                                                  memory_size=memory_size)

        # Create and configure the API Gateway
        api_id = zappa.create_api_gateway_routes(lambda_arn, lambda_name)

        # Deploy the API!
        endpoint_url = zappa.deploy_api_gateway(api_id, api_stage)

        # Finally, delete the local copy our zip package
        if zappa_settings[api_stage].get('delete_zip', True):
            os.remove(zip_path)

        # Remove the uploaded zip from S3, because it is now registered..
        zappa.remove_from_s3(zip_path, s3_bucket_name)

        if zappa_settings[api_stage].get('touch', True):
            requests.get(endpoint_url)

        print("Your Zappa deployment is live!: " + endpoint_url)

        return

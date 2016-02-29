from __future__ import absolute_import

import inspect
import os
import sys
import zipfile

import requests
from django.core.management.base import BaseCommand
from django_zappa.management.utils import load_zappa_settings
from zappa.zappa import Zappa


class Command(BaseCommand):
    can_import_settings = True
    requires_system_checks = False

    help = '''Deploy this project to AWS with Zappa.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', type=str)

    def handle(self, *args, **options):  # NoQA
        """
        Execute the command.

        """
        zappa_settings, project_name, api_stage = load_zappa_settings(options)
        zappa = Zappa(options.get("session"))

        # Load environment-specific settings
        s3_bucket_name = zappa_settings[api_stage]['s3_bucket']
        vpc_config = zappa_settings[api_stage].get('vpc_config', {})
        memory_size = zappa_settings[api_stage].get('memory_size', 512)
        settings_file = zappa_settings[api_stage]['settings_file']
        if '~' in settings_file:
            settings_file = settings_file.replace('~', os.path.expanduser('~'))
        if not os.path.isfile(settings_file):
            print("Please make sure your settings_file is properly defined.")
            sys.exit(1)

        custom_settings = [
            'http_methods',
            'parameter_depth',
            'integration_response_codes',
            'method_response_codes',
            'role_name',
            'aws_region'
        ]
        for setting in custom_settings:
            if setting in zappa_settings[api_stage]:
                setattr(zappa, setting, zappa_settings[api_stage][setting])

        # Make sure the necessary IAM execution roles are available
        zappa.create_iam_roles()

        # Create the Lambda zip package (includes project and virtualenvironment)
        # Also define the path the handler file so it can be copied to the zip root for Lambda.
        current_file = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        handler_file = os.sep.join(current_file.split(os.sep)[0:-2]) + os.sep + 'handler.py'
        lambda_name = project_name + '-' + api_stage
        zip_path = zappa.create_lambda_zip(lambda_name, handler_file=handler_file)

        # Add this environment's Django settings to that zipfile
        with open(settings_file, 'r') as f:
            contents = f.read()
            all_contents = contents
            if 'domain' not in zappa_settings[api_stage]:
                script_name = api_stage
            else:
                script_name = ''

            if "ZappaMiddleware" not in all_contents:
                print("\n\nWARNING!\n")
                print("You do not have ZappaMiddleware in your remote settings's MIDDLEWARE_CLASSES.\n")
                print("This means that some aspects of your application may not work!\n\n")

            all_contents = all_contents + '\n# Automatically added by Zappa:\nSCRIPT_NAME=\'/' + script_name + '\'\n'
            f.close()

        with open('zappa_settings.py', 'w') as f:
            f.write(all_contents)

        with zipfile.ZipFile(zip_path, 'a') as lambda_zip:
            lambda_zip.write('zappa_settings.py', 'zappa_settings.py')
            lambda_zip.close()

        os.unlink('zappa_settings.py')

        # Upload it to S3
        zappa.upload_to_s3(zip_path, s3_bucket_name)

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

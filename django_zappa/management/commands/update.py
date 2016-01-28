from __future__ import absolute_import

from django.core.management.base import BaseCommand


import inspect
import os
import sys
import zipfile

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
        api_stage = options['environment'][0]
        if api_stage not in zappa_settings.keys():
            print("Please make sure that the environment '" + api_stage + "' is defined in your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        # Make your Zappa object
        zappa = Zappa()

        # Load environment-specific settings
        s3_bucket_name = zappa_settings[api_stage]['s3_bucket']
        settings_file = zappa_settings[api_stage]['settings_file']
        if '~' in settings_file:
            settings_file = settings_file.replace('~', os.path.expanduser('~'))
        if not os.path.isfile(settings_file):
            print("Please make sure your settings_file is properly defined.")
            return

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
                setattr(zappa, zappa_settings[api_stage][setting])

        # Load your AWS credentials from ~/.aws/credentials
        zappa.load_credentials()

        # Make sure the necessary IAM execution roles are available
        zappa.create_iam_roles()

        # Create the Lambda zip package (includes project and virtualenvironment)
        # Also define the path the handler file so it can be copied to the zip root for Lambda.
        current_file =  os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        handler_file = os.sep.join(current_file.split(os.sep)[0:-2]) + os.sep + 'handler.py'
        lambda_name = project_name + '-' + api_stage
        zip_path = zappa.create_lambda_zip(lambda_name, handler_file=handler_file)

        # Add this environment's Django settings to that zipfile
        with zipfile.ZipFile(zip_path, 'a') as lambda_zip:
            lambda_zip.write(settings_file, 'zappa_settings.py')
            lambda_zip.close()

        # Upload it to S3
        zip_arn = zappa.upload_to_s3(zip_path, s3_bucket_name)

        # Register the Lambda function with that zip as the source
        # You'll also need to define the path to your lambda_handler code.
        lambda_arn = zappa.update_lambda_function(s3_bucket_name, zip_path, lambda_name)

        # Get the URL!
        endpoint_url = zappa.get_api_url(lambda_name)

        # Finally, delete the local copy our zip package
        os.remove(zip_path)

        print("Your updated Zappa deployment is live!")

        return
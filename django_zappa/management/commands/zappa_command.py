from __future__ import absolute_import

from django.core.management.base import BaseCommand

import inspect
import os
import sys
import zipfile

from zappa.zappa import Zappa

class ZappaCommand(BaseCommand):

    # Management command
    can_import_settings = True
    requires_system_checks = False
    
    # Zappa settings
    zappa = None
    zappa_settings = None
    api_stage = None
    project_name = None
    s3_bucket_name = None
    settings_file = None
    vpc_config = None
    memory_size = None

    help = '''Deploy this project to AWS with Zappa.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def __init__(self, *args, **kwargs):
        super(ZappaCommand, self).__init__(*args, **kwargs)
        self.zappa = Zappa()

    def require_settings(self, *args, **options):
        """
        Load the ZAPPA_SETTINGS as we expect it.

        """

        if not options.has_key('environment'):
            print("You must call deploy with an environment name. \n python manage.py deploy <environment>")
            return

        from django.conf import settings
        if not 'ZAPPA_SETTINGS' in dir(settings):
            print("Please define your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        self.zappa_settings = settings.ZAPPA_SETTINGS

        # Set your configuration
        self.project_name = settings.BASE_DIR.split(os.sep)[-1]
        self.api_stage = options['environment'][0]
        if self.api_stage not in self.zappa_settings.keys():
            print("Please make sure that the environment '" + self.api_stage + "' is defined in your ZAPPA_SETTINGS in your settings file before deploying.")
            return

        # Load environment-specific settings
        self.s3_bucket_name = zappa_settings[api_stage]['s3_bucket']
        self.vpc_config = zappa_settings[api_stage].get('vpc_config', {})
        self.memory_size = zappa_settings[api_stage].get('memory_size', 512)
        self.settings_file = zappa_settings[api_stage]['settings_file']
        if '~' in self.settings_file:
            self.settings_file = self.settings_file.replace('~', os.path.expanduser('~'))
        if not os.path.isfile(self.settings_file):
            print("Please make sure your settings_file is properly defined.")
            return

    def create_package(self):
        """
        Ensure that the package can be properly configured,
        and then create it.
        
        """

        # Create the Lambda zip package (includes project and virtualenvironment)
        # Also define the path the handler file so it can be copied to the zip root for Lambda.
        current_file =  os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        handler_file = os.sep.join(current_file.split(os.sep)[0:-2]) + os.sep + 'handler.py'
        lambda_name = project_name + '-' + api_stage
        zip_path = zappa.create_lambda_zip(lambda_name, handler_file=handler_file)

        # Add this environment's Django settings to that zipfile
        with open(settings_file, 'r') as f:
            contents = f.read()
            all_contents = contents
            if not zappa_settings[api_stage].has_key('domain'):
                script_name = api_stage
            else:
                script_name = ''

            if not "ZappaMiddleware" in all_contents:
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

    def remove_uploaded_zip(self):
        """
        Remove the local and S3 zip file after uploading and updating.
        """

        # Finally, delete the local copy our zip package
        if self.zappa_settings[self.api_stage].get('delete_zip', True):
            os.remove(zip_path)

        # Remove the uploaded zip from S3, because it is now registered..
        self.zappa.remove_from_s3(zip_path, s3_bucket_name)

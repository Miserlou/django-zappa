from __future__ import absolute_import

import boto3
import botocore
import inspect
import os
import zipfile

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.text import slugify

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
    lambda_name = None
    s3_bucket_name = None
    settings_file = None
    zip_path = None
    vpc_config = None
    memory_size = None
    timeout = None

    help = '''Deploy this project to AWS with Zappa.'''

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs='+', type=str)

    def __init__(self, *args, **kwargs):
        super(ZappaCommand, self).__init__(*args, **kwargs)
        self.zappa = Zappa()

    def require_settings(self, args, options):
        """
        Load the ZAPPA_SETTINGS as we expect it.

        """

        if not options.has_key('environment'):
            print(
                "You must call deploy with an environment name. \n python manage.py deploy <environment>")
            raise ImproperlyConfigured

        from django.conf import settings
        if not 'ZAPPA_SETTINGS' in dir(settings):
            print(
                "Please define your ZAPPA_SETTINGS in your settings file before deploying.")
            raise ImproperlyConfigured

        self.zappa_settings = settings.ZAPPA_SETTINGS

        # Set your configuration
        if type(options['environment']) == list:
            self.api_stage = options['environment'][0]
        else:
            self.api_stage = options['environment']
        if self.zappa_settings[self.api_stage].get('project_name'):
            self.project_name = self.zappa_settings[self.api_stage]['project_name']
        else:
            self.project_name = os.path.abspath(settings.BASE_DIR).split(os.sep)[-1]
        self.lambda_name = slugify(self.project_name + '-' + self.api_stage).replace("_","-")
        if self.api_stage not in self.zappa_settings.keys():
            print("Please make sure that the environment '" + self.api_stage +
                  "' is defined in your ZAPPA_SETTINGS in your settings file before deploying.")
            raise ImproperlyConfigured

        # Load environment-specific settings
        self.s3_bucket_name = self.zappa_settings[self.api_stage]['s3_bucket']
        self.vpc_config = self.zappa_settings[
            self.api_stage].get('vpc_config', {})
        self.memory_size = self.zappa_settings[
            self.api_stage].get('memory_size', 512)
        self.timeout = self.zappa_settings[
            self.api_stage].get('timeout', 30)


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
                setattr(self.zappa, setting, self.zappa_settings[
                        self.api_stage][setting])



    def get_django_settings_file(self):
        if not self.get_settings_location().startswith('s3://'):
            self.settings_file = self.zappa_settings[
            self.api_stage]['settings_file']
            if '~' in self.settings_file:
                self.settings_file = self.settings_file.replace(
                '~', os.path.expanduser('~'))
            self.check_settings_file()
        else:
            self.settings_file = self.download_from_s3(*self.parse_s3_url(self.get_settings_location()))
            self.check_settings_file()

    def check_settings_file(self):
        """
        Checks whether the settings file specified is actually a file.
        """
        if not os.path.isfile(self.settings_file):
            print("Please make sure your settings_file is properly defined.")
            raise ImproperlyConfigured

    def get_settings_location(self):
        """
        Returns the value of the settings file location as specified in the
        json file.
        :return:
        """
        return self.zappa_settings[self.api_stage]['settings_file']

    def download_from_s3(self,bucket_name,s3_key,
                     output_filename='temp_zappa_settings.py'):
        """
        Download a file from S3
        :param bucket_name: Name of the S3 bucket (string)
        :param s3_key: Name of the file hosted on S3 (string)
        :param output_filename: Name of the file the download operation
        will create (string)
        :return: False or the value of output_filename
        """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        try:
            s3.meta.client.head_object(Bucket=bucket_name,Key=s3_key)
        except botocore.exceptions.ClientError:
            return False
        print(u'Downloading the settings file ({0}) from S3'.format(s3_key))
        new_file = bucket.download_file(s3_key,output_filename)
        return output_filename

    def parse_s3_url(self,s3_url):
        """
        Parse the S3 url. Format: s3://mybucket:path/to/my/key
        Example: s3://settings-bucket:/production_settings.py
        :param s3_url: Path to the file hosted on S3
        :return:
        """
        return s3_url.replace('s3://','').split(':')


    def load_credentials(self):
        session = None
        profile_name = self.zappa_settings[self.api_stage].get('profile_name')
        region_name = self.zappa_settings[self.api_stage].get('aws_region')
        if profile_name is not None:
            session = boto3.Session(profile_name=profile_name, region_name=region_name)
        self.zappa.load_credentials(session)

    def create_package(self):
        """
        Ensure that the package can be properly configured,
        and then create it.

        """

        # Create the Lambda zip package (includes project and virtualenvironment)
        # Also define the path the handler file so it can be copied to the zip
        # root for Lambda.
        current_file = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        handler_file = os.sep.join(current_file.split(os.sep)[
                                   0:-2]) + os.sep + 'handler.py'
        exclude = self.zappa_settings[self.api_stage].get('exclude', []) + ['static', 'media']
        self.zip_path = self.zappa.create_lambda_zip(
                self.lambda_name,
                handler_file=handler_file,
                use_precompiled_packages=self.zappa_settings[self.api_stage].get('use_precompiled_packages', True),
                exclude=exclude
            )

        # Add this environment's Django settings to that zipfile
        with open(self.settings_file, 'r') as f:
            contents = f.read()
            all_contents = contents
            if not self.zappa_settings[self.api_stage].has_key('domain'):
                script_name = self.api_stage
            else:
                script_name = ''

            all_contents = all_contents + \
                '\n# Automatically added by Zappa:\nSCRIPT_NAME=\'/' + script_name + '\'\n'
            f.close()

        with open('zappa_settings.py', 'w') as f:
            f.write(all_contents)

        with zipfile.ZipFile(self.zip_path, 'a') as lambda_zip:
            lambda_zip.write('zappa_settings.py', 'zappa_settings.py')
            lambda_zip.close()

        os.unlink('zappa_settings.py')

    def remove_s3_local_settings(self):
        #Remove the settings file if downloaded from S3
        if self.get_settings_location().startswith('s3://'):
            os.remove(self.settings_file)

    def remove_local_zip(self):
        """
        Remove our local zip file.
        """

        if self.zappa_settings[self.api_stage].get('delete_zip', True):
            os.remove(self.zip_path)


    def remove_uploaded_zip(self):
        """
        Remove the local and S3 zip file after uploading and updating.
        """

        # Remove the uploaded zip from S3, because it is now registered..
        self.zappa.remove_from_s3(self.zip_path, self.s3_bucket_name)

        # Finally, delete the local copy our zip package
        self.remove_local_zip()

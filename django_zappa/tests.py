from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from .handler import lambda_handler
from .management.commands import (
    deploy, invoke, rollback, tail, update, zappa_command
)


class DjangoZappaTests(TestCase):
    ##
    # Sanity
    ##

    def test_basic_addition(self):
        """
        Test that 1 + 1 always equals 2.

        Sanity test.
        """
        self.assertEqual(1 + 1, 2)
    ##
    # Handler
    ##

    def test_basic_handler(self):

        event = {
            "body": "",
            "headers": {
                "Via": "1.1 e604e934e9195aaf3e36195adbcb3e18.cloudfront.net (CloudFront)",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip",
                "CloudFront-Is-SmartTV-Viewer": "false",
                "CloudFront-Forwarded-Proto": "https",
                "X-Forwarded-For": "109.81.209.118, 216.137.58.43",
                "CloudFront-Viewer-Country": "CZ",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "X-Forwarded-Proto": "https",
                "X-Amz-Cf-Id": "LZeP_TZxBgkDt56slNUr_H9CHu1Us5cqhmRSswOh1_3dEGpks5uW-g==",
                "CloudFront-Is-Tablet-Viewer": "false",
                "X-Forwarded-Port": "443",
                "CloudFront-Is-Mobile-Viewer": "false",
                "CloudFront-Is-Desktop-Viewer": "true",
            },
            "method": "GET",
            "params": {
            },
            "command": "check",
            "query": {
                "dead": "beef"
            }
        }

        try:
            lambda_handler(event, None)
        except Exception as e:
            print(e)
            self.assertTrue("PCFET0NUWVBFIGh" in str(e))

    ##
    # Commands
    ##

    def test_deploy_sanity(self):

        try:
            cmd = deploy.Command()
            opts = {}  # kwargs
            cmd.handle(**opts)
        except ImproperlyConfigured:
            return

    def test_update_sanity(self):

        try:
            cmd = update.Command()
            opts = {}  # kwargs
            cmd.handle(**opts)
        except ImproperlyConfigured:
            return

    def test_invoke_sanity(self):

        try:
            cmd = invoke.Command()
            opts = {}  # kwargs
            cmd.handle(**opts)
        except ImproperlyConfigured:
            return

    def test_tail_sanity(self):

        try:
            cmd = tail.Command()
            opts = {}  # kwargs
            cmd.handle(**opts)
        except ImproperlyConfigured:
            return

    def test_rollback_sanity(self):

        try:
            cmd = rollback.Command()
            opts = {}  # kwargs
            cmd.handle(**opts)
        except ImproperlyConfigured:
            return

    def test_parse_s3_url(self):
        cmd = zappa_command.ZappaCommand()
        options = {'environment': ['s3']}
        args = {}
        cmd.require_settings(args,options)
        s3_url = cmd.get_settings_location()
        self.assertEquals(s3_url,'s3://zappa-test-bucket:test_settings.py')
        self.assertEquals(cmd.parse_s3_url(s3_url),['zappa-test-bucket','test_settings.py'])

    def test_get_django_settings_file(self):
        cmd = zappa_command.ZappaCommand()

        args = {}
        options = {'environment': ['test']}
        cmd.require_settings(args, options)
        cmd.get_django_settings_file()
        self.assertEquals(cmd.settings_file,'test_settings.py')

    def test_check_settings_file(self):
        cmd = zappa_command.ZappaCommand()

        args = {}
        options = {'environment': ['test']}
        cmd.require_settings(args,options)
        with self.assertRaises(TypeError):
            cmd.check_settings_file()

        cmd.get_django_settings_file()
        self.assertEqual(None,cmd.check_settings_file())


    def test_zappa_command_sanity(self):

        cmd = zappa_command.ZappaCommand()

        args = {}
        options = {'environment': ['test']}
        cmd.require_settings(args, options)
        cmd.get_django_settings_file()
        cmd.create_package()
        cmd.remove_local_zip()

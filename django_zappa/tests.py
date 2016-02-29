import sys
from StringIO import StringIO
from django.test import TestCase
from .handler import lambda_handler
from django.core.management import call_command
from placebo.utils import placebo_session


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
            self.assertTrue("PCFET0NUWVBFIGh" in str(e))

    def test_lets_encrypt_event(self):

        challenge_path = 'KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz'
        challenge_content = "KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz.ABC5hET2fxMsBLCsQLlAVA5MLvYUna8gEAYaXN0xI4Y"

        yay_event = {
            "body": {},
            "headers": {
                "Via": "1.1 e604e934e9195aaf3e36195adbcb3e18.cloudfront.net (CloudFront)",
            },
            "params": {
                "parameter_1": ".well-known",
                "parameter_2": "acme-challenge",
                "parameter_3": challenge_path
            },
            "method": "GET",
            "query": {
            }
        }

        try:
            lambda_handler(yay_event, None, "test_settings")
        except Exception as e:
            self.assertTrue(challenge_content in str(e))

        boo_event = {
            "body": {},
            "headers": {
                "Via": "1.1 e604e934e9195aaf3e36195adbcb3e18.cloudfront.net (CloudFront)",
            },
            "params": {
                "parameter_1": ".well-known",
                "parameter_2": "acme-challenge",
                "parameter_3": "barf-derp-fart"
            },
            "method": "GET",
            "query": {
            }
        }

        try:
            lambda_handler(boo_event, None, "test_settings")
        except Exception as e:
            self.assertTrue(challenge_content not in str(e))

    ##
    # Commands
    ##
    @placebo_session
    def test_deploy(self, session):
        args = ["test"]
        opts = {'session': session}
        out = StringIO()
        stdout_backup, sys.stdout = sys.stdout, out
        call_command('deploy', *args, **opts)
        sys.stdout = stdout_backup
        self.assertIn(
            "Your Zappa deployment is live!: "
            "https://oakuumaiog.execute-api.us-east-1.amazonaws.com/test",
            out.getvalue()
        )

    @placebo_session
    def test_update(self, session):
        args = ["test"]
        opts = {'session': session}
        out = StringIO()
        stdout_backup, sys.stdout = sys.stdout, out
        call_command('update', *args, **opts)
        sys.stdout = stdout_backup
        self.assertIn(
            "Your updated Zappa deployment is live!",
            out.getvalue()
        )

    def test_invoke(self, session):
        args = ["test", "check this out"]
        opts = {'session': session}
        call_command('invoke', *args, **opts)

    def test_tail(self, session):
        args = ["test"]
        opts = {'session': session}
        call_command('tail', *args, **opts)

    def test_rollback(self, session):
        args = ["test", "1"]
        opts = {'session': session}
        call_command('rollback', *args, **opts)

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.shortcuts import render
from django.db import models
from django.test import TestCase, Client

import os

from .handler import lambda_handler
from .middleware import ZappaMiddleware
from .management.commands import deploy, invoke, update, tail

class DjangoZappaTests(TestCase):

    ##
    # Sanity
    ##
    
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2. (Sanity test.)
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
            returned = lambda_handler(event, None)
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
            returned = lambda_handler(yay_event, None, "test_settings")
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
            returned = lambda_handler(boo_event, None, "test_settings")
        except Exception as e:
            self.assertTrue(challenge_content not in str(e))

    ##
    # Commands
    ##

    def test_deploy_sanity(self):
        
        cmd = deploy.Command()
        opts = {} # kwargs
        cmd.handle(**opts)

    def test_update_sanity(self):
        
        cmd = update.Command()
        opts = {} # kwargs
        cmd.handle(**opts)

    def test_invoke_sanity(self):
        
        cmd = invoke.Command()
        opts = {} # kwargs
        cmd.handle(**opts)

    def test_tail_sanity(self):
        
        cmd = tail.Command()
        opts = {} # kwargs
        cmd.handle(**opts)

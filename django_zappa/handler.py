from __future__ import unicode_literals

import base64
import json
import mimetypes
import os
import re
import sys
import zipfile

from copy import copy
from importlib import import_module
from io import BytesIO

from django.apps import apps
from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIHandler
from django.core.handlers.wsgi import ISO_8859_1, UTF_8, WSGIRequest
from django.core.signals import (
    got_request_exception, request_finished, request_started,
)
from django.db import close_old_connections

from zappa.wsgi import create_wsgi_request

def lambda_handler(event, context):
    """
    An AWS Lambda function which parses specific API Gateway input into a WSGI request,
    feeds it to Django, procceses the Django response, and returns that 
    back to the API Gateway.

    """    

    # Django requires settings and an explicit call to setup()
    # if being used from inside a python context.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zappa_settings")
    import django
    django.setup()
    from django.conf import settings

    # This is a normal HTTP request
    if event.get('method', None):

        # If we just want to inspect this,
        # return this event instead of processing the request
        # https://your_api.aws-api.com/?event_echo=true
        event_echo = getattr(settings, "EVENT_ECHO", True)
        if event_echo:
            if 'event_echo' in event['params'].values():
                return {'Content': str(event) + '\n' + str(context), 'Status': 200}

        # This doesn't matter, but Django's handler requires it.
        def start(a, b):
            return

        # Create the environment for WSGI and handle the request
        environ = create_wsgi_request(event, script_name=settings.SCRIPT_NAME)
        handler = WSGIHandler()
        response = handler(environ, start)

        # Prepare the special dictionary which will be returned to the API GW.
        returnme = {'Content': response.content}

        # Pack the WSGI response into our special dictionary.
        for item in response.items():
            returnme[item[0]] = item[1]
        returnme['Status'] = response.status_code

        # Parse the WSGI Cookie and pack it.
        cookie = response.cookies.output()
        if ': ' in cookie:
            returnme['Set-Cookie'] = response.cookies.output().split(': ')[1]

        # To ensure correct status codes, we need to
        # pack the response as a deterministic B64 string and raise it
        # as an error to match our APIGW regex.
        # The DOCTYPE ensures that the page still renders in the browser.
        if response.status_code in [400, 401, 403, 500]:
            content = response.content
            content = "<!DOCTYPE html>" + str(response.status_code) + response.content
            b64_content = base64.b64encode(content)
            raise Exception(b64_content)
        # Internal are changed to become relative redirects
        # so they still work for apps on raw APIGW and on a domain.
        elif response.status_code in [301, 302]:
            location = returnme['Location']
            location = '/' + location.replace("http://zappa/", "")
            raise Exception(location)
        else:
            return returnme

    # This is a management command invocation.
    elif event.get('command', None):
        from django.core import management

        # Couldn't figure out how to get the value into stdout with StringIO..
        # Read the log for now. :[]
        management.call_command(*event['command'].split(' '))
        return {}

if __name__ == "__main__":
    event = {
        "body": "hello=there",
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
            "Content-Type": "application/x-www-form-urlencoded"
        },
        "method": "POST",
        "params": {
            "a_path": "post_echo",
        },
        "command": "check",
        "query": { 
            "dead": "beef" 
        }
    }

    print lambda_handler(event, None)

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
from django.core.handlers.wsgi import ISO_8859_1, UTF_8, WSGIRequest
from django.core.signals import (
    got_request_exception, request_finished, request_started,
)
from django.db import close_old_connections

from zappa.wsgi import create_wsgi_request

class LambdaHandler(BaseHandler):
    """
    A HTTP Handler that can be used for testing purposes. Uses the WSGI
    interface to compose requests, but returns the raw HttpResponse object with
    the originating WSGIRequest attached to its ``wsgi_request`` attribute.
    """
    def __init__(self, enforce_csrf_checks=True, *args, **kwargs):
        self.enforce_csrf_checks = enforce_csrf_checks
        super(LambdaHandler, self).__init__(*args, **kwargs)

    def __call__(self, environ):
        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._request_middleware is None:
            self.load_middleware()

        request_started.disconnect(close_old_connections)
        request_started.send(sender=self.__class__, environ=environ)
        request_started.connect(close_old_connections)
        request = WSGIRequest(environ)
        # sneaky little hack so that we can easily get round
        # CsrfViewMiddleware.  This makes life easier, and is probably
        # required for backwards compatibility with external tests against
        # admin views.
        request._dont_enforce_csrf_checks = not self.enforce_csrf_checks

        # Request goes through middleware.
        response = self.get_response(request)
        # Attach the originating request to the response so that it could be
        # later retrieved.
        response.wsgi_request = request

        # We're emulating a WSGI server; we must call the close method
        # on completion.
        if response.streaming:
            response.streaming_content = closing_iterator_wrapper(
                response.streaming_content, response.close)
        else:
            request_finished.disconnect(close_old_connections)
            response.close()                    # will fire request_finished
            request_finished.connect(close_old_connections)

        return response

def lambda_handler(event, context):    

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zappa_settings")
    import django
    django.setup()

    # This is a normal HTTP request
    if event.get('method', None):
        handler = LambdaHandler()
        environ = create_wsgi_request(event)
        response = handler(environ)
        returnme = {'Content': response.content}
        for item in response.items():
            returnme[item[0]] = item[1]
        returnme['Status'] = response.status_code

        if response.status_code != 200:

            # So that we can always match on the first few characters
            # ex '{"AAA": "404'
            # returnme['AAA'] = str(response.status_code)
            # returnme['errorMessage'] = str(response.status_code)
            # returnme['errorType'] = str(response.status_code)
            # returnme['stackTrace'] = str(response.status_code)

            # error_json = json.dumps(returnme, sort_keys=True)
            # print "Error JSON:"
            # print error_json

            content = response.content
            content = "<!DOCTYPE html>" + str(response.status_code) + response.content

            b64_content = base64.b64encode(content)
            print b64_content

            raise Exception(b64_content)

        print returnme

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
        "body": {},
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
            "CloudFront-Is-Desktop-Viewer": "true"
        },
        "params": {
            "a_path": "asdf1",
            "b_path": "asdf2",
        },
        "command": "check",
        "query": { 
            "dead": "beef" 
        }
    }

    print lambda_handler(event, None)

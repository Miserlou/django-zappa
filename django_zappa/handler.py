# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import datetime
import logging
import os

from django.core.handlers.wsgi import WSGIHandler
from zappa.wsgi import common_log, create_wsgi_request

# Django requires settings and an explicit call to setup()
# if being used from inside a python context.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zappa_settings")
import django
django.setup()
from django.conf import settings

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ERROR_CODES = [400, 401, 403, 404, 500]


def start(a, b):
    """
    This doesn't matter, but Django's handler requires it.
    """
    return


def lambda_handler(event, context, settings_name="zappa_settings"):  # NoQA
    """
    An AWS Lambda function which parses specific API Gateway input into a WSGI request.

    The request get fed it to Django, processes the Django response, and returns that
    back to the API Gateway.
    """
    time_start = datetime.datetime.now()

    # If in DEBUG mode, log all raw incoming events.
    if settings.DEBUG:
        logger.info('Zappa Event: {}'.format(event))

    # This is a normal HTTP request
    if event.get('method', None):

        # If we just want to inspect this,
        # return this event instead of processing the request
        # https://your_api.aws-api.com/?event_echo=true
        event_echo = getattr(settings, "EVENT_ECHO", True)
        if event_echo:
            if 'event_echo' in event['params'].values():
                return {'Content': str(event) + '\n' + str(context), 'Status': 200}

        # If Let's Encrypt is defined in the settings,
        # and the path is your.domain.com/.well-known/acme-challenge/{{lets_encrypt_challenge_content}},
        # return a 200 of lets_encrypt_challenge_content.
        lets_encrypt_challenge_path = getattr(settings, "LETS_ENCRYPT_CHALLENGE_PATH", None)
        lets_encrypt_challenge_content = getattr(settings, "LETS_ENCRYPT_CHALLENGE_CONTENT", None)
        if lets_encrypt_challenge_path:
            if len(event['params']) == 3:
                if event['params']['parameter_1'] == '.well-known' and \
                                event['params']['parameter_2'] == 'acme-challenge' and \
                                event['params']['parameter_3'] == lets_encrypt_challenge_path:
                    return {'Content': lets_encrypt_challenge_content, 'Status': 200}

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
        exception = None
        if response.status_code in ERROR_CODES:
            content = response.content
            content = u"<!DOCTYPE html>" + unicode(response.status_code) + unicode('<meta charset="utf-8" />') + response.content.encode('utf-8')
            b64_content = base64.b64encode(content)
            exception = (b64_content)
        # Internal are changed to become relative redirects
        # so they still work for apps on raw APIGW and on a domain.
        elif 300 <= response.status_code < 400 and response.has_header('Location'):
            location = returnme['Location']
            location = '/' + location.replace("http://zappa/", "")
            exception = location

        # Calculate the total response time,
        # and log it in the Common Log format.
        time_end = datetime.datetime.now()
        delta = time_end - time_start
        response_time_ms = delta.total_seconds() * 1000
        common_log(environ, response, response_time=response_time_ms)

        # Finally, return the response to API Gateway.
        if exception:
            raise Exception(exception)
        else:
            return returnme

    # This is a management command invocation.
    elif event.get('command', None):
        from django.core import management

        # Couldn't figure out how to get the value into stdout with StringIO..
        # Read the log for now. :[]
        management.call_command(*event['command'].split(' '))
        return {}

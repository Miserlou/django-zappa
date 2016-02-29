import os
import sys
from django.conf import settings


def load_zappa_settings(options):
    if 'ZAPPA_SETTINGS' not in dir(settings):
        print("Please define your ZAPPA_SETTINGS in your settings file before deploying.")
        sys.exit(1)

    zappa_settings = settings.ZAPPA_SETTINGS

    # Set your configuration
    project_name = settings.BASE_DIR.split(os.sep)[-1]
    api_stage = options['environment']
    if api_stage not in zappa_settings:
        print("Please make sure that the environment '%s'"
              " is defined in your ZAPPA_SETTINGS in your"
              " settings file before deploying." % api_stage)
        sys.exit(1)
    return zappa_settings, project_name, api_stage
